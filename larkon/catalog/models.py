import datetime
from zoneinfo import ZoneInfo
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class Brand(models.Model):
    """Marca multimarcas parceira da Vakaria."""
    name = models.CharField(_("Nome da Marca"), max_length=150, unique=True)
    slug = models.SlugField(_("Slug"), max_length=160, unique=True, blank=True)
    logo = models.ImageField(_("Logo"), upload_to="brands/", blank=True, null=True)
    description = models.TextField(_("Descrição / Estilo"), blank=True)
    website = models.URLField(_("Site / Redes"), blank=True)
    is_active = models.BooleanField(_("Ativa"), default=True)
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)

    class Meta:
        verbose_name = _("Marca")
        verbose_name_plural = _("Marcas")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    """Categoria de produtos (Feminino, Masculino, Acessórios, etc.)."""
    GENDER_CHOICES = [
        ("F", _("Feminino")),
        ("M", _("Masculino")),
        ("U", _("Unissex")),
    ]

    name = models.CharField(_("Nome da Categoria"), max_length=100)
    slug = models.SlugField(_("Slug"), max_length=120, unique=True, blank=True)
    gender_target = models.CharField(_("Público-Alvo"), max_length=1, choices=GENDER_CHOICES, default="U")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Categoria Pai"),
    )
    icon = models.CharField(_("Ícone (Classe CSS/Solar)"), max_length=50, blank=True, default="solar:t-shirt-bold-duotone")
    is_active = models.BooleanField(_("Ativa"), default=True)
    order = models.PositiveIntegerField(_("Ordem de Exibição"), default=0)

    class Meta:
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")
        ordering = ["order", "name"]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name} ({self.get_gender_target_display()})"
        return f"{self.name} ({self.get_gender_target_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.name}-{self.gender_target}")
            self.slug = base_slug
        super().save(*args, **kwargs)


class Drop(models.Model):
    """Lançamentos de Coleções e Novidades Bi-semanais da Vakaria."""
    title = models.CharField(_("Título do Drop"), max_length=150)
    slug = models.SlugField(_("Slug"), max_length=160, unique=True, blank=True)
    edition = models.CharField(_("Edição / Código"), max_length=50, blank=True, help_text=_("Ex: DROP-2026-W36-01"))
    launch_date = models.DateField(_("Data de Lançamento"))
    banner = models.ImageField(_("Banner Promocional"), upload_to="drops/", blank=True, null=True)
    description = models.TextField(_("Conceito & Curadoria"), blank=True)
    is_featured = models.BooleanField(_("Destaque na Home"), default=False)
    is_active = models.BooleanField(_("Ativo"), default=True)
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)

    class Meta:
        verbose_name = _("Drop Semanal")
        verbose_name_plural = _("Drops Semanais")
        ordering = ["-launch_date"]

    def __str__(self):
        return f"{self.title} ({self.launch_date.strftime('%d/%m/%Y')})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Peça de moda do catálogo Vakaria."""
    GENDER_CHOICES = [
        ("F", _("Feminino")),
        ("M", _("Masculino")),
        ("U", _("Unissex")),
    ]

    title = models.CharField(_("Nome da Peça"), max_length=200)
    slug = models.SlugField(_("Slug"), max_length=220, unique=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products", verbose_name=_("Marca"))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name=_("Categoria"))
    drop = models.ForeignKey(Drop, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name=_("Drop da Semana"))
    gender = models.CharField(_("Gênero"), max_length=1, choices=GENDER_CHOICES, default="F")

    price = models.DecimalField(_("Preço de Venda (R$)"), max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(_("Preço Original / De (R$)"), max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(_("Preço de Custo (R$)"), max_digits=10, decimal_places=2, null=True, blank=True)

    description = models.TextField(_("Descrição da Peça"), blank=True)
    fabric_composition = models.CharField(_("Composição do Tecido"), max_length=255, blank=True, help_text=_("Ex: 100% Algodão Pima / Linho Puro"))
    care_instructions = models.TextField(_("Instruções de Lavagem"), blank=True)

    is_exclusive = models.BooleanField(_("Peça Exclusiva / Limitada"), default=True)
    is_featured = models.BooleanField(_("Destaque"), default=False)
    is_active = models.BooleanField(_("Ativo no Catálogo"), default=True)

    views_count = models.PositiveIntegerField(_("Visualizações"), default=0)
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Produto")
        verbose_name_plural = _("Produtos")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.brand.name} (R$ {self.price})"

    @property
    def cover_image(self):
        cover = self.images.filter(is_cover=True).first()
        if not cover:
            cover = self.images.first()
        return cover

    @property
    def total_stock(self):
        return sum(variant.stock_quantity for variant in self.variants.all())

    @property
    def in_stock(self):
        return self.total_stock > 0

    @property
    def secondary_image(self):
        """Segunda imagem para efeito de hover nos cards."""
        imgs = list(self.images.all())
        if len(imgs) > 1:
            return imgs[1]
        return None

    @property
    def available_colors(self):
        """Retorna lista de cores únicas disponíveis com nome e HEX."""
        colors = []
        seen = set()
        for v in self.variants.all():
            if v.color and v.color not in seen:
                seen.add(v.color)
                colors.append({
                    "name": v.color,
                    "hex": v.color_hex or "#0f172a",
                })
        return colors

    @property
    def variants_matrix(self):
        """Retorna a matriz de variantes agrupada por cor com foto, tamanhos e estoque."""
        variants = list(self.variants.all())
        images = list(self.images.all())

        colors_map = {}
        for v in variants:
            col_name = v.color or "Padrão"
            if col_name not in colors_map:
                col_img = next((img.url for img in images if img.color and img.color.strip().lower() == col_name.strip().lower()), None)
                if not col_img:
                    col_img = self.cover_image.url if self.cover_image else "/static/images/products/product-placeholder.png"

                colors_map[col_name] = {
                    "name": col_name,
                    "hex": v.color_hex or "#0f172a",
                    "image_url": col_img,
                    "sizes": []
                }
            colors_map[col_name]["sizes"].append({
                "size": v.size,
                "stock": v.stock_quantity,
                "in_stock": v.stock_quantity > 0,
                "variant_id": v.id,
            })

        return list(colors_map.values())

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.brand.name}")
        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """Variação de tamanho, cor e estoque da peça."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants", verbose_name=_("Produto"))
    size = models.CharField(_("Tamanho"), max_length=30, help_text=_("Ex: PP, P, M, G, GG, 38, 40, 42, etc."))
    color = models.CharField(_("Cor / Estampa"), max_length=50, blank=True)
    color_hex = models.CharField(_("Cor HEX"), max_length=10, blank=True, help_text=_("Ex: #000000, #F5F5DC"))
    sku = models.CharField(_("SKU / Código"), max_length=60, unique=True, blank=True)
    stock_quantity = models.PositiveIntegerField(_("Quantidade em Estoque"), default=1)
    additional_price = models.DecimalField(_("Acréscimo de Preço (R$)"), max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _("Variação de Produto")
        verbose_name_plural = _("Variações de Produtos")
        unique_together = ("product", "size", "color")

    def __str__(self):
        return f"{self.product.title} - Tam: {self.size} / Cor: {self.color or 'Padrão'} (Qtd: {self.stock_quantity})"

    @property
    def final_price(self):
        return self.product.price + self.additional_price

    def save(self, *args, **kwargs):
        if not self.sku:
            prod_slug = self.product.slug if hasattr(self, 'product') and self.product else "prod"
            base_sku = f"{prod_slug}-{slugify(self.color or 'padrao')}-{slugify(self.size)}"
            candidate = base_sku[:50]
            counter = 1
            while ProductVariant.objects.filter(sku=candidate).exclude(pk=self.pk).exists():
                candidate = f"{base_sku[:44]}-{counter}"
                counter += 1
            self.sku = candidate
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Galeria de imagens da peça."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name=_("Produto"))
    image = models.ImageField(_("Arquivo de Imagem"), upload_to="products/", blank=True, null=True)
    image_url = models.URLField(_("URL Externa (CDN/Cloud)"), blank=True, null=True)
    color = models.CharField(_("Cor / Variação Vinculada"), max_length=50, blank=True, help_text=_("Cor associada a esta foto (opcional)"))
    alt_text = models.CharField(_("Texto Alternativo (Acessibilidade/SEO)"), max_length=200, blank=True)
    order = models.PositiveIntegerField(_("Ordem"), default=0)
    is_cover = models.BooleanField(_("Foto de Capa Principal"), default=False)

    class Meta:
        verbose_name = _("Imagem do Produto")
        verbose_name_plural = _("Imagens do Produto")
        ordering = ["order", "id"]

    def __str__(self):
        return f"Foto #{self.id} de {self.product.title}"

    @property
    def url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "/static/images/products/product-placeholder.png"


class StockMovement(models.Model):
    """Histórico e Auditoria de Entradas e Saídas do Estoque."""
    MOVEMENT_TYPES = [
        ("IN", _("Entrada (+)")),
        ("OUT", _("Saída (-)")),
        ("ADJUST", _("Ajuste de Saldo (=)")),
    ]

    REASON_CHOICES = [
        # Entradas
        ("purchase", _("Compra / Reposição de Fornecedor")),
        ("return_customer", _("Devolução de Cliente")),
        ("drop_launch", _("Novo Drop / Lançamento")),
        ("initial_stock", _("Saldo Inicial / Cadastro")),
        
        # Saídas
        ("sale", _("Venda")),
        ("showroom", _("Mostruário / Provador / Fotos")),
        ("damaged", _("Avaria / Defeito")),
        ("loss", _("Perda / Extravio")),
        ("gift_pr", _("Brinde / Parceria / Influenciador")),
        ("return_supplier", _("Devolução para Fornecedor")),
        
        # Ajustes
        ("inventory_audit", _("Ajuste de Balanço / Inventário")),
        ("other", _("Outro Motivo")),
    ]

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="stock_movements",
        verbose_name=_("Variante do Produto")
    )
    movement_type = models.CharField(_("Tipo de Movimento"), max_length=10, choices=MOVEMENT_TYPES)
    reason = models.CharField(_("Motivo"), max_length=30, choices=REASON_CHOICES, default="purchase")
    quantity = models.IntegerField(_("Quantidade Movimentada"))
    
    previous_stock = models.IntegerField(_("Estoque Anterior"), default=0)
    new_stock = models.IntegerField(_("Novo Estoque"), default=0)
    
    cost_price = models.DecimalField(_("Custo Unitário (R$)"), max_digits=10, decimal_places=2, null=True, blank=True)
    invoice_number = models.CharField(_("Nota Fiscal / Pedido / Doc"), max_length=100, blank=True)
    notes = models.TextField(_("Observações"), blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
        verbose_name=_("Registrado por")
    )
    created_at = models.DateTimeField(_("Data da Movimentação"), default=timezone.now)

    class Meta:
        verbose_name = _("Movimentação de Estoque")
        verbose_name_plural = _("Movimentações de Estoque")
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_movement_type_display()}] {self.variant.product.title} ({self.variant.size}/{self.variant.color or 'Padrão'}) - Qtd: {self.quantity}"


class CarouselSlide(models.Model):
    """Banners e slides de carrossel dinâmicos da Vakaria."""
    SLIDE_TYPES = [
        ("hero", _("Hero Principal (Topo da Home)")),
        ("drops", _("Drops & Novidades da Semana")),
        ("promo", _("Banner Promocional")),
    ]

    title = models.CharField(_("Título do Slide"), max_length=200)
    subtitle = models.TextField(_("Subtítulo / Descrição"), blank=True)
    badge_text = models.CharField(_("Texto da Tag / Badge"), max_length=100, blank=True, help_text=_("Ex: ✨ Drop Feminino Ativo"))
    
    image = models.ImageField(_("Imagem do Banner"), upload_to="carousels/", blank=True, null=True)
    image_url = models.URLField(_("URL da Imagem (Opcional / CDN)"), blank=True)
    image_mobile = models.ImageField(_("Imagem Mobile (Opcional - Vertical)"), upload_to="carousels/mobile/", blank=True, null=True)
    image_mobile_url = models.URLField(_("URL da Imagem Mobile (Opcional / CDN)"), blank=True)
    
    button_text = models.CharField(_("Texto do Botão"), max_length=60, default="Explorar Coleção")
    button_url = models.CharField(_("Link de Destino"), max_length=255, default="/produtos/")
    
    overlay_darkness = models.CharField(
        _("Filtro de Contraste da Foto"),
        max_length=20,
        choices=[
            ("light", _("Leve (25%)")),
            ("medium", _("Médio (45% - Recomendado)")),
            ("dark", _("Intenso (70%)")),
        ],
        default="medium"
    )
    text_alignment = models.CharField(
        _("Alinhamento do Texto"),
        max_length=20,
        choices=[
            ("left", _("Alinhado à Esquerda")),
            ("center", _("Centralizado")),
            ("right", _("Alinhado à Direita")),
        ],
        default="left"
    )
    button_style = models.CharField(
        _("Estilo Visual do Botão"),
        max_length=20,
        choices=[
            ("gold", _("Dourado Luxo (Padrão Vakaria)")),
            ("dark", _("Preto Minimalista")),
            ("whatsapp", _("Verde WhatsApp")),
            ("outline", _("Borda Branca")),
        ],
        default="gold"
    )
    
    slide_type = models.CharField(_("Posição / Tipo"), max_length=20, choices=SLIDE_TYPES, default="hero")
    order = models.PositiveIntegerField(_("Ordem de Exibição"), default=0)
    is_active = models.BooleanField(_("Ativo no Site"), default=True)
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Slide do Carrossel")
        verbose_name_plural = _("Slides dos Carrosséis")
        ordering = ["slide_type", "order", "-created_at"]

    def __str__(self):
        return f"[{self.get_slide_type_display()}] {self.title} (Ordem: {self.order})"

    @property
    def final_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "/static/images/hero_feminina.jpg"

    @property
    def final_mobile_image_url(self):
        if self.image_mobile:
            return self.image_mobile.url
        if self.image_mobile_url:
            return self.image_mobile_url
        return self.final_image_url


class CustomerReview(models.Model):
    """Depoimentos e avaliações de clientes exibidos na página inicial (Prova Social)."""
    SOURCE_CHOICES = [
        ("instagram", _("Instagram Direct / Story")),
        ("google", _("Google Reviews (5.0 ★)")),
        ("whatsapp", _("WhatsApp & Atendimento")),
        ("vip", _("Cliente VIP / Provador")),
        ("direct", _("Direct / Mensagem Privada")),
        ("loja", _("Loja Física (Cajazeiras - PB)")),
        ("outro", _("Cliente Verificado / Indicação")),
    ]

    name = models.CharField(_("Nome do Cliente"), max_length=120)
    location = models.CharField(_("Cidade / Localização"), max_length=120, blank=True, default="Cajazeiras - PB")
    rating = models.PositiveSmallIntegerField(_("Avaliação (Estrelas)"), default=5)
    comment = models.TextField(_("Depoimento / Comentário"))
    source = models.CharField(_("Origem / Selo"), max_length=20, choices=SOURCE_CHOICES, default="google")
    
    avatar = models.ImageField(_("Foto / Avatar"), upload_to="reviews/", blank=True, null=True)
    avatar_url = models.URLField(_("URL da Foto (Opcional)"), blank=True)
    
    order = models.PositiveIntegerField(_("Ordem de Exibição"), default=0)
    is_active = models.BooleanField(_("Ativo no Site"), default=True)
    created_at = models.DateTimeField(_("Data do Depoimento"), auto_now_add=True)

    class Meta:
        verbose_name = _("Depoimento de Cliente")
        verbose_name_plural = _("Depoimentos de Clientes")
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.rating}★ - {self.get_source_display()})"

    @property
    def final_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        if self.avatar_url:
            return self.avatar_url
        return None

    @property
    def initial_letter(self):
        return self.name[:1].upper() if self.name else "G"


class LinktreeItem(models.Model):
    """Links rápidos das páginas públicas do Linktree oficial (Vakaria /links e Luiza Fit /tree)."""
    PAGE_CHOICES = [
        ("vakaria", _("Vakaria Barbearia (/links)")),
        ("luiza_fit", _("Luiza Fit Moda Fitness (/tree)")),
    ]

    page_type = models.CharField(_("Página de Destino"), max_length=20, choices=PAGE_CHOICES, default="vakaria")
    title = models.CharField(_("Título do Botão"), max_length=120)
    subtitle = models.CharField(_("Subtítulo / Descrição Rápida"), max_length=200, blank=True)
    url = models.CharField(_("Link de Redirecionamento"), max_length=500)
    icon = models.CharField(_("Ícone Boxicons"), max_length=50, default="bx bx-link-external", help_text=_("Ex: bx bxl-whatsapp, bx bx-store-alt, bx bxl-instagram"))
    style = models.CharField(_("Estilo do Botão"), max_length=30, default="outline", help_text=_("primary, success, dark, gold, rose, champagne, outline"))
    is_highlighted = models.BooleanField(_("Botão em Destaque (Pulsar)"), default=False)
    order = models.PositiveIntegerField(_("Ordem"), default=0)
    clicks_count = models.PositiveIntegerField(_("Cliques Registrados"), default=0)
    is_active = models.BooleanField(_("Ativo na Página"), default=True)
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)

    class Meta:
        verbose_name = _("Item do Linktree")
        verbose_name_plural = _("Itens do Linktree")
        ordering = ["page_type", "order", "id"]

    def __str__(self):
        return f"[{self.get_page_type_display()}] {self.title}"


class HomePageConfig(models.Model):
    """Configurações centralizadas de conteúdo e elementos visuais da Página Inicial da Vakaria."""
    # 1. Barra de Aviso Superior (Top Announcement Bar)
    announcement_active = models.BooleanField(_("Exibir Barra Superior"), default=True)
    announcement_badge = models.CharField(_("Tag da Barra"), max_length=50, default="✨ NOVIDADE", blank=True)
    announcement_text = models.CharField(_("Texto do Aviso"), max_length=255, default="Frete Grátis para compras acima de R$ 399 | Entregas expressas em Cajazeiras e região")
    announcement_link = models.CharField(_("Link do Aviso (Opcional)"), max_length=255, blank=True, default="/produtos/")

    # 2. Card Moda Feminina (Coleções em Destaque)
    women_card_image = models.ImageField(_("Foto Card Feminino"), upload_to="home/cards/", blank=True, null=True)
    women_card_image_url = models.URLField(_("URL da Foto Feminina (Fallback/CDN)"), blank=True, default="https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1000&q=80")
    women_card_badge = models.CharField(_("Badge Card Feminino"), max_length=60, default="👗 Coleção Feminina")
    women_card_title = models.CharField(_("Título Card Feminino"), max_length=120, default="Moda Feminina Autoral")
    women_card_subtitle = models.TextField(_("Descrição Card Feminino"), default="Vestidos fluidos, peças em seda pura, alfaiataria premium e conjuntos da Farm Rio e Luiza Fit.")
    women_card_url = models.CharField(_("Link Card Feminino"), max_length=255, default="/produtos/?gender=F")
    women_card_btn_text = models.CharField(_("Texto do Botão Feminino"), max_length=60, default="Ver Coleção Feminina")

    # 3. Card Moda Masculina (Coleções em Destaque)
    men_card_image = models.ImageField(_("Foto Card Masculino"), upload_to="home/cards/", blank=True, null=True)
    men_card_image_url = models.URLField(_("URL da Foto Masculina (Fallback/CDN)"), blank=True, default="https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1000&q=80")
    men_card_badge = models.CharField(_("Badge Card Masculino"), max_length=60, default="👔 Coleção Masculina")
    men_card_title = models.CharField(_("Título Card Masculino"), max_length=120, default="Moda Masculina Elegante")
    men_card_subtitle = models.TextField(_("Descrição Card Masculino"), default="Camisas em linho nobre, blazers slim, polos pima cotton e bermudas alfaiataria.")
    men_card_url = models.CharField(_("Link Card Masculino"), max_length=255, default="/produtos/?gender=M")
    men_card_btn_text = models.CharField(_("Texto do Botão Masculino"), max_length=60, default="Ver Coleção Masculina")

    # 4. Seção Loja Física & Sobre (Cajazeiras - PB)
    store_image = models.ImageField(_("Foto da Loja Física"), upload_to="home/store/", blank=True, null=True)
    store_image_url = models.URLField(_("URL da Foto da Loja (Fallback/CDN)"), blank=True, default="https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1000&q=80")
    store_badge = models.CharField(_("Badge Seção Loja"), max_length=100, default="📍 Loja Física em Cajazeiras - PB")
    store_title = models.CharField(_("Título Seção Loja"), max_length=150, default="Experiência Presencial na Vakaria")
    store_description = models.TextField(_("Descrição Seção Loja"), default="Localizada no centro de Cajazeiras, nossa loja física foi criada para proporcionar conforto, sofisticação e uma experiência de compra personalizada. Venha conhecer de perto as peças, experimentar as composições e tomar um café com a nossa equipe.")
    store_address = models.CharField(_("Endereço Completo"), max_length=255, default="Rua José Pires Braga 120, Cajazeiras PB, 58900-000, Brasil")
    store_phone = models.CharField(_("WhatsApp & Telefone de Vendas"), max_length=50, default="+55 81 8398-3355")
    store_instagram_handle = models.CharField(_("Instagram Handle"), max_length=60, default="@eduardo_vaka_")
    store_maps_url = models.CharField(_("Link do Google Maps"), max_length=500, default="https://maps.google.com/?q=Rua+Jose+Pires+Braga+120+Cajazeiras+PB")
    
    STORE_STATUS_MODE_CHOICES = [
        ("auto", _("🟢 Automático pelo Horário de Funcionamento")),
        ("open", _("🟢 Forçar Aberto")),
        ("closed", _("🔴 Forçar Fechado")),
        ("manual", _("✏️ Texto Manual Fixo")),
    ]
    store_status_mode = models.CharField(_("Modo do Selo de Status"), max_length=20, choices=STORE_STATUS_MODE_CHOICES, default="auto")
    store_status_badge = models.CharField(_("Badge de Status / Texto Manual"), max_length=100, default="Loja Aberta", blank=True)
    
    # Horários Estruturados
    store_weekday_open = models.TimeField(_("Seg a Sex - Abertura"), default=datetime.time(8, 0))
    store_weekday_close = models.TimeField(_("Seg a Sex - Fechamento"), default=datetime.time(18, 0))
    
    store_saturday_active = models.BooleanField(_("Abre aos Sábados"), default=True)
    store_saturday_open = models.TimeField(_("Sábado - Abertura"), default=datetime.time(8, 0))
    store_saturday_close = models.TimeField(_("Sábado - Fechamento"), default=datetime.time(13, 0))
    
    store_sunday_active = models.BooleanField(_("Abre aos Domingos / Feriados"), default=False)
    store_sunday_open = models.TimeField(_("Domingo - Abertura"), null=True, blank=True)
    store_sunday_close = models.TimeField(_("Domingo - Fechamento"), null=True, blank=True)
    
    store_hours_text = models.CharField(_("Texto Resumo do Horário"), max_length=150, default="Segunda a Sexta: 08h às 18h • Sábado: 08h às 13h", blank=True)

    # 5. Seção de Drops da Semana
    drops_badge = models.CharField(_("Badge da Seção Drops"), max_length=80, default="🔥 Lançamentos Recentes")
    drops_title = models.CharField(_("Título da Seção Drops"), max_length=120, default="Drops & Novidades da Semana")
    drops_subtitle = models.CharField(_("Subtítulo da Seção Drops"), max_length=200, default="Novidades exclusivas que chegam duas vezes por semana na loja.")

    # 6. Quatro Cards de Vantagens / Diferenciais
    benefit1_icon = models.CharField(_("Ícone Vantagem 1"), max_length=60, default="solar:refresh-circle-bold-duotone")
    benefit1_title = models.CharField(_("Título Vantagem 1"), max_length=80, default="Drops 2x por Semana")
    benefit1_subtitle = models.CharField(_("Subtítulo Vantagem 1"), max_length=120, default="Novidades terças e quintas")

    benefit2_icon = models.CharField(_("Ícone Vantagem 2"), max_length=60, default="solar:tag-bold-duotone")
    benefit2_title = models.CharField(_("Título Vantagem 2"), max_length=80, default="Curadoria Multimarcas")
    benefit2_subtitle = models.CharField(_("Subtítulo Vantagem 2"), max_length=120, default="Os melhores produtos e atendimento da região")

    benefit3_icon = models.CharField(_("Ícone Vantagem 3"), max_length=60, default="solar:chat-round-dots-bold-duotone")
    benefit3_title = models.CharField(_("Título Vantagem 3"), max_length=80, default="Personal Stylist VIP")
    benefit3_subtitle = models.CharField(_("Subtítulo Vantagem 3"), max_length=120, default="Atendimento humanizado")

    benefit4_icon = models.CharField(_("Ícone Vantagem 4"), max_length=60, default="solar:box-minimalistic-bold-duotone")
    benefit4_title = models.CharField(_("Título Vantagem 4"), max_length=80, default="Loja Física & Envio")
    benefit4_subtitle = models.CharField(_("Subtítulo Vantagem 4"), max_length=120, default="Cajazeiras-PB e todo o Brasil")

    # 7. Seção de Avaliações
    reviews_active = models.BooleanField(_("Exibir Seção de Avaliações"), default=True)
    reviews_title = models.CharField(_("Título da Seção de Depoimentos"), max_length=120, default="O que Nossos Clientes Dizem", blank=True)
    reviews_subtitle = models.CharField(_("Subtítulo da Seção de Depoimentos"), max_length=200, default="Experiência comprovada por quem veste e confia na curadoria multimarcas da Vakaria.", blank=True)

    # 8. Promoções Relâmpago & Contador Regressivo (Timer)
    promo_active = models.BooleanField(_("Ativar Bloco de Promoções & Timer"), default=True)
    promo_badge = models.CharField(_("Tag da Promoção"), max_length=100, default="⚡ DROP RELÂMPAGO DE 48 HORAS", blank=True)
    promo_title = models.CharField(_("Título da Promoção"), max_length=150, default="Peças Selecionadas com até 30% OFF", blank=True)
    promo_subtitle = models.TextField(_("Subtítulo da Promoção"), default="Condições exclusivas por tempo limitado. Aproveite a contagem regressiva para garantir sua numeração.", blank=True)
    promo_discount_badge = models.CharField(_("Tag de Desconto"), max_length=50, default="-30% OFF", blank=True)
    promo_end_date = models.DateTimeField(_("Data/Hora de Término do Timer"), null=True, blank=True)
    promo_card_image = models.ImageField(_("Foto do Card Promocional"), upload_to="home/promo/", blank=True, null=True)
    promo_card_image_url = models.URLField(_("URL da Foto Promocional (Fallback/CDN)"), blank=True, default="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1000&q=80")
    promo_button_text = models.CharField(_("Texto do Botão Promocional"), max_length=80, default="Garantir Oferta no WhatsApp", blank=True)
    promo_button_url = models.CharField(_("Link do Botão"), max_length=255, default="/produtos/?gender=F", blank=True)
    promo_stock_alert_text = models.CharField(_("Alerta de Estoque / Escassez"), max_length=150, default="⚠️ Últimas unidades disponíveis na loja física", blank=True)
    promo_top_ticker_active = models.BooleanField(_("Exibir Barra Fixa no Topo com Timer"), default=True)

    # 9. Contador Regressivo para Drops
    countdown_active = models.BooleanField(_("Ativar Contador Regressivo"), default=False)
    countdown_label = models.CharField(_("Texto do Contador"), max_length=120, default="Lançamento Novo Drop", blank=True)
    countdown_target_date = models.DateTimeField(_("Data/Hora Alvo do Lançamento"), null=True, blank=True)

    # 10. Botão de Grupo VIP / WhatsApp
    whatsapp_group_active = models.BooleanField(_("Exibir Botão de Grupo VIP"), default=True)
    whatsapp_group_text = models.CharField(_("Texto do Botão VIP"), max_length=100, default="Grupo VIP Lançamentos", blank=True)
    whatsapp_group_url = models.CharField(_("Link do Grupo VIP (WhatsApp)"), max_length=255, default="https://chat.whatsapp.com/exemplo", blank=True)

    # 11. Compartilhamento Social & OpenGraph
    og_share_image = models.ImageField(_("Foto de Prévia no WhatsApp (OpenGraph)"), upload_to="cms/og/", blank=True, null=True)
    og_share_image_url = models.URLField(_("URL da Foto de Prévia"), blank=True)
    og_share_title = models.CharField(_("Título no Compartilhamento"), max_length=200, blank=True, default="Vakaria Barbearia | Alta Moda Feminina & Masculina")
    og_share_description = models.TextField(_("Descrição no Compartilhamento"), blank=True, default="Curadoria exclusiva das marcas mais desejadas do Brasil em Cajazeiras - PB.")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Configuração da Página Inicial")
        verbose_name_plural = _("Configurações da Página Inicial")

    def __str__(self):
        return "Configurações da Página Inicial (Home CMS)"

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    @property
    def final_women_card_image(self):
        if self.women_card_image:
            return self.women_card_image.url
        return self.women_card_image_url or "https://images.unsplash.com/photo-1483985988355-763728e1935b?auto=format&fit=crop&w=1000&q=80"

    @property
    def final_men_card_image(self):
        if self.men_card_image:
            return self.men_card_image.url
        return self.men_card_image_url or "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=1000&q=80"

    @property
    def final_promo_card_image(self):
        if self.promo_card_image:
            return self.promo_card_image.url
        return self.promo_card_image_url or "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1000&q=80"

    @property
    def is_promo_running(self):
        if not self.promo_active:
            return False
        if not self.promo_end_date:
            return True
        return timezone.now() < self.promo_end_date

    @property
    def promo_iso_end_date(self):
        if self.promo_end_date:
            return self.promo_end_date.isoformat()
        return (timezone.now() + timezone.timedelta(days=2)).isoformat()

    @property
    def final_store_image(self):
        if self.store_image:
            return self.store_image.url
        return self.store_image_url or "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1000&q=80"

    @property
    def final_og_image(self):
        if self.og_share_image:
            return self.og_share_image.url
        if self.og_share_image_url:
            return self.og_share_image_url
        return "/static/images/hero_feminina.jpg"

    @property
    def current_store_status(self):
        """Calcula o status em tempo real da loja com base no fuso horário do Brasil (America/Recife, UTC-3)."""
        if self.store_status_mode == "manual":
            return {
                "is_open": True,
                "badge_text": self.store_status_badge or "Loja Aberta",
                "badge_class": "bg-success text-white",
                "badge_icon": "bx bx-store-alt",
                "status_label": "Manual",
            }
        elif self.store_status_mode == "open":
            return {
                "is_open": True,
                "badge_text": self.store_status_badge or "Loja Aberta",
                "badge_class": "bg-success text-white",
                "badge_icon": "bx bx-door-open",
                "status_label": "Aberto",
            }
        elif self.store_status_mode == "closed":
            return {
                "is_open": False,
                "badge_text": self.store_status_badge or "Fechado no momento",
                "badge_class": "bg-secondary text-white",
                "badge_icon": "bx bx-time-five",
                "status_label": "Fechado",
            }

        # Modo Automático ('auto')
        try:
            tz = ZoneInfo("America/Recife")
            now = timezone.now().astimezone(tz)
        except Exception:
            now = timezone.localtime(timezone.now())

        weekday = now.weekday()  # 0 = Seg, 1 = Ter, ..., 5 = Sáb, 6 = Dom
        current_time = now.time()

        is_open = False
        badge_text = ""
        badge_class = "bg-secondary text-white"

        open_h = self.store_weekday_open.strftime('%H:%M') if self.store_weekday_open else "08:00"
        close_h = self.store_weekday_close.strftime('%H:%M') if self.store_weekday_close else "18:00"
        sat_open_h = self.store_saturday_open.strftime('%H:%M') if self.store_saturday_open else "08:00"
        sat_close_h = self.store_saturday_close.strftime('%H:%M') if self.store_saturday_close else "13:00"
        sun_open_h = self.store_sunday_open.strftime('%H:%M') if self.store_sunday_open else "09:00"
        sun_close_h = self.store_sunday_close.strftime('%H:%M') if self.store_sunday_close else "13:00"

        if weekday < 5:  # Seg a Sex
            if self.store_weekday_open and self.store_weekday_close:
                if self.store_weekday_open <= current_time <= self.store_weekday_close:
                    is_open = True
                    badge_text = f"Aberto agora • Fecha às {close_h}"
                    badge_class = "bg-success text-white"
                elif current_time < self.store_weekday_open:
                    badge_text = f"Fechado • Abre hoje às {open_h}"
                else:
                    if weekday == 4:  # Sexta à noite
                        if self.store_saturday_active and self.store_saturday_open:
                            badge_text = f"Fechado • Abre amanhã às {sat_open_h}"
                        else:
                            badge_text = f"Fechado • Abre seg às {open_h}"
                    else:
                        badge_text = f"Fechado • Abre amanhã às {open_h}"
            else:
                is_open = True
                badge_text = self.store_status_badge or "Loja Aberta"
                badge_class = "bg-success text-white"

        elif weekday == 5:  # Sábado
            if self.store_saturday_active and self.store_saturday_open and self.store_saturday_close:
                if self.store_saturday_open <= current_time <= self.store_saturday_close:
                    is_open = True
                    badge_text = f"Aberto hoje até {sat_close_h}"
                    badge_class = "bg-success text-white"
                elif current_time < self.store_saturday_open:
                    badge_text = f"Fechado • Abre hoje às {sat_open_h}"
                else:
                    if self.store_sunday_active and self.store_sunday_open:
                        badge_text = f"Fechado • Abre amanhã às {sun_open_h}"
                    else:
                        badge_text = f"Fechado • Abre seg às {open_h}"
            else:
                badge_text = f"Fechado • Abre seg às {open_h}"

        else:  # Domingo (6)
            if self.store_sunday_active and self.store_sunday_open and self.store_sunday_close:
                if self.store_sunday_open <= current_time <= self.store_sunday_close:
                    is_open = True
                    badge_text = f"Aberto hoje até {sun_close_h}"
                    badge_class = "bg-success text-white"
                elif current_time < self.store_sunday_open:
                    badge_text = f"Fechado • Abre hoje às {sun_open_h}"
                else:
                    badge_text = f"Fechado • Abre seg às {open_h}"
            else:
                badge_text = f"Fechado hoje • Abre seg às {open_h}"

        return {
            "is_open": is_open,
            "badge_text": badge_text,
            "badge_class": badge_class,
            "badge_icon": "bx bx-door-open" if is_open else "bx bx-time-five",
            "status_label": "Aberto Agora" if is_open else "Fechado",
        }

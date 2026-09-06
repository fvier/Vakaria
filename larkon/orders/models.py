import uuid
import urllib.parse
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from larkon.catalog.models import ProductVariant


class Cart(models.Model):
    """Carrinho de compras (sessão ou usuário autenticado)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="carts")
    session_key = models.CharField(_("Chave de Sessão"), max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(_("Criado em"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Atualizado em"), auto_now=True)

    class Meta:
        verbose_name = _("Carrinho")
        verbose_name_plural = _("Carrinhos")

    def __str__(self):
        return f"Carrinho #{self.id} ({self.user or self.session_key})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Item dentro do carrinho de compras."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(_("Quantidade"), default=1)
    added_at = models.DateTimeField(_("Adicionado em"), auto_now_add=True)

    class Meta:
        verbose_name = _("Item do Carrinho")
        verbose_name_plural = _("Itens do Carrinho")
        unique_together = ("cart", "variant")

    def __str__(self):
        return f"{self.quantity}x {self.variant}"

    @property
    def unit_price(self):
        return self.variant.final_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity


class Order(models.Model):
    """Pedido registrado na Grife HF."""
    STATUS_CHOICES = [
        ("pending", _("Aguardando Pagamento / Atendimento")),
        ("confirmed", _("Confirmado / Pago")),
        ("preparing", _("Em Separação")),
        ("shipped", _("Enviado / Em Transporte")),
        ("delivered", _("Entregue")),
        ("cancelled", _("Cancelado")),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("pix", _("Pix (Envio Imediato)")),
        ("credit_card", _("Cartão de Crédito (até 12x)")),
        ("debit_card", _("Cartão de Débito")),
        ("cash", _("Dinheiro / Espécie")),
        ("on_delivery", _("Pagamento na Entrega")),
    ]

    DELIVERY_METHOD_CHOICES = [
        ("pickup", _("Retirada na Loja")),
        ("motoboy", _("Entrega Rápida (Motoboy Cajazeiras)")),
        ("shipping", _("Envio Correios / Transportadora (Brasil)")),
    ]

    ORIGIN_CHOICES = [
        ("store_online", _("Loja Online")),
        ("whatsapp", _("WhatsApp VIP")),
        ("counter", _("Balcão / Loja Física")),
    ]

    order_number = models.CharField(_("Número do Pedido"), max_length=32, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")

    customer_name = models.CharField(_("Nome do Cliente"), max_length=150)
    customer_email = models.EmailField(_("E-mail"), blank=True)
    customer_phone = models.CharField(_("WhatsApp / Telefone"), max_length=30)

    shipping_address = models.CharField(_("Endereço Completo"), max_length=255, blank=True)
    city = models.CharField(_("Cidade"), max_length=100, blank=True)
    state = models.CharField(_("Estado (UF)"), max_length=2, blank=True)
    postal_code = models.CharField(_("CEP"), max_length=20, blank=True)

    payment_method = models.CharField(_("Forma de Pagamento"), max_length=30, choices=PAYMENT_METHOD_CHOICES, default="pix")
    delivery_method = models.CharField(_("Forma de Entrega"), max_length=30, choices=DELIVERY_METHOD_CHOICES, default="pickup")
    origin = models.CharField(_("Origem do Pedido"), max_length=30, choices=ORIGIN_CHOICES, default="store_online")

    notes = models.TextField(_("Observações / Instruções Especiais"), blank=True)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default="pending")

    subtotal = models.DecimalField(_("Subtotal (R$)"), max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(_("Frete (R$)"), max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(_("Total Geral (R$)"), max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(_("Data do Pedido"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Última Atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Pedido")
        verbose_name_plural = _("Pedidos")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pedido #{self.order_number} - {self.customer_name} (R$ {self.total})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"GHF-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def generate_whatsapp_link(self, whatsapp_number="558391650137"):
        """Gera o link de checkout VIP humanizado para o WhatsApp da Grife HF."""
        items_list = []
        for item in self.items.all():
            items_list.append(f"• {item.quantity}x *{item.product_title}* (Tam: {item.size}, Cor: {item.color}) - R$ {item.total_price:.2f}")

        items_str = "\n".join(items_list)
        msg = (
            f"✨ *Novo Pedido VIP — Grife HF* ✨\n\n"
            f"📋 *Pedido:* #{self.order_number}\n"
            f"👤 *Cliente:* {self.customer_name}\n"
            f"📱 *Contato:* {self.customer_phone}\n\n"
            f"🛍️ *Peças Escolhidas:*\n{items_str}\n\n"
            f"💰 *Total:* R$ {self.total:.2f}\n"
            f"📍 *Entrega:* {self.shipping_address}, {self.city}-{self.state}\n\n"
            f"Gostaria de confirmar a disponibilidade e finalizar o pagamento!"
        )
        encoded_msg = urllib.parse.quote(msg)
        return f"https://wa.me/{whatsapp_number}?text={encoded_msg}"

    def generate_receipt_whatsapp_link(self):
        """Gera comprovante de venda humanizado para enviar direto no WhatsApp do cliente."""
        clean_phone = "".join(filter(str.isdigit, self.customer_phone))
        if not clean_phone.startswith("55") and len(clean_phone) in (10, 11):
            clean_phone = f"55{clean_phone}"

        items_list = []
        for item in self.items.all():
            color_part = f", Cor: {item.color}" if item.color else ""
            items_list.append(f"• {item.quantity}x *{item.product_title}* (Tam: {item.size}{color_part}) — R$ {item.total_price:.2f}")

        items_str = "\n".join(items_list)
        payment_display = self.get_payment_method_display()
        delivery_display = self.get_delivery_method_display()

        pix_block = ""
        if self.payment_method == "pix":
            pix_block = "\n🔑 *Chave Pix Oficial (WhatsApp):* 8391650137\n🏦 *Favorecido:* Grife HF Multimarcas\n"

        msg = (
            f"✨ *Comprovante de Pedido — Grife HF Multimarcas* ✨\n\n"
            f"Olá *{self.customer_name}*, seu pedido foi registrado com sucesso! 🎉\n\n"
            f"📋 *Código do Pedido:* #{self.order_number}\n"
            f"📅 *Data:* {self.created_at.strftime('%d/%m/%Y às %H:%M')}\n\n"
            f"🛍️ *Peças Selecionadas:*\n{items_str}\n\n"
            f"💳 *Forma de Pagamento:* {payment_display}{pix_block}"
            f"🛵 *Entrega / Retirada:* {delivery_display}\n"
            f"💰 *Total do Pedido:* R$ {self.total:.2f}\n\n"
            f"📦 *Status Atual:* {self.get_status_display()}\n\n"
            f"Muito obrigado pela preferência e confiança na Grife HF! Qualquer dúvida estamos 100% à sua disposição por aqui. ✨"
        )
        encoded_msg = urllib.parse.quote(msg)
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"

    def generate_status_whatsapp_link(self, status_type="preparing", tracking_code=""):
        """Gera link de WhatsApp para atualizações pontuais de envio / entrega."""
        clean_phone = "".join(filter(str.isdigit, self.customer_phone))
        if not clean_phone.startswith("55") and len(clean_phone) in (10, 11):
            clean_phone = f"55{clean_phone}"

        if status_type == "preparing":
            msg = (
                f"✨ Olá *{self.customer_name}*! Tudo bem?\n\n"
                f"Seu pedido *#{self.order_number}* já está sendo separado e embalado com todo carinho pela equipe da *Grife HF*! 📦✨\n\n"
                f"Assim que sair para entrega ou ficar pronto para retirada, avisaremos você imediatamente por aqui!"
            )
        elif status_type == "motoboy":
            addr = f" no endereço: *{self.shipping_address}, {self.city}*" if self.shipping_address else ""
            msg = (
                f"🛵 Olá *{self.customer_name}*! Ótima notícia!\n\n"
                f"O motoboy da *Grife HF* acabou de sair para realizar a entrega do seu pedido *#{self.order_number}*{addr}! 📦\n\n"
                f"Por favor, fique atento(a) para receber sua encomenda hoje mesmo. Muito obrigado!"
            )
        elif status_type == "pickup_ready":
            msg = (
                f"🏪 Olá *{self.customer_name}*! Sua sacola está pronta!\n\n"
                f"Seu pedido *#{self.order_number}* já está 100% separado e prontinho para retirada na loja física da *Grife HF*.\n"
                f"📍 *Endereço:* Rua José Pires Braga 120, Centro - Cajazeiras PB.\n"
                f"⏰ *Horário:* Segunda a Sábado das 09h às 19h.\n\n"
                f"Aguardamos sua visita!"
            )
        elif status_type == "shipped":
            track_str = f"\n📦 *Código de Rastreio:* {tracking_code}" if tracking_code else ""
            msg = (
                f"✈️ Olá *{self.customer_name}*! Seu pedido foi despachado!\n\n"
                f"Sua encomenda da *Grife HF* (Pedido *#{self.order_number}*) foi postada com sucesso nos Correios/Transportadora!{track_str}\n\n"
                f"Agradecemos muito pela confiança e desejamos uma excelente experiência com suas novas peças!"
            )
        else:
            msg = f"Olá *{self.customer_name}*! Atualização sobre seu pedido *#{self.order_number}* da Grife HF: {self.get_status_display()}."

        encoded_msg = urllib.parse.quote(msg)
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"




class OrderItem(models.Model):
    """Item individual gravado em um pedido finalizado."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_title = models.CharField(_("Nome da Peça"), max_length=200)
    brand_name = models.CharField(_("Marca"), max_length=150, blank=True)
    size = models.CharField(_("Tamanho"), max_length=30)
    color = models.CharField(_("Cor"), max_length=50, blank=True)
    quantity = models.PositiveIntegerField(_("Quantidade"), default=1)
    unit_price = models.DecimalField(_("Preço Unitário (R$)"), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_("Preço Total (R$)"), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _("Item do Pedido")
        verbose_name_plural = _("Itens do Pedido")

    def __str__(self):
        return f"{self.quantity}x {self.product_title} ({self.size})"


class ProductReservation(models.Model):
    """Reserva de Peça / Fila de Espera para Peças Esgotadas (CRM de Vendas)."""
    STATUS_CHOICES = [
        ("pending", _("Pendente (Aguardando Chegada)")),
        ("notified", _("Cliente Avisado")),
        ("converted", _("Venda Concluída")),
        ("cancelled", _("Cancelado / Desistiu")),
    ]

    product = models.ForeignKey("catalog.Product", on_delete=models.CASCADE, related_name="reservations", verbose_name=_("Peça"))
    customer_name = models.CharField(_("Nome do Cliente"), max_length=150)
    customer_phone = models.CharField(_("WhatsApp / Telefone"), max_length=30)
    color = models.CharField(_("Cor Desejada"), max_length=50, blank=True)
    size = models.CharField(_("Tamanho Desejado"), max_length=30, blank=True)
    notes = models.TextField(_("Observações"), blank=True)
    status = models.CharField(_("Status"), max_length=20, choices=STATUS_CHOICES, default="pending")
    notified_at = models.DateTimeField(_("Avisado em"), null=True, blank=True)

    created_at = models.DateTimeField(_("Data da Reserva"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Última Atualização"), auto_now=True)

    class Meta:
        verbose_name = _("Reserva / Fila de Espera")
        verbose_name_plural = _("Reservas / Fila de Espera")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reserva #{self.id} - {self.customer_name} ({self.product.title} - {self.size})"

    def generate_whatsapp_vip_link(self):
        """Gera link humanizado no WhatsApp do cliente avisando que a peça chegou com garantia de 24h."""
        clean_phone = "".join(filter(str.isdigit, self.customer_phone))
        if not clean_phone.startswith("55") and len(clean_phone) in (10, 11):
            clean_phone = f"55{clean_phone}"

        color_str = f" na cor *{self.color}*" if self.color else ""
        size_str = f" e tamanho *{self.size}*" if self.size else ""
        brand_str = f" ({self.product.brand.name})" if self.product.brand else ""

        msg = (
            f"Olá *{self.customer_name}*, tudo bem? ✨\n\n"
            f"Temos uma ótima notícia da *Grife HF*! A peça *{self.product.title}*{brand_str}{color_str}{size_str} que você estava aguardando *acabou de chegar no estoque*! 🎉\n\n"
            f"Sua reserva está garantida com exclusividade pelas próximas *24 horas*.\n"
            f"Podemos separar para você retirar ou enviar para entrega hoje mesmo?"
        )
        encoded_msg = urllib.parse.quote(msg)
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"


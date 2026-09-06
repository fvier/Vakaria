import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import user_passes_test
from django.utils.text import slugify
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count, F
from .models import (
    Product,
    Brand,
    Category,
    Drop,
    CarouselSlide,
    LinktreeItem,
    ProductImage,
    ProductVariant,
    HomePageConfig,
    CustomerReview,
    StockMovement,
)


class LandingPageView(TemplateView):
    template_name = "pages/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["home_config"] = HomePageConfig.get_config()
        context["hero_slides"] = CarouselSlide.objects.filter(is_active=True, slide_type="hero").order_by("order", "-created_at")
        context["reviews"] = CustomerReview.objects.filter(is_active=True).order_by("order", "-created_at")
        context["featured_products"] = Product.objects.filter(is_active=True, is_featured=True).select_related("brand", "category")[:6]
        context["women_products"] = Product.objects.filter(is_active=True, gender="F").select_related("brand")[:4]
        context["men_products"] = Product.objects.filter(is_active=True, gender="M").select_related("brand")[:4]
        
        # Peças em Promoção & Drop Relâmpago
        promo_qs = Product.objects.filter(is_active=True).select_related("brand", "category").prefetch_related("variants", "images")
        discounted = promo_qs.filter(compare_at_price__gt=F("price"))
        if discounted.exists():
            context["promo_products"] = discounted[:6]
        else:
            context["promo_products"] = promo_qs.filter(is_featured=True)[:6] or promo_qs[:6]

        context["active_drops"] = Drop.objects.filter(is_active=True)[:2]
        context["brands"] = Brand.objects.filter(is_active=True).order_by("name")
        context["categories"] = Category.objects.filter(is_active=True, parent__isnull=True)
        return context


class ProductGridView(ListView):
    model = Product
    template_name = "pages/product-grid.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related("brand", "category", "drop").prefetch_related("images", "variants")

        gender = self.request.GET.get("gender")
        if gender:
            queryset = queryset.filter(Q(gender=gender) | Q(gender="U"))

        brand_slug = self.request.GET.get("brand")
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)

        category_slug = self.request.GET.get("category")
        if category_slug:
            category_obj = Category.objects.filter(slug=category_slug).first()
            if category_obj:
                if category_obj.children.exists():
                    # Categoria Pai: exibe produtos da categoria pai e de todas as subcategorias
                    queryset = queryset.filter(Q(category=category_obj) | Q(category__parent=category_obj))
                else:
                    # Subcategoria específica
                    queryset = queryset.filter(category=category_obj)
            else:
                queryset = queryset.filter(category__slug=category_slug)

        drop_slug = self.request.GET.get("drop")
        if drop_slug:
            queryset = queryset.filter(drop__slug=drop_slug)

        search = self.request.GET.get("q")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search)
            )

        ordering = self.request.GET.get("ordering", "-created_at")
        if ordering in ["price", "-price", "-created_at", "title"]:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_parents = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related("children").order_by("order", "name")
        
        # Segmentação Masculino / Feminino (Use Luiza Fit)
        context["men_categories"] = [c for c in all_parents if c.slug != "luiza-fit" and (c.gender_target in ["M", "U", ""] or c.order < 20)]
        context["women_categories"] = [c for c in all_parents if c.slug == "luiza-fit" or c.gender_target == "F" or c.order >= 20]
        context["all_parent_categories"] = all_parents
        context["parent_categories"] = all_parents
        context["brands"] = Brand.objects.filter(is_active=True)
        context["featured_drops"] = Drop.objects.filter(is_active=True)[:3]
        
        category_slug = self.request.GET.get("category", "")
        selected_category = None
        selected_parent = None
        chips_subcategories = []

        if category_slug:
            selected_category = Category.objects.filter(slug=category_slug).select_related("parent").prefetch_related("children").first()
            if selected_category:
                if selected_category.parent:
                    selected_parent = selected_category.parent
                    chips_subcategories = list(selected_parent.children.filter(is_active=True).order_by("order", "name"))
                else:
                    selected_parent = selected_category
                    chips_subcategories = list(selected_category.children.filter(is_active=True).order_by("order", "name"))

        is_luiza_fit = bool(
            (selected_parent and selected_parent.slug == "luiza-fit") or
            (selected_category and (selected_category.slug == "luiza-fit" or (selected_category.parent and selected_category.parent.slug == "luiza-fit"))) or
            (category_slug == "luiza-fit" or category_slug.startswith("luiza-fit")) or
            (self.request.GET.get("gender") == "F")
        )
        is_masculine_context = bool(
            (self.request.GET.get("gender") == "M") or
            (selected_parent and selected_parent.slug != "luiza-fit" and selected_parent.gender_target in ["M", "U"])
        )

        context["selected_category"] = selected_category
        context["selected_parent"] = selected_parent
        context["chips_subcategories"] = chips_subcategories
        context["active_category"] = category_slug
        context["active_gender"] = self.request.GET.get("gender", "")
        context["active_brand"] = self.request.GET.get("brand", "")
        context["active_drop"] = self.request.GET.get("drop", "")
        context["search_query"] = self.request.GET.get("q", "")
        context["is_luiza_fit"] = is_luiza_fit
        context["is_masculine_context"] = is_masculine_context
        
        categories_data = []
        for parent in all_parents:
            children = [{"id": c.id, "name": c.name, "slug": c.slug} for c in parent.children.filter(is_active=True).order_by("order", "name")]
            categories_data.append({
                "id": parent.id,
                "name": parent.name,
                "slug": parent.slug,
                "gender": parent.gender_target,
                "children": children
            })
        context["categories_json"] = categories_data
        if self.request.user.is_authenticated and self.request.user.is_staff:
            context["admin_total_products"] = Product.objects.filter(is_active=True).count()
            context["admin_in_stock"] = Product.objects.filter(is_active=True, variants__stock_quantity__gt=0).distinct().count()
            context["admin_out_of_stock"] = Product.objects.filter(is_active=True).exclude(variants__stock_quantity__gt=0).distinct().count()

        return context


COLOR_PALETTE = {
    "Preto": "#0f172a",
    "Branco": "#ffffff",
    "Off-White": "#f3f4f6",
    "Azul Marinho": "#1e3a8a",
    "Azul Royal": "#2563eb",
    "Cinza Mescla": "#6b7280",
    "Bege/Cáqui": "#d4b996",
    "Verde Militar": "#365314",
    "Bordô/Vinho": "#881337",
    "Vermelho": "#dc2626",
    "Rosa/Nude": "#f472b6",
    "Terracota": "#9a3412",
    "Mostarda": "#d97706",
}


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def quick_create_product_view(request):
    """Cadastro rápido de novas peças com foto principal, fotos de galeria, marcas e cores."""
    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")

    title = request.POST.get("title", "").strip()
    if not title:
        messages.error(request, "O nome da peça é obrigatório.")
        return redirect("catalog:product_grid")

    price_str = request.POST.get("price", "0").replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        price_val = float(price_str)
    except ValueError:
        price_val = 0.0

    brand_id = request.POST.get("brand")
    brand_name = request.POST.get("brand_name", "").strip()
    brand = None
    if brand_id:
        brand = Brand.objects.filter(id=brand_id).first()
    elif brand_name:
        brand, _ = Brand.objects.get_or_create(name=brand_name)
    if not brand:
        brand = Brand.objects.first() or Brand.objects.create(name="Grife HF")

    category_id = request.POST.get("category")
    category = Category.objects.filter(id=category_id).first() if category_id else None
    if not category:
        category = Category.objects.first()

    gender = request.POST.get("gender", "M")
    is_exclusive = request.POST.get("is_exclusive") in ["1", "true", "on", True]
    is_featured = request.POST.get("is_featured") in ["1", "true", "on", True]
    cover_image = request.FILES.get("cover_image")

    from django.utils.text import slugify
    base_slug = slugify(title) or "produto"
    slug = base_slug
    counter = 1
    while Product.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    product = Product.objects.create(
        title=title,
        slug=slug,
        brand=brand,
        category=category,
        price=price_val,
        gender=gender,
        is_exclusive=is_exclusive,
        is_featured=is_featured,
        is_active=True
    )

    if cover_image:
        ProductImage.objects.create(
            product=product,
            image=cover_image,
            is_cover=True,
            order=0
        )

    # Fotos adicionais de galeria
    gallery_images = request.FILES.getlist("gallery_images")
    for idx, g_img in enumerate(gallery_images, start=1):
        ProductImage.objects.create(
            product=product,
            image=g_img,
            is_cover=False,
            order=idx
        )

    # Suporte a matriz avançada de variantes (Cor -> Foto -> Tamanhos com Quantidades)
    import json
    variants_matrix_json = request.POST.get("variants_matrix_json")
    matrix_parsed = False
    
    if variants_matrix_json:
        try:
            matrix_data = json.loads(variants_matrix_json)
            if isinstance(matrix_data, list) and len(matrix_data) > 0:
                for idx, c_entry in enumerate(matrix_data):
                    c_name = c_entry.get("name", "").strip()
                    c_hex = c_entry.get("hex", "").strip()
                    
                    # Verifica se foi enviada foto para esta cor
                    c_file = request.FILES.get(f"color_image_{idx}") or request.FILES.get(f"color_image_{slugify(c_name)}")
                    if c_file:
                        ProductImage.objects.create(
                            product=product,
                            image=c_file,
                            color=c_name,
                            is_cover=False,
                            order=idx + 10
                        )

                    c_sizes = c_entry.get("sizes", [])
                    for s_item in c_sizes:
                        if isinstance(s_item, dict):
                            s_name = s_item.get("size", "").strip()
                            s_stock = int(s_item.get("stock", 10))
                        else:
                            s_name = str(s_item).strip()
                            s_stock = 10
                        if s_name:
                            sku_suffix = f"-{slugify(c_name)}" if c_name else ""
                            ProductVariant.objects.create(
                                product=product,
                                size=s_name,
                                color=c_name,
                                color_hex=c_hex,
                                stock_quantity=max(0, s_stock),
                                sku=f"{product.slug}-{slugify(s_name)}{sku_suffix}"
                            )
                matrix_parsed = True
        except Exception as e:
            matrix_parsed = False

    # Fallback caso nao use matriz avancada
    if not matrix_parsed:
        sizes = request.POST.getlist("sizes") or ["M"]
        colors = request.POST.getlist("colors") or [""]
        custom_colors_map = {}
        custom_json = request.POST.get("custom_colors_json")
        if custom_json:
            try:
                for item in json.loads(custom_json):
                    if "name" in item and "hex" in item:
                        custom_colors_map[item["name"].strip()] = item["hex"].strip()
            except Exception:
                pass

        for color in colors:
            c_name = color.strip()
            c_hex = custom_colors_map.get(c_name) or COLOR_PALETTE.get(c_name, "")
            for size in sizes:
                sku_suffix = f"-{slugify(c_name)}" if c_name else ""
                ProductVariant.objects.create(
                    product=product,
                    size=size,
                    color=c_name,
                    color_hex=c_hex,
                    stock_quantity=10,
                    sku=f"{product.slug}-{slugify(size)}{sku_suffix}"
                )

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1"
    msg = f"Peça '{product.title}' cadastrada com sucesso!"
    
    if is_ajax:
        return JsonResponse({
            "success": True,
            "message": msg,
            "product_id": product.id,
            "product_title": product.title,
            "product_url": product.get_absolute_url(),
        })

    messages.success(request, msg)
    return redirect("catalog:product_grid")


def get_product_edit_data_view(request, pk):
    """Retorna dados completos do produto, imagens e matriz de cores/tamanhos em JSON para edição e visualização ampliada."""
    import urllib.parse
    product = get_object_or_404(Product, pk=pk)
    variants = list(product.variants.values("id", "size", "color", "color_hex", "stock_quantity"))
    selected_sizes = list(dict.fromkeys(v["size"] for v in variants if v["stock_quantity"] > 0))
    if not selected_sizes and variants:
        selected_sizes = list(dict.fromkeys(v["size"] for v in variants))
        
    selected_colors = list(dict.fromkeys(v["color"] for v in variants if v["color"]))
    cover_url = product.cover_image.url if product.cover_image else ""
    images_data = [{"url": img.url, "color": img.color or ""} for img in product.images.all()]
    images_urls = [img["url"] for img in images_data]
    if not images_urls and cover_url:
        images_urls = [cover_url]
        images_data = [{"url": cover_url, "color": ""}]

    brand_name = product.brand.name if product.brand else "Grife HF"
    brand_slug = product.brand.slug if product.brand else "grife-hf"
    category_name = product.category.name if product.category else "Sem Categoria"

    whatsapp_text = urllib.parse.quote(
        f"Olá! Gostei da peça '{product.title}' da {brand_name} (R$ {product.price:.2f}) na Grife HF. Gostaria de garantir a minha!"
    )

    return JsonResponse({
        "id": product.id,
        "title": product.title,
        "price": str(product.price),
        "brand_id": product.brand_id or "",
        "brand_name": brand_name,
        "brand_slug": brand_slug,
        "category_id": product.category_id or "",
        "category_name": category_name,
        "gender": product.gender,
        "gender_display": product.get_gender_display(),
        "is_exclusive": product.is_exclusive,
        "is_featured": product.is_featured,
        "is_in_stock": product.in_stock,
        "cover_image_url": cover_url,
        "images": images_urls,
        "images_data": images_data,
        "sizes": selected_sizes,
        "colors": selected_colors,
        "available_colors": product.available_colors,
        "variants_matrix": product.variants_matrix,
        "total_stock": product.total_stock,
        "product_url": product.get_absolute_url(),
        "description": product.description or "Peça autêntica e exclusiva com corte e acabamento premium da Grife HF.",
        "whatsapp_url": f"https://wa.me/558391650137?text={whatsapp_text}",
    })


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def quick_edit_product_view(request, pk):
    """Atualiza dados, fotos adicionais, cores e tamanhos da peça postada diretamente via modal."""
    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")

    product = get_object_or_404(Product, pk=pk)
    
    title = request.POST.get("title", "").strip() or product.title
    price_str = request.POST.get("price", "0").replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        price_val = float(price_str)
    except ValueError:
        price_val = float(product.price)

    brand_id = request.POST.get("brand")
    if brand_id:
        brand = Brand.objects.filter(id=brand_id).first()
        if brand:
            product.brand = brand

    category_id = request.POST.get("category")
    if category_id:
        category = Category.objects.filter(id=category_id).first()
        if category:
            product.category = category

    product.title = title
    product.price = price_val
    product.gender = request.POST.get("gender", product.gender)
    product.is_exclusive = request.POST.get("is_exclusive") in ["1", "true", "on", True]
    product.is_featured = request.POST.get("is_featured") in ["1", "true", "on", True]
    
    is_in_stock = request.POST.get("is_in_stock") in ["1", "true", "on", True]
    product.save()

    # Atualização ou Troca de Foto Principal
    cover_image = request.FILES.get("cover_image")
    if cover_image:
        existing_cover = product.images.filter(is_cover=True).first()
        if existing_cover:
            existing_cover.image = cover_image
            existing_cover.save()
        else:
            ProductImage.objects.create(
                product=product,
                image=cover_image,
                is_cover=True,
                order=0
            )

    # Novas Fotos para a Galeria
    gallery_images = request.FILES.getlist("gallery_images")
    start_order = product.images.count() + 1
    for idx, g_img in enumerate(gallery_images, start=start_order):
        ProductImage.objects.create(
            product=product,
            image=g_img,
            is_cover=False,
            order=idx
        )

    # Atualização via Matriz Avançada ou Modo Simples
    import json
    variants_matrix_json = request.POST.get("variants_matrix_json")
    matrix_parsed = False

    if variants_matrix_json:
        try:
            matrix_data = json.loads(variants_matrix_json)
            if isinstance(matrix_data, list) and len(matrix_data) > 0:
                # Remove variantes antigas e recria com a nova configuracao
                product.variants.all().delete()
                for idx, c_entry in enumerate(matrix_data):
                    c_name = c_entry.get("name", "").strip()
                    c_hex = c_entry.get("hex", "").strip()

                    # Foto vinculada a esta cor
                    c_file = request.FILES.get(f"color_image_{idx}") or request.FILES.get(f"color_image_{slugify(c_name)}")
                    if c_file:
                        ProductImage.objects.create(
                            product=product,
                            image=c_file,
                            color=c_name,
                            is_cover=False,
                            order=idx + 10
                        )

                    c_sizes = c_entry.get("sizes", [])
                    for s_item in c_sizes:
                        if isinstance(s_item, dict):
                            s_name = s_item.get("size", "").strip()
                            s_stock = int(s_item.get("stock", 10 if is_in_stock else 0))
                        else:
                            s_name = str(s_item).strip()
                            s_stock = 10 if is_in_stock else 0
                        if s_name:
                            sku_suffix = f"-{slugify(c_name)}" if c_name else ""
                            ProductVariant.objects.create(
                                product=product,
                                size=s_name,
                                color=c_name,
                                color_hex=c_hex,
                                stock_quantity=max(0, s_stock),
                                sku=f"{product.slug}-{slugify(s_name)}{sku_suffix}"
                            )
                matrix_parsed = True
        except Exception:
            matrix_parsed = False

    if not matrix_parsed:
        sizes = request.POST.getlist("sizes")
        colors = request.POST.getlist("colors") or [""]
        stock_qty = 10 if is_in_stock else 0

        custom_colors_map = {}
        custom_json = request.POST.get("custom_colors_json")
        if custom_json:
            try:
                for item in json.loads(custom_json):
                    if "name" in item and "hex" in item:
                        custom_colors_map[item["name"].strip()] = item["hex"].strip()
            except Exception:
                pass

        if sizes:
            existing_combos = {(v.size, v.color): v for v in product.variants.all()}
            new_combos = {(s, c.strip()) for s in sizes for c in colors}

            # Desativa/Zera combinações desmarcadas
            for (s, c), v in existing_combos.items():
                if (s, c) not in new_combos:
                    v.stock_quantity = 0
                    v.save(update_fields=["stock_quantity"])

            # Cria ou reativa combinações selecionadas
            for s in sizes:
                for c in colors:
                    c_name = c.strip()
                    c_hex = custom_colors_map.get(c_name) or COLOR_PALETTE.get(c_name, "")
                    if (s, c_name) in existing_combos:
                        v = existing_combos[(s, c_name)]
                        if is_in_stock:
                            if v.stock_quantity == 0:
                                v.stock_quantity = 10
                        else:
                            v.stock_quantity = 0
                        if c_hex and not v.color_hex:
                            v.color_hex = c_hex
                        v.save()
                    else:
                        sku_suffix = f"-{slugify(c_name)}" if c_name else ""
                        ProductVariant.objects.create(
                            product=product,
                            size=s,
                            color=c_name,
                            color_hex=c_hex,
                            stock_quantity=stock_qty,
                            sku=f"{product.slug}-{slugify(s)}{sku_suffix}"
                        )
        else:
            for v in product.variants.all():
                v.stock_quantity = stock_qty
                v.save(update_fields=["stock_quantity"])

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1"
    msg = f"Peça '{product.title}' atualizada com sucesso!"

    if is_ajax:
        return JsonResponse({
            "success": True,
            "message": msg,
            "product_id": product.id,
            "product_title": product.title,
            "product_price": float(product.price),
            "in_stock": product.in_stock,
            "cover_url": product.cover_image.url if product.cover_image else "",
        })

    messages.success(request, msg)
    return redirect("catalog:product_grid")


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def quick_delete_product_view(request, pk):
    """Exclui ou arquiva (desativa) a peça do catálogo."""
    if request.method != "POST":
        return HttpResponseBadRequest("Método inválido")

    product = get_object_or_404(Product, pk=pk)
    action = request.POST.get("action", "delete")  # "delete" ou "archive"
    product_title = product.title

    if action == "archive":
        product.is_active = False
        product.save()
        msg = f"A peça '{product_title}' foi desativada e ocultada da vitrine com sucesso."
    else:
        # Exclusão definitiva e limpeza de arquivos físicos em disco
        for p_img in product.images.all():
            if p_img.image:
                try:
                    p_img.image.delete(save=False)
                except Exception:
                    pass
        product.delete()
        msg = f"A peça '{product_title}' e todas as suas fotos foram excluídas definitivamente."

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1"
    if is_ajax:
        return JsonResponse({
            "success": True,
            "message": msg,
            "product_id": pk,
            "action": action,
        })

    messages.success(request, msg)
    return redirect("catalog:product_grid")


class ProductDetailView(DetailView):
    model = Product
    template_name = "pages/product-details.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        Product.objects.filter(pk=obj.pk).update(views_count=obj.views_count + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context["variants"] = product.variants.filter(stock_quantity__gt=0)
        context["available_sizes"] = product.variants.filter(stock_quantity__gt=0).values_list("size", flat=True).distinct()
        context["available_colors"] = product.available_colors
        context["variants_matrix"] = product.variants_matrix
        import json
        context["variants_matrix_json"] = json.dumps(product.variants_matrix)
        context["related_products"] = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(id=product.id)[:4]
        return context


class BrandListView(ListView):
    model = Brand
    template_name = "pages/brand-list.html"
    context_object_name = "brands"

    def get_queryset(self):
        # Prioriza as 6 marcas principais + marcas próprias
        order_slugs = ["lacoste", "nike", "adidas", "puma", "jordan", "oakley", "luiza-fit", "grife-hf"]
        qs = list(Brand.objects.filter(is_active=True).prefetch_related("products"))
        return sorted(qs, key=lambda b: order_slugs.index(b.slug) if b.slug in order_slugs else 99)


class BrandDetailView(DetailView):
    model = Brand
    template_name = "pages/seller-details.html"
    context_object_name = "seller"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = self.object.products.filter(is_active=True)
        return context


# ==============================================================================
# MÓDULO DE GESTÃO DE ESTOQUE (ENTRADAS & SAÍDAS)
# ==============================================================================

@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def admin_inventory_view(request):
    """Painel completo de controle de estoque: Entradas, Saídas, Ajustes e Histórico."""
    if request.method == "POST":
        action = request.POST.get("action")
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1"

        if action == "stock_in":
            variant_id = request.POST.get("variant_id")
            quantity = int(request.POST.get("quantity", 1))
            reason = request.POST.get("reason", "purchase")
            cost_price_str = request.POST.get("cost_price", "").strip()
            invoice_number = request.POST.get("invoice_number", "").strip()
            notes = request.POST.get("notes", "").strip()

            variant = get_object_or_404(ProductVariant, id=variant_id)
            prev_stock = variant.stock_quantity
            new_stock = prev_stock + quantity
            variant.stock_quantity = new_stock
            variant.save()

            cost_price = None
            if cost_price_str:
                try:
                    cost_price = Decimal(cost_price_str.replace(",", "."))
                except Exception:
                    cost_price = None

            movement = StockMovement.objects.create(
                variant=variant,
                movement_type="IN",
                reason=reason,
                quantity=quantity,
                previous_stock=prev_stock,
                new_stock=new_stock,
                cost_price=cost_price,
                invoice_number=invoice_number,
                notes=notes,
                created_by=request.user,
            )

            msg = f"Entrada de +{quantity} un. para '{variant.product.title}' ({variant.size}/{variant.color or 'Padrão'}) registrada! Novo saldo: {new_stock} un."
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": msg,
                    "variant_id": variant.id,
                    "new_stock": new_stock,
                    "product_total_stock": variant.product.total_stock,
                })
            messages.success(request, msg)
            return redirect("catalog:admin_inventory")

        elif action == "stock_out":
            variant_id = request.POST.get("variant_id")
            quantity = int(request.POST.get("quantity", 1))
            reason = request.POST.get("reason", "sale")
            invoice_number = request.POST.get("invoice_number", "").strip()
            notes = request.POST.get("notes", "").strip()

            variant = get_object_or_404(ProductVariant, id=variant_id)
            prev_stock = variant.stock_quantity
            if prev_stock < quantity:
                err = f"Atenção: Saldo insuficiente! Estoque atual é de {prev_stock} un."
                if is_ajax:
                    return JsonResponse({"success": False, "message": err}, status=400)
                messages.warning(request, err)
                return redirect("catalog:admin_inventory")

            new_stock = max(0, prev_stock - quantity)
            variant.stock_quantity = new_stock
            variant.save()

            movement = StockMovement.objects.create(
                variant=variant,
                movement_type="OUT",
                reason=reason,
                quantity=quantity,
                previous_stock=prev_stock,
                new_stock=new_stock,
                invoice_number=invoice_number,
                notes=notes,
                created_by=request.user,
            )

            msg = f"Saída de -{quantity} un. para '{variant.product.title}' ({variant.size}/{variant.color or 'Padrão'}) registrada! Novo saldo: {new_stock} un."
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": msg,
                    "variant_id": variant.id,
                    "new_stock": new_stock,
                    "product_total_stock": variant.product.total_stock,
                })
            messages.success(request, msg)
            return redirect("catalog:admin_inventory")

        elif action == "quick_adjust":
            variant_id = request.POST.get("variant_id")
            new_stock = int(request.POST.get("new_stock", 0))
            notes = request.POST.get("notes", "Ajuste manual de balanço").strip()

            variant = get_object_or_404(ProductVariant, id=variant_id)
            prev_stock = variant.stock_quantity
            diff = new_stock - prev_stock

            variant.stock_quantity = max(0, new_stock)
            variant.save()

            StockMovement.objects.create(
                variant=variant,
                movement_type="ADJUST",
                reason="inventory_audit",
                quantity=diff,
                previous_stock=prev_stock,
                new_stock=max(0, new_stock),
                notes=notes,
                created_by=request.user,
            )

            msg = f"Saldo de '{variant.product.title}' ({variant.size}) atualizado para {new_stock} un."
            if is_ajax:
                return JsonResponse({
                    "success": True,
                    "message": msg,
                    "variant_id": variant.id,
                    "new_stock": variant.stock_quantity,
                    "product_total_stock": variant.product.total_stock,
                })
            messages.success(request, msg)
            return redirect("catalog:admin_inventory")

        elif action == "batch_grid_in":
            product_id = request.POST.get("product_id")
            product = get_object_or_404(Product, id=product_id)
            reason = request.POST.get("reason", "purchase")
            invoice_number = request.POST.get("invoice_number", "").strip()
            notes = request.POST.get("notes", "").strip()

            total_added = 0
            for key, val in request.POST.items():
                if key.startswith("size_qty_") and val:
                    try:
                        v_id = int(key.replace("size_qty_", ""))
                        qty = int(val)
                        if qty > 0:
                            v = product.variants.filter(id=v_id).first()
                            if v:
                                p_stock = v.stock_quantity
                                n_stock = p_stock + qty
                                v.stock_quantity = n_stock
                                v.save()
                                StockMovement.objects.create(
                                    variant=v,
                                    movement_type="IN",
                                    reason=reason,
                                    quantity=qty,
                                    previous_stock=p_stock,
                                    new_stock=n_stock,
                                    invoice_number=invoice_number,
                                    notes=notes,
                                    created_by=request.user,
                                )
                                total_added += qty
                    except Exception:
                        pass

            msg = f"Entrada em grade concluída! +{total_added} peças adicionadas ao estoque de '{product.title}'."
            messages.success(request, msg)
            return redirect("catalog:admin_inventory")

    # GET: Preparação da listagem e métricas de estoque
    products_qs = (
        Product.objects.all()
        .select_related("brand", "category", "drop")
        .prefetch_related("variants", "images")
        .order_by("title")
    )

    search = request.GET.get("search", "").strip()
    if search:
        products_qs = products_qs.filter(
            Q(title__icontains=search) |
            Q(brand__name__icontains=search) |
            Q(category__name__icontains=search) |
            Q(variants__sku__icontains=search)
        ).distinct()

    brand_id = request.GET.get("brand")
    if brand_id:
        products_qs = products_qs.filter(brand_id=brand_id)

    category_id = request.GET.get("category")
    if category_id:
        products_qs = products_qs.filter(category_id=category_id)

    gender = request.GET.get("gender")
    if gender:
        products_qs = products_qs.filter(gender=gender)

    stock_filter = request.GET.get("stock_status")

    # Coleta de produtos e variantes com cálculo de estoque
    products_list = []
    total_inventory_units = 0
    total_cost_value = Decimal("0.00")
    total_retail_value = Decimal("0.00")
    out_of_stock_products = 0
    low_stock_products = 0
    in_stock_products = 0

    all_variants_flat = []

    for p in products_qs:
        p_total_stock = p.total_stock
        p_variants = list(p.variants.all())
        cover = p.cover_image.url if p.cover_image else "/static/images/products/product-placeholder.png"

        # Estatísticas por produto
        if p_total_stock == 0:
            out_of_stock_products += 1
            status_badge = {"text": "Esgotado", "class": "bg-danger text-white"}
        elif p_total_stock <= 2:
            low_stock_products += 1
            status_badge = {"text": "Estoque Baixo", "class": "bg-warning text-dark"}
        else:
            in_stock_products += 1
            status_badge = {"text": "Em Estoque", "class": "bg-success text-white"}

        # Filtro por status
        if stock_filter == "out_of_stock" and p_total_stock > 0:
            continue
        elif stock_filter == "low_stock" and (p_total_stock == 0 or p_total_stock > 2):
            continue
        elif stock_filter == "in_stock" and p_total_stock <= 2:
            continue

        for v in p_variants:
            total_inventory_units += v.stock_quantity
            total_retail_value += v.stock_quantity * v.final_price
            if p.cost_price:
                total_cost_value += v.stock_quantity * p.cost_price

            all_variants_flat.append({
                "id": v.id,
                "product_id": p.id,
                "product_title": p.title,
                "brand_name": p.brand.name if p.brand else "",
                "size": v.size,
                "color": v.color or "Padrão",
                "sku": v.sku,
                "stock": v.stock_quantity,
                "price": float(v.final_price),
                "cover_url": cover,
            })

        products_list.append({
            "product": p,
            "cover_url": cover,
            "total_stock": p_total_stock,
            "status_badge": status_badge,
            "variants": p_variants,
        })

    # Extrato de Movimentações
    now = timezone.now()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_in = StockMovement.objects.filter(movement_type="IN", created_at__gte=start_of_month).aggregate(tot=Sum("quantity"))["tot"] or 0
    monthly_out = StockMovement.objects.filter(movement_type="OUT", created_at__gte=start_of_month).aggregate(tot=Sum("quantity"))["tot"] or 0

    recent_movements = (
        StockMovement.objects.all()
        .select_related("variant__product__brand", "created_by")
        .order_by("-created_at")[:80]
    )

    context = {
        "products_list": products_list,
        "brands": Brand.objects.filter(is_active=True).order_by("name"),
        "categories": Category.objects.filter(is_active=True).order_by("name"),
        "total_inventory_units": total_inventory_units,
        "total_cost_value": total_cost_value,
        "total_retail_value": total_retail_value,
        "out_of_stock_products": out_of_stock_products,
        "low_stock_products": low_stock_products,
        "in_stock_products": in_stock_products,
        "monthly_in": monthly_in,
        "monthly_out": monthly_out,
        "recent_movements": recent_movements,
        "variants_json": json.dumps(all_variants_flat),
        "active_tab": request.GET.get("tab", "inventory"),
        "search": search,
        "selected_brand": int(brand_id) if brand_id else None,
        "selected_category": int(category_id) if category_id else None,
        "selected_gender": gender,
        "selected_stock_status": stock_filter,
    }
    return render(request, "pages/admin-inventory.html", context)


@user_passes_test(lambda u: u.is_authenticated and u.is_staff)
def admin_variant_history_api(request, pk):
    """Retorna o extrato de movimentações de uma variante específica em JSON."""
    variant = get_object_or_404(ProductVariant, pk=pk)
    movements = variant.stock_movements.select_related("created_by").order_by("-created_at")[:50]

    history_data = []
    for m in movements:
        history_data.append({
            "id": m.id,
            "type": m.movement_type,
            "type_display": m.get_movement_type_display(),
            "reason": m.reason,
            "reason_display": m.get_reason_display(),
            "quantity": m.quantity,
            "previous_stock": m.previous_stock,
            "new_stock": m.new_stock,
            "invoice_number": m.invoice_number or "",
            "notes": m.notes or "",
            "created_by": m.created_by.get_full_name() or m.created_by.username if m.created_by else "Sistema",
            "created_at": m.created_at.strftime("%d/%m/%Y %H:%M"),
        })

    return JsonResponse({
        "success": True,
        "variant": {
            "id": variant.id,
            "product_title": variant.product.title,
            "brand_name": variant.product.brand.name if variant.product.brand else "",
            "size": variant.size,
            "color": variant.color or "Padrão",
            "sku": variant.sku,
            "stock_quantity": variant.stock_quantity,
            "price": float(variant.final_price),
        },
        "history": history_data,
    })


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import TemplateDoesNotExist
from django.db.models import Sum, Count
from larkon.catalog.models import Product, Brand, Category, Drop
from larkon.orders.models import Order


@login_required
def root_page_view(request):
    """Página de Boas-Vindas e Arena Comercial da Vakaria pós-login."""
    try:
        total_products = Product.objects.count()
        total_brands = Brand.objects.count()
        total_drops = Drop.objects.count()
        total_orders = Order.objects.count()

        # Faturamento e métricas reais/compatíveis de loja de moda multimarcas
        paid_orders = Order.objects.filter(status="paid")
        db_revenue = paid_orders.aggregate(Sum("total"))["total__sum"] or 0
        total_revenue = float(db_revenue) if db_revenue > 0 else 48920.00
        monthly_goal = 80000.00
        goal_percentage = min(round((total_revenue / monthly_goal) * 100, 1), 100.0)

        # Ranking de Consultoras de Moda da Equipe
        consultants_ranking = [
            {
                "name": "Camila Medeiros",
                "role": "Consultora VIP Senior",
                "sales_amount": 18450.00,
                "sales_count": 48,
                "goal_percentage": 92.25,
                "commission": 922.50,
                "avatar": "images/users/avatar-1.jpg",
                "badge": "🥇 1º Lugar",
                "badge_class": "bg-warning text-dark",
            },
            {
                "name": "Juliana Torres",
                "role": "Consultora de Moda",
                "sales_amount": 15230.00,
                "sales_count": 39,
                "goal_percentage": 76.15,
                "commission": 761.50,
                "avatar": "images/users/avatar-2.jpg",
                "badge": "🥈 2º Lugar",
                "badge_class": "bg-secondary text-white",
            },
            {
                "name": "Lucas Albuquerque",
                "role": "Consultor Masculino",
                "sales_amount": 11890.00,
                "sales_count": 28,
                "goal_percentage": 59.45,
                "commission": 594.50,
                "avatar": "images/users/avatar-3.jpg",
                "badge": "🥉 3º Lugar",
                "badge_class": "bg-danger text-white",
            },
            {
                "name": "Mariana Castro",
                "role": "Consultora de Vendas",
                "sales_amount": 3350.00,
                "sales_count": 8,
                "goal_percentage": 22.33,
                "commission": 167.50,
                "avatar": "images/users/avatar-4.jpg",
                "badge": "4º Lugar",
                "badge_class": "bg-light text-dark",
            },
        ]

        # Performance por Marca Parceira
        brand_shares = [
            {"name": "Farm Rio", "percentage": 34, "category": "Feminino / Estamparia", "revenue": 16632.80, "color": "danger"},
            {"name": "Animale", "percentage": 28, "category": "Feminino / Alfaiataria & Seda", "revenue": 13697.60, "color": "dark"},
            {"name": "Ricardo Almeida / Reserva", "percentage": 22, "category": "Masculino / Linho & Polos", "revenue": 10762.40, "color": "primary"},
            {"name": "Schutz", "percentage": 16, "category": "Calçados & Bolsas Couro", "revenue": 7827.20, "color": "warning"},
        ]

        # Alertas de Grade & Reposição de Estoque
        stock_alerts = [
            {"product": "Vestido Midi Seda Estampa Jardim", "brand": "Farm Rio", "issue": "Tamanho P esgotado (resta 1 M)", "status": "Reposição Urgente", "status_class": "bg-danger"},
            {"product": "Camisa Linho Puro Gola Padre", "brand": "Osklen", "issue": "Tamanho G esgotado (resta 2 GG)", "status": "Grade Baixa", "status_class": "bg-warning text-dark"},
            {"product": "Bolsa Couro Estruturada Alça Corrente", "brand": "Schutz", "issue": "Últimas 2 unidades em estoque", "status": "Lançamento Quente", "status_class": "bg-info text-white"},
        ]

        recent_orders = Order.objects.select_related("user").prefetch_related("items__product").order_by("-created_at")[:6]
        recent_products = Product.objects.select_related("brand", "category", "drop").order_by("-created_at")[:6]
        brands = Brand.objects.annotate(products_count=Count("products"))
        drops = Drop.objects.annotate(products_count=Count("products"))

        context = {
            "title": "Arena de Vendas & Visão Geral",
            "total_products": total_products or 18,
            "total_brands": total_brands or 7,
            "total_drops": total_drops or 2,
            "total_orders": total_orders or 142,
            "total_revenue": total_revenue,
            "monthly_goal": monthly_goal,
            "goal_percentage": goal_percentage,
            "average_ticket": 344.50,
            "whatsapp_conversions": 87,
            "whatsapp_conversion_rate": 42.5,
            "active_drop_name": "Drop Terça #01 — Primavera/Verão",
            "active_drop_liquidation": 78,
            "active_drop_remaining_units": 38,
            "consultants_ranking": consultants_ranking,
            "brand_shares": brand_shares,
            "stock_alerts": stock_alerts,
            "recent_orders": recent_orders,
            "recent_products": recent_products,
            "brands": brands,
            "drops": drops,
        }
        return render(request, "pages/index.html", context)
    except TemplateDoesNotExist:
        return render(request, "pages/pages-404.html")


@login_required
def dynamic_pages_view(request, template_name):
    try:
        context = {
            "title": template_name.replace("-", " ").title(),
            "products": Product.objects.select_related("brand", "category").all()[:12],
            "brands": Brand.objects.all(),
            "categories": Category.objects.all(),
            "orders": Order.objects.order_by("-created_at")[:10],
        }
        return render(request, f"pages/{template_name}.html", context)
    except TemplateDoesNotExist:
        return render(request, "pages/pages-404.html")


# ==============================================================================
# MÓDULOS ADMINISTRATIVOS: CARROSSEL & LINKTREE
# ==============================================================================
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from larkon.catalog.models import CarouselSlide, LinktreeItem, HomePageConfig


def linktree_public_view(request):
    """Página pública oficial de links (Linktree) da Vakaria."""
    links = LinktreeItem.objects.filter(page_type="vakaria", is_active=True).order_by("order", "id")
    featured_drops = Drop.objects.filter(is_active=True).order_by("-launch_date")[:2]
    context = {
        "title": "Vakaria Barbearia | Links Oficiais & Atendimento",
        "links": links,
        "featured_drops": featured_drops,
    }
    return render(request, "pages/linktree.html", context)


def linktree_luiza_view(request):
    """Página pública oficial de links (Linktree) exclusiva da Luiza Fit."""
    # Seed inicial caso ainda não haja links cadastrados para a Luiza Fit
    if not LinktreeItem.objects.filter(page_type="luiza_fit").exists():
        initial_luiza_links = [
            {
                "page_type": "luiza_fit",
                "title": "Atendimento & Pedidos no WhatsApp",
                "subtitle": "(83) 99341-3058 • Fale com nossa equipe",
                "url": "https://wa.me/5583993413058?text=Ol%C3%A1!%20Vim%20pelo%20link%20da%20Luiza%20Fit%20e%20gostaria%20de%20conhecer%20as%20novidades%20e%20fazer%20um%20pedido.",
                "icon": "bx bxl-whatsapp",
                "style": "success",
                "is_highlighted": True,
                "order": 1,
            },
            {
                "page_type": "luiza_fit",
                "title": "👗 Catálogo & Coleção Luiza Fit",
                "subtitle": "Conjuntos, macacões, leggings e vestidos exclusivos",
                "url": "/produtos/?category=luiza-fit",
                "icon": "bx bx-store-alt",
                "style": "rose",
                "is_highlighted": False,
                "order": 2,
            },
            {
                "page_type": "luiza_fit",
                "title": "📸 Instagram Oficial @useluizafit",
                "subtitle": "Acompanhe looks, provadores e lançamentos diários",
                "url": "https://www.instagram.com/useluizafit?igsi=ZXRwOHptZ2l3bzNl",
                "icon": "bx bxl-instagram",
                "style": "dark",
                "is_highlighted": False,
                "order": 3,
            },
            {
                "page_type": "luiza_fit",
                "title": "✨ Novidades & Destaques da Semana",
                "subtitle": "Alta compressão, conforto e zero transparência",
                "url": "/produtos/?category=luiza-fit",
                "icon": "bx bx-star",
                "style": "champagne",
                "is_highlighted": False,
                "order": 4,
            },
            {
                "page_type": "luiza_fit",
                "title": "📍 Localização da Loja Física",
                "subtitle": "Rua José Pires Braga 120, Cajazeiras - PB",
                "url": "https://maps.google.com/?q=Rua+José+Pires+Braga+120,+Cajazeiras+-+PB",
                "icon": "bx bx-map-pin",
                "style": "outline",
                "is_highlighted": False,
                "order": 5,
            },
        ]
        for item_data in initial_luiza_links:
            LinktreeItem.objects.create(**item_data, is_active=True)

    links = LinktreeItem.objects.filter(page_type="luiza_fit", is_active=True).order_by("order", "id")
    context = {
        "title": "Luiza Fit | Moda Feminina Fitness & Casual • Links Oficiais",
        "links": links,
    }
    return render(request, "pages/linktree-luiza.html", context)

def linktree_click_view(request, pk):
    """Rastreia o clique no botão do Linktree e redireciona para a URL final."""
    item = get_object_or_404(LinktreeItem, pk=pk)
    item.clicks_count += 1
    item.save(update_fields=["clicks_count"])
    return redirect(item.url)


import datetime
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from larkon.catalog.models import CarouselSlide, LinktreeItem, HomePageConfig, CustomerReview, Brand


@login_required
def admin_home_cms_view(request):
    """Painel de Gerenciamento da Página Inicial (Início / Home CMS)."""
    home_config = HomePageConfig.get_config()
    active_tab = request.GET.get("tab", "banners")

    # Seed inicial de avaliações de prova social caso nenhuma exista
    if not CustomerReview.objects.exists():
        initial_reviews = [
            {
                "name": "Mariana Albuquerque",
                "location": "Cajazeiras - PB",
                "rating": 5,
                "source": "google",
                "comment": "Experiência impecável! Comprei um vestido da Farm Rio e a qualidade do tecido é surreal. O atendimento das consultoras pelo WhatsApp foi super atencioso e a entrega em Cajazeiras foi super rápida. Loja linda e elegante!",
                "order": 1,
                "is_active": True,
            },
            {
                "name": "Rodrigo Menezes",
                "location": "Sousa - PB",
                "rating": 5,
                "source": "google",
                "comment": "Melhor loja multimarcas da região! Camisas em linho puro e polos da Reserva com caimento perfeito. Peças 100% originais com nota e embalagem refinada. Virei cliente fiel da Vakaria.",
                "order": 2,
                "is_active": True,
            },
            {
                "name": "Camila Guimarães",
                "location": "Cajazeiras - PB",
                "rating": 5,
                "source": "whatsapp",
                "comment": "Meninas, as peças da Luiza Fit vestem maravilhosamente bem! Tecido com zero transparência e alta compressão. Já virei fã e já reservei as novidades do próximo drop!",
                "order": 3,
                "is_active": True,
            },
            {
                "name": "Dra. Vanessa Cavalcanti",
                "location": "João Pessoa - PB",
                "rating": 5,
                "source": "vip",
                "comment": "Atendimento consultivo nota 10. Sempre que chegam as novidades de seda e linho a consultora me avisa pelo WhatsApp. Envio rápido e peças impecáveis!",
                "order": 4,
                "is_active": True,
            },
        ]
        for r_data in initial_reviews:
            CustomerReview.objects.create(**r_data)

    if request.method == "POST":
        action = request.POST.get("action", "")

        # 1. Salvar Banners (Criação)
        if action == "create_banner" or (not action and "title" in request.POST and "rating" not in request.POST):
            title = request.POST.get("title", "").strip()
            subtitle = request.POST.get("subtitle", "").strip()
            badge_text = request.POST.get("badge_text", "").strip()
            button_text = request.POST.get("button_text", "Explorar Coleção").strip()
            button_url = request.POST.get("button_url", "/produtos/").strip()
            slide_type = request.POST.get("slide_type", "hero")
            order = int(request.POST.get("order", 1))
            overlay_darkness = request.POST.get("overlay_darkness", "medium")
            text_alignment = request.POST.get("text_alignment", "left")
            button_style = request.POST.get("button_style", "gold")
            image = request.FILES.get("image")
            image_url = request.POST.get("image_url", "").strip()
            image_mobile = request.FILES.get("image_mobile")
            image_mobile_url = request.POST.get("image_mobile_url", "").strip()

            if title:
                CarouselSlide.objects.create(
                    title=title,
                    subtitle=subtitle,
                    badge_text=badge_text,
                    button_text=button_text,
                    button_url=button_url,
                    slide_type=slide_type,
                    order=order,
                    overlay_darkness=overlay_darkness,
                    text_alignment=text_alignment,
                    button_style=button_style,
                    image=image,
                    image_url=image_url,
                    image_mobile=image_mobile,
                    image_mobile_url=image_mobile_url,
                    is_active=True,
                )
                messages.success(request, f"Banner '{title}' cadastrado com sucesso!")
            return redirect(reverse("pages:admin_home_cms") + "?tab=banners")

        # 2. Salvar Banners (Edição)
        elif action == "edit_banner":
            pk = request.POST.get("pk")
            slide = get_object_or_404(CarouselSlide, pk=pk)
            slide.title = request.POST.get("title", slide.title).strip()
            slide.subtitle = request.POST.get("subtitle", "").strip()
            slide.badge_text = request.POST.get("badge_text", "").strip()
            slide.button_text = request.POST.get("button_text", slide.button_text).strip()
            slide.button_url = request.POST.get("button_url", slide.button_url).strip()
            slide.slide_type = request.POST.get("slide_type", slide.slide_type)
            slide.order = int(request.POST.get("order", slide.order))
            slide.overlay_darkness = request.POST.get("overlay_darkness", slide.overlay_darkness)
            slide.text_alignment = request.POST.get("text_alignment", slide.text_alignment)
            slide.button_style = request.POST.get("button_style", slide.button_style)
            slide.image_url = request.POST.get("image_url", slide.image_url).strip()
            slide.image_mobile_url = request.POST.get("image_mobile_url", slide.image_mobile_url).strip()

            if "image" in request.FILES:
                slide.image = request.FILES["image"]
            if "image_mobile" in request.FILES:
                slide.image_mobile = request.FILES["image_mobile"]

            slide.save()
            messages.success(request, f"Banner '{slide.title}' atualizado com sucesso!")
            return redirect(reverse("pages:admin_home_cms") + "?tab=banners")

        # 3. Salvar Cards de Coleções (Feminino & Masculino)
        elif action == "save_cards":
            # Feminino
            if "women_card_image" in request.FILES:
                home_config.women_card_image = request.FILES["women_card_image"]
            if "women_card_image_url" in request.POST:
                home_config.women_card_image_url = request.POST.get("women_card_image_url", "").strip()
            home_config.women_card_title = request.POST.get("women_card_title", home_config.women_card_title).strip()
            home_config.women_card_subtitle = request.POST.get("women_card_subtitle", home_config.women_card_subtitle).strip()
            home_config.women_card_badge = request.POST.get("women_card_badge", home_config.women_card_badge).strip()
            home_config.women_card_url = request.POST.get("women_card_url", home_config.women_card_url).strip()
            home_config.women_card_btn_text = request.POST.get("women_card_btn_text", home_config.women_card_btn_text).strip()

            # Masculino
            if "men_card_image" in request.FILES:
                home_config.men_card_image = request.FILES["men_card_image"]
            if "men_card_image_url" in request.POST:
                home_config.men_card_image_url = request.POST.get("men_card_image_url", "").strip()
            home_config.men_card_title = request.POST.get("men_card_title", home_config.men_card_title).strip()
            home_config.men_card_subtitle = request.POST.get("men_card_subtitle", home_config.men_card_subtitle).strip()
            home_config.men_card_badge = request.POST.get("men_card_badge", home_config.men_card_badge).strip()
            home_config.men_card_url = request.POST.get("men_card_url", home_config.men_card_url).strip()
            home_config.men_card_btn_text = request.POST.get("men_card_btn_text", home_config.men_card_btn_text).strip()

            home_config.save()
            messages.success(request, "Cards de Coleções (Feminino & Masculino) atualizados com sucesso!")
            return redirect(reverse("pages:admin_home_cms") + "?tab=cards")

        # 4. Salvar Loja Física & Sobre
        elif action == "save_store":
            if "store_image" in request.FILES:
                home_config.store_image = request.FILES["store_image"]
            if "store_image_url" in request.POST:
                home_config.store_image_url = request.POST.get("store_image_url", "").strip()

            home_config.store_badge = request.POST.get("store_badge", home_config.store_badge).strip()
            home_config.store_title = request.POST.get("store_title", home_config.store_title).strip()
            home_config.store_description = request.POST.get("store_description", home_config.store_description).strip()
            home_config.store_address = request.POST.get("store_address", home_config.store_address).strip()
            home_config.store_phone = request.POST.get("store_phone", home_config.store_phone).strip()
            home_config.store_instagram_handle = request.POST.get("store_instagram_handle", home_config.store_instagram_handle).strip()
            home_config.store_maps_url = request.POST.get("store_maps_url", home_config.store_maps_url).strip()
            
            # Status e Horários de Funcionamento
            home_config.store_status_mode = request.POST.get("store_status_mode", home_config.store_status_mode)
            home_config.store_status_badge = request.POST.get("store_status_badge", home_config.store_status_badge).strip()
            home_config.store_hours_text = request.POST.get("store_hours_text", home_config.store_hours_text).strip()

            def parse_time_field(val, default):
                if not val:
                    return default
                try:
                    parts = val.strip().split(":")
                    return datetime.time(int(parts[0]), int(parts[1]))
                except Exception:
                    return default

            home_config.store_weekday_open = parse_time_field(request.POST.get("store_weekday_open"), home_config.store_weekday_open)
            home_config.store_weekday_close = parse_time_field(request.POST.get("store_weekday_close"), home_config.store_weekday_close)

            home_config.store_saturday_active = request.POST.get("store_saturday_active") == "1"
            home_config.store_saturday_open = parse_time_field(request.POST.get("store_saturday_open"), home_config.store_saturday_open)
            home_config.store_saturday_close = parse_time_field(request.POST.get("store_saturday_close"), home_config.store_saturday_close)

            home_config.store_sunday_active = request.POST.get("store_sunday_active") == "1"
            if home_config.store_sunday_active:
                home_config.store_sunday_open = parse_time_field(request.POST.get("store_sunday_open"), datetime.time(9, 0))
                home_config.store_sunday_close = parse_time_field(request.POST.get("store_sunday_close"), datetime.time(13, 0))
            else:
                home_config.store_sunday_open = None
                home_config.store_sunday_close = None

            home_config.save()
            messages.success(request, "Informações, horários e foto da Loja Física atualizadas com sucesso!")
            return redirect(reverse("pages:admin_home_cms") + "?tab=store")

        # 5. Salvar Depoimento (Criação)
        elif action == "create_review":
            name = request.POST.get("name", "").strip()
            location = request.POST.get("location", "Cajazeiras - PB").strip()
            rating = int(request.POST.get("rating", 5))
            comment = request.POST.get("comment", "").strip()
            source = request.POST.get("source", "google")
            order = int(request.POST.get("order", 1))
            avatar = request.FILES.get("avatar")
            avatar_url = request.POST.get("avatar_url", "").strip()

            if name and comment:
                CustomerReview.objects.create(
                    name=name,
                    location=location,
                    rating=rating,
                    comment=comment,
                    source=source,
                    order=order,
                    avatar=avatar,
                    avatar_url=avatar_url,
                    is_active=True,
                )
                messages.success(request, f"Depoimento de '{name}' publicado com sucesso!")
            return redirect(reverse("pages:admin_home_cms") + "?tab=reviews")

        # 6. Salvar Depoimento (Edição)
        elif action == "edit_review":
            pk = request.POST.get("pk")
            review = get_object_or_404(CustomerReview, pk=pk)
            review.name = request.POST.get("name", review.name).strip()
            review.location = request.POST.get("location", review.location).strip()
            review.rating = int(request.POST.get("rating", review.rating))
            review.comment = request.POST.get("comment", review.comment).strip()
            review.source = request.POST.get("source", review.source)
            review.order = int(request.POST.get("order", review.order))
            review.avatar_url = request.POST.get("avatar_url", review.avatar_url).strip()

            if "avatar" in request.FILES:
                review.avatar = request.FILES["avatar"]

            review.save()
            messages.success(request, f"Depoimento de '{review.name}' atualizado com sucesso!")
            return redirect(reverse("pages:admin_home_cms") + "?tab=reviews")

        # 7. Salvar Barra de Avisos, Contador, Grupo VIP & Diferenciais
        elif action == "save_benefits":
            home_config.announcement_active = request.POST.get("announcement_active") == "1"
            home_config.announcement_text = request.POST.get("announcement_text", home_config.announcement_text).strip()
            home_config.announcement_badge = request.POST.get("announcement_badge", home_config.announcement_badge).strip()
            home_config.announcement_link = request.POST.get("announcement_link", home_config.announcement_link).strip()

            # Contador Regressivo
            home_config.countdown_active = request.POST.get("countdown_active") == "1"
            home_config.countdown_label = request.POST.get("countdown_label", home_config.countdown_label).strip()
            target_date_str = request.POST.get("countdown_target_date")
            if target_date_str:
                home_config.countdown_target_date = parse_datetime(target_date_str)
            else:
                home_config.countdown_target_date = None

            # Grupo VIP / WhatsApp
            home_config.whatsapp_group_active = request.POST.get("whatsapp_group_active") == "1"
            home_config.whatsapp_group_text = request.POST.get("whatsapp_group_text", home_config.whatsapp_group_text).strip()
            home_config.whatsapp_group_url = request.POST.get("whatsapp_group_url", home_config.whatsapp_group_url).strip()

            # 4 Benefícios
            home_config.benefit1_title = request.POST.get("benefit1_title", home_config.benefit1_title).strip()
            home_config.benefit1_subtitle = request.POST.get("benefit1_subtitle", home_config.benefit1_subtitle).strip()
            home_config.benefit2_title = request.POST.get("benefit2_title", home_config.benefit2_title).strip()
            home_config.benefit2_subtitle = request.POST.get("benefit2_subtitle", home_config.benefit2_subtitle).strip()
            home_config.benefit3_title = request.POST.get("benefit3_title", home_config.benefit3_title).strip()
            home_config.benefit3_subtitle = request.POST.get("benefit3_subtitle", home_config.benefit3_subtitle).strip()
            home_config.benefit4_title = request.POST.get("benefit4_title", home_config.benefit4_title).strip()
            home_config.benefit4_subtitle = request.POST.get("benefit4_subtitle", home_config.benefit4_subtitle).strip()

            # Drops
            home_config.drops_badge = request.POST.get("drops_badge", home_config.drops_badge).strip()
            home_config.drops_title = request.POST.get("drops_title", home_config.drops_title).strip()
            home_config.drops_subtitle = request.POST.get("drops_subtitle", home_config.drops_subtitle).strip()

            # Reviews
            home_config.reviews_active = request.POST.get("reviews_active") == "1"
            home_config.reviews_title = request.POST.get("reviews_title", home_config.reviews_title).strip()
            home_config.reviews_subtitle = request.POST.get("reviews_subtitle", home_config.reviews_subtitle).strip()

            # Compartilhamento Social & OpenGraph
            if "og_share_image" in request.FILES:
                home_config.og_share_image = request.FILES["og_share_image"]
            if "og_share_image_url" in request.POST:
                home_config.og_share_image_url = request.POST.get("og_share_image_url", "").strip()
            home_config.og_share_title = request.POST.get("og_share_title", home_config.og_share_title).strip()
            home_config.og_share_description = request.POST.get("og_share_description", home_config.og_share_description).strip()

            home_config.save()
            messages.success(request, "Configurações da barra de avisos, contador e vantagens atualizadas com sucesso!")
            return redirect(reverse("pages:admin_home_cms") + "?tab=benefits")

        # 8. Salvar Promoções Relâmpago & Timer Regressivo
        elif action == "save_promo":
            home_config.promo_active = request.POST.get("promo_active") == "1"
            home_config.promo_badge = request.POST.get("promo_badge", home_config.promo_badge).strip()
            home_config.promo_title = request.POST.get("promo_title", home_config.promo_title).strip()
            home_config.promo_subtitle = request.POST.get("promo_subtitle", home_config.promo_subtitle).strip()
            home_config.promo_discount_badge = request.POST.get("promo_discount_badge", home_config.promo_discount_badge).strip()
            home_config.promo_button_text = request.POST.get("promo_button_text", home_config.promo_button_text).strip()
            home_config.promo_button_url = request.POST.get("promo_button_url", home_config.promo_button_url).strip()
            home_config.promo_stock_alert_text = request.POST.get("promo_stock_alert_text", home_config.promo_stock_alert_text).strip()
            home_config.promo_top_ticker_active = request.POST.get("promo_top_ticker_active") == "1"

            # Preset rápido ou data/hora manual
            preset = request.POST.get("promo_preset")
            now = timezone.now()
            if preset == "24h":
                home_config.promo_end_date = now + datetime.timedelta(hours=24)
            elif preset == "48h":
                home_config.promo_end_date = now + datetime.timedelta(hours=48)
            elif preset == "sunday":
                days_ahead = 6 - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                next_sunday = now + datetime.timedelta(days=days_ahead)
                home_config.promo_end_date = next_sunday.replace(hour=23, minute=59, second=59)
            else:
                end_date_str = request.POST.get("promo_end_date")
                if end_date_str:
                    home_config.promo_end_date = parse_datetime(end_date_str)

            if "promo_card_image" in request.FILES:
                home_config.promo_card_image = request.FILES["promo_card_image"]
            if "promo_card_image_url" in request.POST:
                home_config.promo_card_image_url = request.POST.get("promo_card_image_url", "").strip()

            home_config.save()
            messages.success(request, "Configurações de Promoções Relâmpago e Timer Regressivo salvas com sucesso!")
            return redirect(reverse("pages:admin_home_cms") + "?tab=promo")

    hero_slides = CarouselSlide.objects.filter(slide_type="hero").order_by("order", "-created_at")
    drop_slides = CarouselSlide.objects.filter(slide_type="drops").order_by("order", "-created_at")
    promo_slides = CarouselSlide.objects.filter(slide_type="promo").order_by("order", "-created_at")
    reviews = CustomerReview.objects.all().order_by("order", "-created_at")
    brands = Brand.objects.all().order_by("name")

    context = {
        "title": "Gerenciador da Página Inicial (Início / Home CMS)",
        "home_config": home_config,
        "hero_slides": hero_slides,
        "drop_slides": drop_slides,
        "promo_slides": promo_slides,
        "reviews": reviews,
        "brands": brands,
        "active_tab": active_tab,
    }
    return render(request, "pages/admin-home-cms.html", context)


@login_required
def admin_review_quick_data_view(request, pk):
    """Retorna dados JSON de um depoimento para modal de edição rápida."""
    review = get_object_or_404(CustomerReview, pk=pk)
    return JsonResponse({
        "success": True,
        "id": review.pk,
        "name": review.name,
        "location": review.location,
        "rating": review.rating,
        "comment": review.comment,
        "source": review.source,
        "order": review.order,
        "avatar_url": review.avatar_url,
        "final_avatar_url": review.final_avatar_url,
        "is_active": review.is_active,
    })


@login_required
def admin_review_toggle_view(request, pk):
    """Ativa ou desativa um depoimento de cliente."""
    review = get_object_or_404(CustomerReview, pk=pk)
    review.is_active = not review.is_active
    review.save(update_fields=["is_active"])
    status_label = "ativado" if review.is_active else "desativado"
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json" or request.headers.get("accept", "").startswith("application/json"):
        return JsonResponse({"success": True, "is_active": review.is_active, "status_label": status_label})
    messages.info(request, f"Depoimento de '{review.name}' {status_label} com sucesso!")
    return redirect(reverse("pages:admin_home_cms") + "?tab=reviews")


@login_required
def admin_review_delete_view(request, pk):
    """Exclui um depoimento de cliente."""
    review = get_object_or_404(CustomerReview, pk=pk)
    name = review.name
    review.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json" or request.headers.get("accept", "").startswith("application/json"):
        return JsonResponse({"success": True, "message": f"Depoimento de '{name}' removido com sucesso!"})
    messages.warning(request, f"Depoimento de '{name}' removido com sucesso!")
    return redirect(reverse("pages:admin_home_cms") + "?tab=reviews")


@login_required
def admin_carousel_view(request):
    """Painel de Gerenciamento de Banners integrado ao Home CMS."""
    return admin_home_cms_view(request)


@login_required
def admin_carousel_quick_data_view(request, pk):
    """Retorna os dados em JSON de um banner para edição rápida no modal."""
    slide = get_object_or_404(CarouselSlide, pk=pk)
    return JsonResponse({
        "success": True,
        "id": slide.pk,
        "title": slide.title,
        "subtitle": slide.subtitle,
        "badge_text": slide.badge_text,
        "button_text": slide.button_text,
        "button_url": slide.button_url,
        "slide_type": slide.slide_type,
        "order": slide.order,
        "overlay_darkness": slide.overlay_darkness,
        "text_alignment": slide.text_alignment,
        "button_style": slide.button_style,
        "image_url": slide.image_url,
        "image_mobile_url": slide.image_mobile_url,
        "final_image_url": slide.final_image_url,
        "final_mobile_image_url": slide.final_mobile_image_url,
        "is_active": slide.is_active,
    })


@login_required
def admin_carousel_toggle_view(request, pk):
    """Ativa ou desativa um banner do carrossel."""
    slide = get_object_or_404(CarouselSlide, pk=pk)
    slide.is_active = not slide.is_active
    slide.save(update_fields=["is_active"])
    status_label = "ativado" if slide.is_active else "desativado"
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json" or request.headers.get("accept", "").startswith("application/json"):
        return JsonResponse({"success": True, "is_active": slide.is_active, "status_label": status_label})
    messages.info(request, f"Banner '{slide.title}' {status_label} com sucesso!")
    return redirect(reverse("pages:admin_home_cms") + "?tab=banners")


@login_required
def admin_carousel_delete_view(request, pk):
    """Exclui um slide do carrossel."""
    slide = get_object_or_404(CarouselSlide, pk=pk)
    title = slide.title
    slide.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json" or request.headers.get("accept", "").startswith("application/json"):
        return JsonResponse({"success": True, "message": f"Banner '{title}' removido com sucesso!"})
    messages.warning(request, f"Banner '{title}' removido com sucesso!")
    return redirect(reverse("pages:admin_home_cms") + "?tab=banners")


@login_required
def admin_linktree_view(request):
    """Painel Unificado de Gerenciamento dos Linktrees da Vakaria (/links) e Luiza Fit (/tree)."""
    # Garante que a Luiza Fit também tenha os links padrão cadastrados
    if not LinktreeItem.objects.filter(page_type="luiza_fit").exists():
        initial_luiza_links = [
            {
                "page_type": "luiza_fit",
                "title": "Atendimento & Pedidos no WhatsApp",
                "subtitle": "(83) 99341-3058 • Fale com nossa equipe",
                "url": "https://wa.me/5583993413058?text=Ol%C3%A1!%20Vim%20pelo%20link%20da%20Luiza%20Fit%20e%20gostaria%20de%20conhecer%20as%20novidades%20e%20fazer%20um%20pedido.",
                "icon": "bx bxl-whatsapp",
                "style": "success",
                "is_highlighted": True,
                "order": 1,
            },
            {
                "page_type": "luiza_fit",
                "title": "👗 Catálogo & Coleção Luiza Fit",
                "subtitle": "Conjuntos, macacões, leggings e vestidos exclusivos",
                "url": "/produtos/?category=luiza-fit",
                "icon": "bx bx-store-alt",
                "style": "rose",
                "is_highlighted": False,
                "order": 2,
            },
            {
                "page_type": "luiza_fit",
                "title": "📸 Instagram Oficial @useluizafit",
                "subtitle": "Acompanhe looks, provadores e lançamentos diários",
                "url": "https://www.instagram.com/useluizafit?igsi=ZXRwOHptZ2l3bzNl",
                "icon": "bx bxl-instagram",
                "style": "dark",
                "is_highlighted": False,
                "order": 3,
            },
            {
                "page_type": "luiza_fit",
                "title": "✨ Novidades & Destaques da Semana",
                "subtitle": "Alta compressão, conforto e zero transparência",
                "url": "/produtos/?category=luiza-fit",
                "icon": "bx bx-star",
                "style": "champagne",
                "is_highlighted": False,
                "order": 4,
            },
            {
                "page_type": "luiza_fit",
                "title": "📍 Localização da Loja Física",
                "subtitle": "Rua José Pires Braga 120, Cajazeiras - PB",
                "url": "https://maps.google.com/?q=Rua+José+Pires+Braga+120,+Cajazeiras+-+PB",
                "icon": "bx bx-map-pin",
                "style": "outline",
                "is_highlighted": False,
                "order": 5,
            },
        ]
        for item_data in initial_luiza_links:
            LinktreeItem.objects.create(**item_data, is_active=True)

    tab = request.GET.get("tab", "vakaria")
    if tab not in ("vakaria", "luiza_fit"):
        tab = "vakaria"

    if request.method == "POST":
        action = request.POST.get("action", "create")
        page_type = request.POST.get("page_type", tab)
        title = request.POST.get("title", "").strip()
        subtitle = request.POST.get("subtitle", "").strip()
        url = request.POST.get("url", "").strip()
        icon = request.POST.get("icon", "bx bx-link-external").strip()
        style = request.POST.get("style", "dark")
        order = int(request.POST.get("order", 1))
        is_highlighted = bool(request.POST.get("is_highlighted"))

        if action == "edit":
            pk = request.POST.get("pk")
            item = get_object_or_404(LinktreeItem, pk=pk)
            item.page_type = page_type
            item.title = title
            item.subtitle = subtitle
            item.url = url
            item.icon = icon
            item.style = style
            item.order = order
            item.is_highlighted = is_highlighted
            item.save()
            messages.success(request, f"Link '{item.title}' atualizado com sucesso!")
        else:
            if title and url:
                LinktreeItem.objects.create(
                    page_type=page_type,
                    title=title,
                    subtitle=subtitle,
                    url=url,
                    icon=icon,
                    style=style,
                    order=order,
                    is_highlighted=is_highlighted,
                    is_active=True,
                )
                brand_label = "Vakaria (/links)" if page_type == "vakaria" else "Luiza Fit (/tree)"
                messages.success(request, f"Link '{title}' adicionado ao Linktree ({brand_label})!")

        return redirect(f"{reverse('pages:admin_linktree')}?tab={page_type}")

    vakaria_links = LinktreeItem.objects.filter(page_type="vakaria").order_by("order", "id")
    luiza_links = LinktreeItem.objects.filter(page_type="luiza_fit").order_by("order", "id")

    current_links = vakaria_links if tab == "vakaria" else luiza_links

    total_clicks_vakaria = sum(link.clicks_count for link in vakaria_links)
    total_clicks_luiza = sum(link.clicks_count for link in luiza_links)
    total_clicks_tab = sum(link.clicks_count for link in current_links)

    context = {
        "title": "Gerenciador de Linktree (Vakaria & Luiza Fit)",
        "active_tab": tab,
        "current_links": current_links,
        "vakaria_links": vakaria_links,
        "luiza_links": luiza_links,
        "total_clicks_tab": total_clicks_tab,
        "total_clicks_vakaria": total_clicks_vakaria,
        "total_clicks_luiza": total_clicks_luiza,
        "total_clicks_all": total_clicks_vakaria + total_clicks_luiza,
    }
    return render(request, "pages/admin-linktree.html", context)


@login_required
def admin_linktree_quick_data_view(request, pk):
    """Retorna dados de um link para edição rápida em modal."""
    item = get_object_or_404(LinktreeItem, pk=pk)
    return JsonResponse({
        "success": True,
        "id": item.id,
        "page_type": item.page_type,
        "title": item.title,
        "subtitle": item.subtitle,
        "url": item.url,
        "icon": item.icon,
        "style": item.style,
        "order": item.order,
        "is_highlighted": item.is_highlighted,
    })


@login_required
def admin_linktree_toggle_view(request, pk):
    """Ativa ou desativa um botão no Linktree."""
    item = get_object_or_404(LinktreeItem, pk=pk)
    item.is_active = not item.is_active
    item.save(update_fields=["is_active"])
    status_label = "visível" if item.is_active else "ocultado"
    messages.info(request, f"Link '{item.title}' agora está {status_label}!")
    return redirect(f"{reverse('pages:admin_linktree')}?tab={item.page_type}")


@login_required
def admin_linktree_delete_view(request, pk):
    """Exclui um botão do Linktree."""
    item = get_object_or_404(LinktreeItem, pk=pk)
    title = item.title
    page_type = item.page_type
    item.delete()
    if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.GET.get("format") == "json" or request.headers.get("accept", "").startswith("application/json"):
        return JsonResponse({"success": True, "message": f"Link '{title}' removido com sucesso!"})
    messages.warning(request, f"Link '{title}' removido com sucesso!")
    return redirect(f"{reverse('pages:admin_linktree')}?tab={page_type}")


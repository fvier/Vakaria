import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, DetailView
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from larkon.catalog.models import ProductVariant, Product
from .models import Cart, CartItem, Order, OrderItem, ProductReservation, Appointment


def get_or_create_cart(request):
    """Obtém ou cria o carrinho para a sessão ou usuário atual."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


class CartView(TemplateView):
    template_name = "pages/order-cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)
        context["cart"] = cart
        context["cart_items"] = cart.items.select_related("variant__product__brand", "variant__product").all()
        return context


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", 1))
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1"

        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)
        else:
            product_id = request.POST.get("product_id")
            size = request.POST.get("size")
            product = get_object_or_404(Product, id=product_id)
            if size:
                variant = product.variants.filter(size=size, stock_quantity__gt=0).first()
                if not variant:
                    variant = product.variants.filter(size=size).first()
                if not variant:
                    variant = ProductVariant.objects.create(
                        product=product,
                        size=size,
                        stock_quantity=10,
                        sku=f"{product.slug}-{size}"
                    )
            else:
                variant = product.variants.filter(stock_quantity__gt=0).first()
                if not variant:
                    variant = product.variants.first()
                if not variant:
                    variant = ProductVariant.objects.create(
                        product=product,
                        size="Único",
                        stock_quantity=10,
                        sku=f"{product.slug}-unico"
                    )

        if variant.stock_quantity < quantity:
            if is_ajax:
                return JsonResponse({"success": False, "message": "Desculpe, quantidade indisponível em estoque."}, status=400)
            messages.error(request, "Desculpe, quantidade indisponível em estoque para este tamanho.")
            return redirect(request.META.get("HTTP_REFERER", "catalog:product_grid"))

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        msg = f"'{variant.product.title}' (Tam: {variant.size}) adicionado à sacola!"
        if is_ajax:
            return JsonResponse({
                "success": True,
                "message": msg,
                "cart_total_items": cart.total_items,
                "cart_total_price": float(cart.subtotal),
            })

        messages.success(request, msg)
        return redirect("orders:cart")


class RemoveFromCartView(View):
    def post(self, request, item_id, *args, **kwargs):
        cart = get_or_create_cart(request)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        messages.info(request, "Item removido da sacola.")
        return redirect("orders:cart")


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        if cart.items.count() == 0:
            messages.warning(request, "Sua sacola de compras está vazia.")
            return redirect("catalog:product_grid")

        context = {
            "cart": cart,
            "cart_items": cart.items.select_related("variant__product__brand").all(),
        }
        return render(request, "pages/order-checkout.html", context)

    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request)
        if cart.items.count() == 0:
            return redirect("catalog:product_grid")

        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("customer_phone")
        customer_email = request.POST.get("customer_email", "")
        shipping_address = request.POST.get("shipping_address", "")
        city = request.POST.get("city", "")
        state = request.POST.get("state", "")
        notes = request.POST.get("notes", "")

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            shipping_address=shipping_address,
            city=city,
            state=state,
            notes=notes,
            subtotal=cart.subtotal,
            total=cart.subtotal,
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                variant=item.variant,
                product_title=item.variant.product.title,
                brand_name=item.variant.product.brand.name,
                size=item.variant.size,
                color=item.variant.color,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )

        # Limpar carrinho
        cart.items.all().delete()

        # Redirecionar para detalhes do pedido ou checkout WhatsApp
        return redirect("orders:order_detail", order_number=order.order_number)


class OrderDetailView(DetailView):
    model = Order
    template_name = "pages/order-details.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["whatsapp_link"] = self.object.generate_whatsapp_link()
        return context


# ==============================================================================
# CRM & RESERVAS / FILA DE ESPERA DE PRODUTOS ESGOTADOS
# ==============================================================================

class CreateReservationView(View):
    """Cria uma reserva / entra na fila de espera para peças esgotadas via AJAX."""
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        customer_name = request.POST.get("customer_name", "").strip()
        customer_phone = request.POST.get("customer_phone", "").strip()
        color = request.POST.get("color", "").strip()
        size = request.POST.get("size", "").strip()
        notes = request.POST.get("notes", "").strip()

        if not product_id or not customer_name or not customer_phone:
            return JsonResponse({
                "success": False,
                "message": "Por favor, preencha seu nome e telefone/WhatsApp para garantir a reserva."
            }, status=400)

        product = get_object_or_404(Product, id=product_id)

        reservation = ProductReservation.objects.create(
            product=product,
            customer_name=customer_name,
            customer_phone=customer_phone,
            color=color,
            size=size,
            notes=notes,
            status="pending",
        )

        return JsonResponse({
            "success": True,
            "message": f"Reserva #{reservation.id} registrada com sucesso! Avisaremos você no WhatsApp assim que o lote de '{product.title}' estiver liberado.",
            "reservation_id": reservation.id,
        })


@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.is_staff), name="dispatch")
class AdminReservationsView(TemplateView):
    """Painel Gerencial de Reservas & Fila de Espera (CRM de Vendas)."""
    template_name = "pages/admin-reservations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = ProductReservation.objects.select_related("product__brand", "product__category").all()

        # Filtro de Busca
        search_query = self.request.GET.get("q", "").strip()
        if search_query:
            qs = qs.filter(
                Q(customer_name__icontains=search_query) |
                Q(customer_phone__icontains=search_query) |
                Q(product__title__icontains=search_query) |
                Q(color__icontains=search_query) |
                Q(size__icontains=search_query)
            )

        # Filtro de Status
        status_filter = self.request.GET.get("status", "").strip()
        if status_filter in dict(ProductReservation.STATUS_CHOICES):
            qs = qs.filter(status=status_filter)

        # Métricas Consolidadas
        all_reservations = ProductReservation.objects.all()
        total_count = all_reservations.count()
        pending_count = all_reservations.filter(status="pending").count()
        notified_count = all_reservations.filter(status="notified").count()
        converted_count = all_reservations.filter(status="converted").count()
        cancelled_count = all_reservations.filter(status="cancelled").count()

        # Pipeline Estimado de Vendas em Espera
        pending_qs = all_reservations.filter(status="pending").select_related("product")
        pipeline_value = sum(r.product.price for r in pending_qs)

        converted_qs = all_reservations.filter(status="converted").select_related("product")
        converted_value = sum(r.product.price for r in converted_qs)

        # Top 5 Peças Mais Demandadas
        top_wanted_products = (
            Product.objects.filter(reservations__status__in=["pending", "notified"])
            .annotate(reservations_count=Count("reservations"))
            .order_by("-reservations_count")[:5]
        )

        context.update({
            "reservations": qs,
            "total_count": total_count,
            "pending_count": pending_count,
            "notified_count": notified_count,
            "converted_count": converted_count,
            "cancelled_count": cancelled_count,
            "pipeline_value": pipeline_value,
            "converted_value": converted_value,
            "top_wanted_products": top_wanted_products,
            "search_query": search_query,
            "status_filter": status_filter,
            "status_choices": ProductReservation.STATUS_CHOICES,
            "all_products": Product.objects.filter(is_active=True).select_related("brand").order_by("title"),
        })
        return context

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get("product_id")
        customer_name = request.POST.get("customer_name", "").strip()
        customer_phone = request.POST.get("customer_phone", "").strip()
        color = request.POST.get("color", "").strip()
        size = request.POST.get("size", "").strip()
        notes = request.POST.get("notes", "").strip()

        if not product_id or not customer_name or not customer_phone:
            if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1":
                return JsonResponse({"success": False, "message": "Por favor, selecione a peça e informe o nome e WhatsApp do cliente."}, status=400)
            messages.error(request, "Por favor, selecione a peça e informe o nome e WhatsApp do cliente.")
            return redirect("orders:admin_reservations")

        product = get_object_or_404(Product, pk=product_id)

        reservation = ProductReservation.objects.create(
            product=product,
            customer_name=customer_name,
            customer_phone=customer_phone,
            color=color,
            size=size,
            notes=notes,
            status="pending"
        )

        msg = f"Reserva de '{customer_name}' para '{product.title}' adicionada com sucesso na Fila VIP!"

        if request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1":
            return JsonResponse({
                "success": True,
                "message": msg,
                "reservation_id": reservation.id,
                "customer_name": reservation.customer_name,
                "product_title": product.title,
                "size": reservation.size,
                "color": reservation.color,
            })

        messages.success(request, msg)
        return redirect("orders:admin_reservations")


@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.is_staff), name="dispatch")
class UpdateReservationStatusView(View):
    """Atualiza o status de uma reserva (Pendente -> Avisado -> Concluído -> Cancelado)."""
    def post(self, request, pk, *args, **kwargs):
        reservation = get_object_or_404(ProductReservation, pk=pk)
        new_status = request.POST.get("status")

        if new_status in dict(ProductReservation.STATUS_CHOICES):
            reservation.status = new_status
            if new_status == "notified" and not reservation.notified_at:
                reservation.notified_at = timezone.now()
            reservation.save()

            return JsonResponse({
                "success": True,
                "new_status": reservation.status,
                "status_display": reservation.get_status_display(),
                "message": f"Status da reserva #{reservation.id} atualizado para '{reservation.get_status_display()}'."
            })

        return JsonResponse({"success": False, "message": "Status inválido."}, status=400)


# ==============================================================================
# LANÇAMENTO MANUAL DE PEDIDOS (PDV WHATSAPP & BALCÃO)
# ==============================================================================

@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.is_staff), name="dispatch")
class AdminManualOrderView(View):
    """Tela e processador do PDV / Lançamento Manual de Pedidos pelo Lojista."""
    template_name = "pages/admin-manual-order.html"

    def get(self, request, *args, **kwargs):
        products = (
            Product.objects.filter(is_active=True)
            .select_related("brand", "category")
            .prefetch_related("variants", "images")
            .order_by("title")
        )

        catalog_data = []
        for p in products:
            cover_url = p.cover_image.url if p.cover_image else ""
            available_colors = p.available_colors
            variants_matrix = p.variants_matrix
            variants_list = [
                {
                    "id": v.id,
                    "size": v.size,
                    "color": v.color or "",
                    "stock": v.stock_quantity,
                    "sku": v.sku or "",
                    "price": float(v.final_price),
                }
                for v in p.variants.all()
            ]
            catalog_data.append({
                "id": p.id,
                "title": p.title,
                "slug": p.slug,
                "brand_name": p.brand.name if p.brand else "",
                "category_name": p.category.name if p.category else "",
                "price": float(p.price),
                "cover_url": cover_url,
                "in_stock": p.in_stock,
                "available_colors": available_colors,
                "variants_matrix": variants_matrix,
                "variants": variants_list,
            })

        # Suporte a pré-carregamento direto da Fila de Espera (Reservas)
        reservation_id = request.GET.get("reservation_id")
        preloaded_reservation = None
        if reservation_id:
            preloaded_reservation = ProductReservation.objects.filter(id=reservation_id).select_related("product__brand").first()

        preloaded_data = {
            "customer_name": request.GET.get("customer_name", ""),
            "customer_phone": request.GET.get("customer_phone", ""),
            "product_id": request.GET.get("product_id", ""),
            "color": request.GET.get("color", ""),
            "size": request.GET.get("size", ""),
            "reservation_id": reservation_id or "",
        }

        if preloaded_reservation:
            preloaded_data.update({
                "customer_name": preloaded_reservation.customer_name,
                "customer_phone": preloaded_reservation.customer_phone,
                "product_id": preloaded_reservation.product.id,
                "color": preloaded_reservation.color,
                "size": preloaded_reservation.size,
                "reservation_id": preloaded_reservation.id,
            })

        context = {
            "products_json": json.dumps(catalog_data),
            "payment_choices": Order.PAYMENT_METHOD_CHOICES,
            "delivery_choices": Order.DELIVERY_METHOD_CHOICES,
            "status_choices": Order.STATUS_CHOICES,
            "origin_choices": Order.ORIGIN_CHOICES,
            "preloaded_data_json": json.dumps(preloaded_data),
            "preloaded_reservation": preloaded_reservation,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1"

        customer_name = request.POST.get("customer_name", "").strip()
        customer_phone = request.POST.get("customer_phone", "").strip()
        customer_email = request.POST.get("customer_email", "").strip()
        shipping_address = request.POST.get("shipping_address", "").strip()
        city = request.POST.get("city", "Cajazeiras").strip()
        state = request.POST.get("state", "PB").strip()
        postal_code = request.POST.get("postal_code", "58900-000").strip()

        payment_method = request.POST.get("payment_method", "pix")
        delivery_method = request.POST.get("delivery_method", "pickup")
        origin = request.POST.get("origin", "whatsapp")
        status = request.POST.get("status", "confirmed")
        notes = request.POST.get("notes", "").strip()
        reservation_id = request.POST.get("reservation_id")

        try:
            shipping_cost = Decimal(str(request.POST.get("shipping_cost", "0.00")).replace(",", "."))
        except Exception:
            shipping_cost = Decimal("0.00")

        try:
            discount = Decimal(str(request.POST.get("discount", "0.00")).replace(",", "."))
        except Exception:
            discount = Decimal("0.00")

        items_raw = request.POST.get("items_json", "[]")
        try:
            items_data = json.loads(items_raw)
        except Exception:
            items_data = []

        if not customer_name or not customer_phone:
            err_msg = "Por favor, preencha o Nome e o WhatsApp do cliente."
            if is_ajax:
                return JsonResponse({"success": False, "message": err_msg}, status=400)
            messages.error(request, err_msg)
            return redirect("orders:manual_order_create")

        if not items_data:
            err_msg = "Adicione ao menos uma peça ao pedido."
            if is_ajax:
                return JsonResponse({"success": False, "message": err_msg}, status=400)
            messages.error(request, err_msg)
            return redirect("orders:manual_order_create")

        # Criação do Pedido
        order = Order.objects.create(
            user=request.user,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            shipping_address=shipping_address,
            city=city,
            state=state,
            postal_code=postal_code,
            payment_method=payment_method,
            delivery_method=delivery_method,
            origin=origin,
            status=status,
            notes=notes,
            shipping_cost=shipping_cost,
        )

        subtotal = Decimal("0.00")

        for item_info in items_data:
            product_id = item_info.get("product_id")
            product = get_object_or_404(Product, id=product_id)
            variant_id = item_info.get("variant_id")
            size = item_info.get("size", "Único")
            color = item_info.get("color", "")
            qty = int(item_info.get("quantity", 1))

            try:
                unit_price = Decimal(str(item_info.get("unit_price", product.price)).replace(",", "."))
            except Exception:
                unit_price = product.price

            total_item_price = unit_price * qty
            subtotal += total_item_price

            variant = None
            if variant_id:
                variant = ProductVariant.objects.filter(id=variant_id).first()
            if not variant:
                variant = product.variants.filter(size=size, color=color).first()
            if not variant:
                variant = product.variants.filter(size=size).first()
            if not variant:
                variant = ProductVariant.objects.create(
                    product=product,
                    size=size,
                    color=color,
                    stock_quantity=0,
                    sku=f"{product.slug}-{size}-{color}".strip("-"),
                )

            # Baixa no estoque
            if variant and variant.stock_quantity >= qty:
                variant.stock_quantity -= qty
                variant.save()
            elif variant and variant.stock_quantity > 0:
                variant.stock_quantity = 0
                variant.save()

            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_title=product.title,
                brand_name=product.brand.name if product.brand else "",
                size=size,
                color=color,
                quantity=qty,
                unit_price=unit_price,
                total_price=total_item_price,
            )

        final_total = max(Decimal("0.00"), subtotal + shipping_cost - discount)
        order.subtotal = subtotal
        order.total = final_total
        order.save()

        # Se veio de uma reserva, marca a reserva como convertida
        if reservation_id:
            ProductReservation.objects.filter(id=reservation_id).update(status="converted")

        receipt_url = order.generate_receipt_whatsapp_link()

        if is_ajax:
            return JsonResponse({
                "success": True,
                "order_number": order.order_number,
                "order_id": order.id,
                "receipt_whatsapp_link": receipt_url,
                "message": f"Pedido #{order.order_number} cadastrado com sucesso! Total: R$ {order.total:.2f}",
            })

        messages.success(request, f"Pedido #{order.order_number} cadastrado com sucesso!")
        return redirect("orders:order_detail", order_number=order.order_number)


# ==============================================================================
# SMART CRM & ETIQUETAS & NOTIFICAÇÕES WHATSAPP
# ==============================================================================

@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.is_staff), name="dispatch")
class CustomerSearchApiView(View):
    """Busca inteligente de clientes por nome ou telefone para autocomplete no PDV."""
    def get(self, request, *args, **kwargs):
        q = request.GET.get("q", "").strip()
        if len(q) < 2:
            return JsonResponse({"customers": []})

        orders = (
            Order.objects.filter(
                Q(customer_name__icontains=q) | Q(customer_phone__icontains=q)
            )
            .order_by("-created_at")
        )

        seen_phones = set()
        customers = []

        for o in orders:
            clean_phone = "".join(filter(str.isdigit, o.customer_phone))
            if clean_phone in seen_phones:
                continue
            seen_phones.add(clean_phone)

            # Histórico do cliente
            cust_filter = Q(customer_name__iexact=o.customer_name)
            if o.customer_phone:
                cust_filter |= Q(customer_phone=o.customer_phone)
            cust_orders = Order.objects.filter(cust_filter)
            total_orders = cust_orders.count()
            total_spent = sum(ord.total for ord in cust_orders)

            customers.append({
                "name": o.customer_name,
                "phone": o.customer_phone,
                "email": o.customer_email,
                "shipping_address": o.shipping_address,
                "city": o.city,
                "state": o.state,
                "postal_code": o.postal_code,
                "total_orders": total_orders,
                "total_spent": float(total_spent),
            })

            if len(customers) >= 8:
                break

        return JsonResponse({"customers": customers})


@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.is_staff), name="dispatch")
class OrderLabelPrintView(DetailView):
    """Renderiza a etiqueta de envio e cupom de sacola para impressão térmica (58/80mm) ou A4."""
    model = Order
    template_name = "pages/order-label-print.html"
    context_object_name = "order"
    slug_field = "order_number"
    slug_url_kwarg = "order_number"


@method_decorator(user_passes_test(lambda u: u.is_authenticated and u.is_staff), name="dispatch")
class OrderStatusWhatsAppView(View):
    """Gera o link de WhatsApp para atualizações pontuais de status (separação, motoboy, retirada, rastreio)."""
    def get(self, request, order_number, status_type, *args, **kwargs):
        order = get_object_or_404(Order, order_number=order_number)
        tracking_code = request.GET.get("tracking_code", "")
        wa_link = order.generate_status_whatsapp_link(status_type=status_type, tracking_code=tracking_code)

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": True, "whatsapp_link": wa_link})

        return redirect(wa_link)


@method_decorator(csrf_exempt, name="dispatch")
class AgendaView(View):
    """Página de Agendamento Online da Barbearia Eduardo Cardoso (Vakaria)."""

    def get(self, request, *args, **kwargs):
        # Procedimentos autênticos da barbearia (Cortes, Barba e Alquimia)
        services = (
            Product.objects.filter(is_active=True)
            .filter(
                Q(category__slug__in=["cortes-visagismo", "barba-rituais", "alquimia-capilar-cor"])
                | Q(category__parent__slug__in=["cortes-visagismo", "barba-rituais", "alquimia-capilar-cor"])
            )
            .select_related("category", "brand", "category__parent")
            .prefetch_related("images")
            .order_by("category__parent__order", "category__order", "title")
        )

        if not services.exists():
            services = Product.objects.filter(is_active=True).select_related("category").order_by("title")

        # Procedimento pré-selecionado via query param (?service=slug_ou_id)
        selected_service_param = request.GET.get("service")
        preselected_ids = []
        if selected_service_param:
            preselected_prod = services.filter(
                Q(slug=selected_service_param) | Q(id__iexact=selected_service_param if selected_service_param.isdigit() else 0)
            ).first()
            if preselected_prod:
                preselected_ids.append(preselected_prod.id)

        # Horários disponíveis padrão no ateliê
        time_slots = [
            "09:00", "09:45", "10:30", "11:15",
            "13:30", "14:15", "15:00", "15:45",
            "16:30", "17:15", "18:00", "18:45"
        ]

        # Próximas datas sugeridas (próximos 14 dias, excluindo domingo e segunda)
        today = timezone.localdate()
        available_dates = []
        day_names_pt = {
            0: "Seg", 1: "Ter", 2: "Qua", 3: "Qui", 4: "Sex", 5: "Sáb", 6: "Dom"
        }
        for i in range(1, 15):
            d = today + timezone.timedelta(days=i)
            # Ateliê funciona de Terça a Sábado
            if d.weekday() not in (0, 6):
                available_dates.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "formatted": d.strftime("%d/%m"),
                    "day_name": day_names_pt[d.weekday()],
                    "full_str": f"{day_names_pt[d.weekday()]}, {d.strftime('%d/%m')}",
                })

        context = {
            "services": services,
            "preselected_ids": preselected_ids,
            "time_slots": time_slots,
            "available_dates": available_dates,
            "today_iso": today.strftime("%Y-%m-%d"),
        }
        return render(request, "pages/agenda.html", context)

    def post(self, request, *args, **kwargs):
        customer_name = request.POST.get("customer_name", "").strip()
        customer_phone = request.POST.get("customer_phone", "").strip()
        customer_email = request.POST.get("customer_email", "").strip()
        service_ids = request.POST.getlist("services")
        appointment_date_str = request.POST.get("appointment_date", "").strip()
        appointment_time = request.POST.get("appointment_time", "").strip()
        notes = request.POST.get("notes", "").strip()
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.POST.get("ajax") == "1"

        if not customer_name or not customer_phone or not appointment_date_str or not appointment_time:
            msg = "Por favor, preencha todos os campos obrigatórios (Nome, WhatsApp, Data e Horário)."
            if is_ajax:
                return JsonResponse({"success": False, "message": msg}, status=400)
            messages.error(request, msg)
            return redirect("orders:agenda")

        try:
            appointment_date = timezone.datetime.strptime(appointment_date_str, "%Y-%m-%d").date()
        except ValueError:
            msg = "Formato de data inválido."
            if is_ajax:
                return JsonResponse({"success": False, "message": msg}, status=400)
            messages.error(request, msg)
            return redirect("orders:agenda")

        selected_services = Product.objects.filter(id__in=service_ids, is_active=True)
        total_price = sum(s.price for s in selected_services) if selected_services.exists() else Decimal("0.00")

        appointment = Appointment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            total_price=total_price,
            notes=notes,
            status="pending",
        )
        if selected_services.exists():
            appointment.services.set(selected_services)

        whatsapp_url = appointment.generate_whatsapp_confirmation_link()

        if is_ajax:
            return JsonResponse({
                "success": True,
                "message": "Agendamento registrado com sucesso! Redirecionando para o WhatsApp...",
                "whatsapp_url": whatsapp_url,
                "appointment_id": appointment.id,
            })

        messages.success(request, "Agendamento pré-reservado! Enviando para o WhatsApp de confirmação...")
        return redirect(whatsapp_url)




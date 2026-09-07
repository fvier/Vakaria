from django.urls import path
from larkon.catalog.views import admin_inventory_view
from . import views

app_name = "orders"

urlpatterns = [
    path("agenda/", views.AgendaView.as_view(), name="agenda"),
    path("carrinho/", views.CartView.as_view(), name="cart"),
    path("carrinho/adicionar/", views.AddToCartView.as_view(), name="add_to_cart"),
    path("carrinho/remover/<int:item_id>/", views.RemoveFromCartView.as_view(), name="remove_from_cart"),
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("pedido/<str:order_number>/", views.OrderDetailView.as_view(), name="order_detail"),
    # CRM & Reservas / Fila de Espera
    path("reservar/", views.CreateReservationView.as_view(), name="create_reservation"),
    path("reservas/", views.AdminReservationsView.as_view(), name="admin_reservations"),
    path("reservas/<int:pk>/status/", views.UpdateReservationStatusView.as_view(), name="update_reservation_status"),
    # PDV & Lançamento Manual de Pedidos (WhatsApp / Balcão)
    path("novo/", views.AdminManualOrderView.as_view(), name="manual_order_create"),
    path("pdv/", views.AdminManualOrderView.as_view(), name="manual_order_pdv"),
    path("clientes/busca/", views.CustomerSearchApiView.as_view(), name="customer_search"),
    # Impressão de Etiqueta e Cupom Térmico
    path("<str:order_number>/etiqueta/", views.OrderLabelPrintView.as_view(), name="order_label_print"),
    # Disparos de Status de Envio WhatsApp
    path("<str:order_number>/status-whatsapp/<str:status_type>/", views.OrderStatusWhatsAppView.as_view(), name="order_status_whatsapp"),
    # Atalho para Controle de Estoque no Módulo de Vendas
    path("estoque/", admin_inventory_view, name="admin_inventory"),
]




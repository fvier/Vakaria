from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem, ProductReservation, Appointment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_title", "brand_name", "size", "color", "quantity", "unit_price", "total_price")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "session_key", "total_items", "subtotal", "created_at", "updated_at")
    inlines = [CartItemInline]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer_name", "customer_phone", "origin", "payment_method", "delivery_method", "status_display", "total", "created_at", "whatsapp_button", "receipt_button")
    list_filter = ("status", "origin", "payment_method", "delivery_method", "created_at")
    search_fields = ("order_number", "customer_name", "customer_email", "customer_phone")
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderItemInline]

    def status_display(self, obj):
        colors = {
            "pending": "orange",
            "confirmed": "blue",
            "preparing": "purple",
            "shipped": "teal",
            "delivered": "green",
            "cancelled": "red",
        }
        color = colors.get(obj.status, "gray")
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_display.short_description = "Status"

    def whatsapp_button(self, obj):
        link = obj.generate_whatsapp_link()
        return format_html('<a class="button" style="background-color: #25D366; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none;" href="{}" target="_blank">📲 WhatsApp</a>', link)
    whatsapp_button.short_description = "WhatsApp Loja"

    def receipt_button(self, obj):
        link = obj.generate_receipt_whatsapp_link()
        return format_html('<a class="button" style="background-color: #0f172a; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none;" href="{}" target="_blank">🧾 Enviar Recibo</a>', link)
    receipt_button.short_description = "Comprovante"



@admin.register(ProductReservation)
class ProductReservationAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_phone", "product", "color", "size", "status_badge", "created_at", "whatsapp_vip_button")
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "customer_phone", "product__title", "notes")
    readonly_fields = ("created_at", "updated_at")

    def status_badge(self, obj):
        colors = {
            "pending": "#d97706",
            "notified": "#2563eb",
            "converted": "#16a34a",
            "cancelled": "#dc2626",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = "Status"

    def whatsapp_vip_button(self, obj):
        link = obj.generate_whatsapp_vip_link()
        return format_html('<a class="button" style="background-color: #25D366; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none;" href="{}" target="_blank">💬 Avisar Peça Chegou</a>', link)
    whatsapp_vip_button.short_description = "Aviso VIP"


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_phone", "appointment_date", "appointment_time", "total_price", "status_badge", "created_at", "whatsapp_button")
    list_filter = ("status", "appointment_date", "created_at")
    search_fields = ("customer_name", "customer_phone", "customer_email", "notes")
    filter_horizontal = ("services",)
    readonly_fields = ("created_at", "updated_at")

    def status_badge(self, obj):
        colors = {
            "pending": "#d97706",
            "confirmed": "#2563eb",
            "completed": "#16a34a",
            "cancelled": "#dc2626",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.get_status_display())
    status_badge.short_description = "Status"

    def whatsapp_button(self, obj):
        link = obj.generate_whatsapp_confirmation_link()
        return format_html('<a class="button" style="background-color: #25D366; color: white; padding: 3px 8px; border-radius: 4px; text-decoration: none;" href="{}" target="_blank">📲 WhatsApp</a>', link)
    whatsapp_button.short_description = "WhatsApp Barbeiro"


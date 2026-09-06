from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Category, Drop, Product, ProductVariant, ProductImage, CarouselSlide, LinktreeItem, StockMovement


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2
    fields = ("image", "image_url", "alt_text", "order", "is_cover")


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 3
    fields = ("size", "color", "sku", "stock_quantity", "additional_price")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "website", "products_count", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = "Peças Cadastradas"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "gender_target", "parent", "order", "is_active")
    list_filter = ("gender_target", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Drop)
class DropAdmin(admin.ModelAdmin):
    list_display = ("title", "edition", "launch_date", "is_featured", "is_active", "products_count")
    list_filter = ("is_active", "is_featured", "launch_date")
    search_fields = ("title", "edition", "description")
    prepopulated_fields = {"slug": ("title",)}

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = "Peças do Drop"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "brand", "category", "gender", "price", "total_stock_display", "is_exclusive", "is_featured", "is_active")
    list_filter = ("brand", "category", "gender", "is_exclusive", "is_featured", "is_active", "drop")
    search_fields = ("title", "description", "brand__name", "category__name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductVariantInline, ProductImageInline]

    def total_stock_display(self, obj):
        stock = obj.total_stock
        color = "green" if stock > 0 else "red"
        return format_html('<b style="color:{};">{} un.</b>', color, stock)
    total_stock_display.short_description = "Estoque Total"


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "slide_type", "order", "is_active", "button_text", "created_at")
    list_filter = ("slide_type", "is_active")
    search_fields = ("title", "subtitle", "badge_text")
    list_editable = ("order", "is_active")


@admin.register(LinktreeItem)
class LinktreeItemAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "style", "order", "is_active", "clicks_count", "created_at")
    list_filter = ("style", "is_active", "is_highlighted")
    search_fields = ("title", "subtitle", "url")
    list_editable = ("order", "is_active")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "size", "color", "sku", "stock_quantity", "final_price")
    list_filter = ("size", "color")
    search_fields = ("sku", "product__title")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "order", "is_cover")
    list_filter = ("is_cover",)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("created_at", "movement_type", "variant", "quantity", "previous_stock", "new_stock", "reason", "invoice_number", "created_by")
    list_filter = ("movement_type", "reason", "created_at")
    search_fields = ("variant__product__title", "variant__sku", "invoice_number", "notes")
    date_hierarchy = "created_at"

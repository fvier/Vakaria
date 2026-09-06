from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="home"),
    path("produtos/", views.ProductGridView.as_view(), name="product_grid"),
    path("produtos/cadastrar-rapido/", views.quick_create_product_view, name="quick_create_product"),
    path("produtos/<int:pk>/editar-rapido/", views.quick_edit_product_view, name="quick_edit_product"),
    path("produtos/<int:pk>/excluir/", views.quick_delete_product_view, name="quick_delete_product"),
    path("produtos/<int:pk>/dados-edicao/", views.get_product_edit_data_view, name="product_edit_data"),
    path("produto/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("marcas/", views.BrandListView.as_view(), name="brand_list"),
    path("marca/<slug:slug>/", views.BrandDetailView.as_view(), name="brand_detail"),
    
    # Módulo de Gestão de Estoque (Entradas & Saídas)
    path("estoque/", views.admin_inventory_view, name="admin_inventory"),
    path("estoque/variante/<int:pk>/historico/", views.admin_variant_history_api, name="admin_variant_history"),
]

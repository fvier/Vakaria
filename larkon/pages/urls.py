from django.urls import path
from .views import (
    root_page_view,
    dynamic_pages_view,
    linktree_public_view,
    linktree_click_view,
    admin_home_cms_view,
    admin_carousel_view,
    admin_carousel_quick_data_view,
    admin_carousel_toggle_view,
    admin_carousel_delete_view,
    admin_review_quick_data_view,
    admin_review_toggle_view,
    admin_review_delete_view,
    admin_linktree_view,
    admin_linktree_quick_data_view,
    admin_linktree_toggle_view,
    admin_linktree_delete_view,
)

app_name = "pages"
urlpatterns = [
    path("", root_page_view, name="dashboard"),
    
    # Módulo de Gestão da Página Inicial (Home CMS)
    path("admin/inicio/", admin_home_cms_view, name="admin_home_cms"),
    path("admin/carrossel/", admin_carousel_view, name="admin_carousel"),
    path("admin/carrossel/<int:pk>/data/", admin_carousel_quick_data_view, name="admin_carousel_data"),
    path("admin/carrossel/<int:pk>/toggle/", admin_carousel_toggle_view, name="admin_carousel_toggle"),
    path("admin/carrossel/<int:pk>/remover/", admin_carousel_delete_view, name="admin_carousel_delete"),
    
    # Depoimentos de Clientes (Reviews)
    path("admin/depoimento/<int:pk>/data/", admin_review_quick_data_view, name="admin_review_data"),
    path("admin/depoimentos/<int:pk>/data/", admin_review_quick_data_view, name="admin_reviews_data"),
    path("admin/depoimento/<int:pk>/toggle/", admin_review_toggle_view, name="admin_review_toggle"),
    path("admin/depoimentos/<int:pk>/toggle/", admin_review_toggle_view, name="admin_reviews_toggle"),
    path("admin/depoimento/<int:pk>/remover/", admin_review_delete_view, name="admin_review_delete"),
    path("admin/depoimentos/<int:pk>/remover/", admin_review_delete_view, name="admin_reviews_delete"),
    
    path("admin/linktree/", admin_linktree_view, name="admin_linktree"),
    path("admin/linktree/<int:pk>/data/", admin_linktree_quick_data_view, name="admin_linktree_data"),
    path("admin/linktree/<int:pk>/toggle/", admin_linktree_toggle_view, name="admin_linktree_toggle"),
    path("admin/linktree/<int:pk>/remover/", admin_linktree_delete_view, name="admin_linktree_delete"),
    path("admin/linktree/<int:pk>/clique/", linktree_click_view, name="linktree_click"),

    # Páginas Dinâmicas do Tema
    path("<str:template_name>/", dynamic_pages_view, name="dynamic_pages"),
]

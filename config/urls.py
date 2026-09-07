# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from allauth.account.views import LoginView, LogoutView
import larkon.pages.views

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # Rotas Diretas de Autenticação
    path("login/", LoginView.as_view(), name="account_login_direct"),
    path("logout/", LogoutView.as_view(), name="account_logout_direct"),
    # User management & Allauth
    path("users/", include("larkon.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # E-commerce Vakaria: Catálogo e Pedidos
    path("", include("larkon.catalog.urls", namespace="catalog")),
    path("pedidos/", include("larkon.orders.urls", namespace="orders")),
    # Agenda Online & Agendamento Direto
    path("agenda/", larkon.orders.views.AgendaView.as_view(), name="agenda"),
    path("agenda", larkon.orders.views.AgendaView.as_view()),
    path("agendar/", larkon.orders.views.AgendaView.as_view(), name="agendar"),
    path("agendar", larkon.orders.views.AgendaView.as_view()),
    # Módulo de Reservas & Fila de Espera (CRM)
    path("reservas/", larkon.orders.views.AdminReservationsView.as_view(), name="reservas_direct"),
    path("reservas/<int:pk>/status/", larkon.orders.views.UpdateReservationStatusView.as_view(), name="reservas_status_direct"),
    # Linktree Público Vakaria
    path("links/", larkon.pages.views.linktree_public_view, name="linktree_public"),
    path("links", larkon.pages.views.linktree_public_view),
    # Linktree Exclusivo Luiza Fit (/tree)
    path("tree/", larkon.pages.views.linktree_luiza_view, name="linktree_luiza"),
    path("tree", larkon.pages.views.linktree_luiza_view),
    # Painel Administrativo / Dashboard
    path("dashboard/", include("larkon.pages.urls", namespace="pages")),
    # Media files (funciona tanto em dev quanto em prod com volumes locais)
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]


from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

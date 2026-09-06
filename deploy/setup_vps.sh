#!/bin/bash
# ==============================================================================
# SCRIPT DE DEPLOY AUTOMATIZADO - VAKARIA (VPS 147.79.110.132)
# ==============================================================================

set -e

echo "🚀 Iniciando deploy da Vakaria Barbearia no servidor 147.79.110.132..."

# 1. Cria .env.vps a partir do exemplo se não existir
if [ ! -f .env.vps ]; then
    echo "📋 Criando arquivo .env.vps a partir do .env.vps.example..."
    cp .env.vps.example .env.vps
fi

# 2. Build e inicialização dos containers Docker
echo "📦 Construindo containers (Django + Postgres 16 + Caddy SSL)..."
docker compose down || true
docker compose build --no-cache
docker compose up -d

# 3. Aguarda o container do Django iniciar
echo "⏳ Aguardando inicialização do Django..."
sleep 10

# 4. Executa criação inicial de superusuário e seeds
echo "🌱 Criando dados iniciais e usuário Herivelton..."
docker compose exec app python -c '
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()
from larkon.users.models import User
from larkon.catalog.models import CarouselSlide, LinktreeItem

# Cria ou atualiza usuário administrador inicial
admin_email = os.environ.get("INITIAL_ADMIN_EMAIL", "herivelton@vakaria.com.br")
admin_pass = os.environ.get("INITIAL_ADMIN_PASSWORD", "")

user, created = User.objects.get_or_create(
    email=admin_email,
    defaults={"name": "Administrador", "is_staff": True, "is_superuser": True}
)
if admin_pass:
    user.set_password(admin_pass)
user.is_staff = True
user.is_superuser = True
user.save()
print(f"✓ Usuário {admin_email} pronto!")

# Seed de slides
if not CarouselSlide.objects.exists():
    CarouselSlide.objects.create(
        title="O Melhor em Barbearia e Estilo em Uma Só Experiência",
        subtitle="Curadoria exclusiva de alta moda feminina. Vestidos fluidos, sedas nobres, alfaiataria impecável e peças autorais das marcas mais consagradas do país.",
        badge_text="✨ VAKARIA BARBEARIA • CAJAZEIRAS - PB",
        image_url="/static/images/hero_feminina.jpg",
        button_text="Coleção Feminina",
        button_url="/produtos/?gender=F",
        slide_type="hero",
        order=1,
        is_active=True
    )
    CarouselSlide.objects.create(
        title="Moda Masculina Premium & Alfaiataria Contemporânea",
        subtitle="O encontro do conforto com a sofisticação. Camisaria em linho puro, polos pima, calçados e peças casuais de luxo para homens que exigem o melhor.",
        badge_text="📍 MODA MASCULINA PREMIUM • CAJAZEIRAS - PB",
        image_url="/static/images/hero_masculina.jpg",
        button_text="Coleção Masculina",
        button_url="/produtos/?gender=M",
        slide_type="hero",
        order=2,
        is_active=True
    )
    print("✓ Carousel slides prontos!")

# Seed de Linktree
if not LinktreeItem.objects.exists():
    LinktreeItem.objects.create(
        title="📲 Consultoria & Vendas no WhatsApp",
        subtitle="Fale agora com nossa equipe de consultoras VIP",
        url="https://wa.me/558183983355",
        icon="bx bxl-whatsapp",
        style="success",
        is_highlighted=True,
        order=1,
        is_active=True
    )
    LinktreeItem.objects.create(
        title="🛍️ Catálogo Online & Vitrine da Semana",
        subtitle="Confira todas as novidades e peças exclusivas",
        url="/produtos/",
        icon="bx bx-shopping-bag",
        style="gold",
        order=2,
        is_active=True
    )
    LinktreeItem.objects.create(
        title="🔥 Grupo VIP de Promoções & Drops",
        subtitle="Receba lançamentos exclusivos e promoções no WhatsApp",
        url="https://chat.whatsapp.com/EoQm1858BrK36Uvjs6dYRG?mode=gi_t",
        icon="bx bxs-flame",
        style="dark",
        order=3,
        is_active=True
    )
    print("✓ Linktree pronto!")
'

echo "=================================================================="
echo "🎉 DEPLOY CONCLUÍDO COM SUCESSO!"
echo "🌐 Acesse: https://vakaria.com.br"
echo "🔐 Login: https://vakaria.com.br/login/"
echo "🔗 Linktree: https://vakaria.com.br/links"
echo "=================================================================="

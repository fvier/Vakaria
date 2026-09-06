from datetime import date, time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from larkon.catalog.models import (
    Brand,
    Category,
    Drop,
    Product,
    ProductVariant,
    CarouselSlide,
    CustomerReview,
    HomePageConfig,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com a identidade, serviços e ambiente do Cabeleireiro Eduardo Cardoso em Olinda"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("💈 Iniciando o Seed do Cabeleireiro Eduardo Cardoso (Olinda - PE)..."))

        # 1. Superuser
        if not User.objects.filter(email="admin@vakaria.com.br").exists():
            User.objects.create_superuser("admin@vakaria.com.br", "admin123", name="Eduardo Cardoso")
            self.stdout.write(self.style.SUCCESS("✅ Superusuário criado: admin@vakaria.com.br / admin123"))

        # 2. Linhas de Cuidado / Assinaturas
        brands_data = [
            {"name": "Eduardo Cardoso Atelier", "description": "Atendimento autoral com corte e visagismo personalizado no Sítio Histórico de Olinda."},
            {"name": "Ritual Barber & Spa", "description": "Alinhamento preciso, toalha quente e cuidados faciais para relaxamento pleno."},
            {"name": "Alquimia Capilar Olinda", "description": "Cor, mechas, relaxamento seguro e a autêntica arte do 'nevou' olindense."},
        ]

        brand_objs = {}
        for b_data in brands_data:
            brand, _ = Brand.objects.get_or_create(name=b_data["name"], defaults={"description": b_data["description"], "is_active": True})
            brand_objs[b_data["name"]] = brand
        self.stdout.write(self.style.SUCCESS(f"✅ {len(brand_objs)} Linhas de Serviços cadastradas"))

        # 3. Categorias Principais do Ecossistema
        cat_cortes, _ = Category.objects.get_or_create(
            name="Cortes Personalizados",
            defaults={"gender_target": "U", "order": 1, "icon": "solar:scissors-square-bold-duotone"}
        )
        cat_barba, _ = Category.objects.get_or_create(
            name="Barba, Bigode & Cuidados Faciais",
            defaults={"gender_target": "M", "order": 2, "icon": "solar:shield-user-bold-duotone"}
        )
        cat_quimica, _ = Category.objects.get_or_create(
            name="Alquimia Capilar, Cor & Química",
            defaults={"gender_target": "U", "order": 3, "icon": "solar:fire-bold-duotone"}
        )

        subcats = [
            ("Cortes Masculinos Autorais", "M", cat_cortes),
            ("Cortes Femininos Personalizados", "F", cat_cortes),
            ("Cortes Infantis & Juvenis", "U", cat_cortes),
            ("Ritual da Barba com Toalha Quente", "M", cat_barba),
            ("Alinhamento & Barboterapia", "M", cat_barba),
            ("Nevou & Descoloração Global", "U", cat_quimica),
            ("Coloração Artística & Mechas", "U", cat_quimica),
            ("Tratamentos & Cronograma Capilar", "U", cat_quimica),
        ]

        cat_objs = {}
        for name, gender, parent in subcats:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"gender_target": gender, "parent": parent})
            cat_objs[name] = cat
        self.stdout.write(self.style.SUCCESS("✅ Categorias do Ecossistema de Beleza configuradas"))

        # 4. Drops / Sessões de Atendimento
        drop_olinda, _ = Drop.objects.get_or_create(
            title="Temporada Olinda — Identidade, Arte & Acolhimento",
            defaults={
                "edition": "OLINDA-2026",
                "launch_date": date.today(),
                "description": "Experiência completa de cuidado e estética nas ladeiras do Sítio Histórico de Olinda.",
                "is_featured": True,
                "is_active": True,
            }
        )

        # 5. Serviços / Procedimentos
        services_data = [
            {
                "title": "Corte Autoral Eduardo Cardoso (Todas as Gerações)",
                "brand": brand_objs["Eduardo Cardoso Atelier"],
                "category": cat_objs["Cortes Masculinos Autorais"],
                "gender": "U",
                "price": 60.00,
                "compare_at_price": 70.00,
                "description": (
                    "A tesoura não tem gênero. Atendimento focado na escuta atenta para traduzir a sua "
                    "personalidade e estilo de vida. Inclui lavagem com produtos de alta performance, "
                    "corte milimétrico e finalização personalizada."
                ),
                "fabric_composition": "Tesoura, Navalha & Visagismo Humanizado",
                "care_instructions": "Recomendada manutenção a cada 20 a 30 dias para preservar as linhas do corte.",
                "is_featured": True,
                "variants": [
                    {"size": "Tradicional", "color": "Atelier", "stock": 99},
                    {"size": "Moderno / Fade", "color": "Atelier", "stock": 99},
                ],
            },
            {
                "title": "Corte Feminino Personalizado & Visagismo",
                "brand": brand_objs["Eduardo Cardoso Atelier"],
                "category": cat_objs["Cortes Femininos Personalizados"],
                "gender": "F",
                "price": 80.00,
                "compare_at_price": 95.00,
                "description": (
                    "Corte feito sob medida para realçar os traços, textura natural dos fios e identidade. "
                    "Seja curto, médio, longo ou desfiado, a proposta é leveza, movimento e harmonia."
                ),
                "fabric_composition": "Corte a Seco ou Molhado com Finalização Especial",
                "care_instructions": "Finalizado com leave-in botânico e secagem respeitando a curvatura do fio.",
                "is_featured": True,
                "variants": [
                    {"size": "Curto / Pixie", "color": "Atelier", "stock": 99},
                    {"size": "Médio / Long Bob", "color": "Atelier", "stock": 99},
                    {"size": "Longo em Camadas", "color": "Atelier", "stock": 99},
                ],
            },
            {
                "title": "Ritual da Barba com Toalha Quente & Óleos Essenciais",
                "brand": brand_objs["Ritual Barber & Spa"],
                "category": cat_objs["Ritual da Barba com Toalha Quente"],
                "gender": "M",
                "price": 45.00,
                "compare_at_price": 50.00,
                "description": (
                    "O ritual clássico elevado a outro nível. Aplicação de toalha quente com vapor aromático, "
                    "massagem facial, alinhamento milimétrico com navalhete descartável e hidratação profunda da pele."
                ),
                "fabric_composition": "Toalha Quente, Balm Artesanal & Navalha de Precisão",
                "care_instructions": "Finalizado com pós-barba calmante e óleo para barba com fragrância amadeirada sutil.",
                "is_featured": True,
                "variants": [
                    {"size": "Barba Completa", "color": "Barber Spa", "stock": 99},
                    {"size": "Apenas Desenho", "color": "Barber Spa", "stock": 99},
                ],
            },
            {
                "title": "Combo Completo: Corte Autoral + Ritual da Barba",
                "brand": brand_objs["Eduardo Cardoso Atelier"],
                "category": cat_objs["Ritual da Barba com Toalha Quente"],
                "gender": "M",
                "price": 95.00,
                "compare_at_price": 105.00,
                "description": (
                    "A experiência definitiva do laboratório. Uma pausa de puro relaxamento e renovação no Sítio "
                    "Histórico de Olinda: corte completo alinhado ao seu perfil + ritual da barba com toalha quente."
                ),
                "fabric_composition": "Visagismo Completo + Barboterapia Relaxante",
                "care_instructions": "Duração média: 60 minutos de acolhimento e cuidado impecável.",
                "is_featured": True,
                "variants": [
                    {"size": "Sessão Completa", "color": "Olinda VIP", "stock": 99},
                ],
            },
            {
                "title": "Nevou Olindense — Descoloração Global de Alto Padrão",
                "brand": brand_objs["Alquimia Capilar Olinda"],
                "category": cat_objs["Nevou & Descoloração Global"],
                "gender": "U",
                "price": 130.00,
                "compare_at_price": 150.00,
                "description": (
                    "Celebrando o autêntico estilo 'nevou' como uma marca vibrante da nossa cultura urbana. "
                    "Processo de descoloração seguro, com proteção prévia do couro cabeludo (Plex) e matização "
                    "perolada ou platinada impecável."
                ),
                "fabric_composition": "Descolorante Premium com Proteção Plex Anti-Danos",
                "care_instructions": "Acompanha orientação para manutenção em casa e máscara de nutrição.",
                "is_featured": True,
                "variants": [
                    {"size": "Cabelo Curto", "color": "Platinado Gelo", "stock": 99},
                    {"size": "Cabelo Médio", "color": "Platinado Gelo", "stock": 99},
                ],
            },
            {
                "title": "Corte Infantil & Juvenil com Acolhimento",
                "brand": brand_objs["Eduardo Cardoso Atelier"],
                "category": cat_objs["Cortes Infantis & Juvenis"],
                "gender": "U",
                "price": 45.00,
                "compare_at_price": 50.00,
                "description": (
                    "Paciência, respeito ao tempo da criança e muita leveza. O momento do corte transformado "
                    "em uma experiência divertida e agradável nas ladeiras de Olinda."
                ),
                "fabric_composition": "Ambiente Seguro e Lúdico",
                "care_instructions": "Sem pressa, com diálogo e total cuidado com os pequenos.",
                "is_featured": False,
                "variants": [
                    {"size": "Infantil (até 12 anos)", "color": "Kids", "stock": 99},
                ],
            },
            {
                "title": "Cronograma de Tratamento: Nutrição & Reconstrução",
                "brand": brand_objs["Alquimia Capilar Olinda"],
                "category": cat_objs["Tratamentos & Cronograma Capilar"],
                "gender": "U",
                "price": 75.00,
                "compare_at_price": 85.00,
                "description": (
                    "Alquimia pura para recuperar a saúde dos fios pós-sol, praia ou química. Terapia capilar "
                    "com massagem estimulante no couro cabeludo e óleos vegetais nobres."
                ),
                "fabric_composition": "Blend de Óleos Naturais, Queratina e Manteiga de Karité",
                "care_instructions": "Devolve o brilho, maciez e vitalidade imediata aos fios.",
                "is_featured": False,
                "variants": [
                    {"size": "Sessão Intensiva", "color": "Spa Capilar", "stock": 99},
                ],
            },
        ]

        # Limpar produtos antigos de moda que foram importados de teste
        Product.objects.all().delete()

        for s_data in services_data:
            variants = s_data.pop("variants")
            prod = Product.objects.create(drop=drop_olinda, is_active=True, **s_data)
            for v_data in variants:
                ProductVariant.objects.create(
                    product=prod,
                    size=v_data["size"],
                    color=v_data["color"],
                    stock_quantity=v_data["stock"],
                )

        self.stdout.write(self.style.SUCCESS(f"✅ {len(services_data)} Serviços autorais cadastrados"))

        # 6. Slides de Carrossel (Hero Principal)
        CarouselSlide.objects.all().delete()
        CarouselSlide.objects.create(
            title="Cabeleireiro Eduardo Cardoso",
            subtitle="Laboratório Artístico e Ecossistema de Beleza no Sítio Histórico de Olinda.",
            badge_text="📍 Sítio Histórico de Olinda • Arte & Cultura",
            button_text="Conhecer Serviços & Agendar",
            button_url="/produtos/",
            slide_type="hero",
            order=1,
            overlay_darkness="medium",
        )
        CarouselSlide.objects.create(
            title="A Tesoura Não Tem Gênero",
            subtitle="Cortes personalizados para todas as gerações. Foco em traduzir a sua identidade com escuta atenta e respeito.",
            badge_text="✂️ Cortes Masculinos, Femininos & Infantis",
            button_text="Ver Catálogo de Cortes",
            button_url="/produtos/?category=cortes-personalizados",
            slide_type="hero",
            order=2,
            overlay_darkness="medium",
        )
        CarouselSlide.objects.create(
            title="Ritual da Barba & O Autêntico Nevou",
            subtitle="Alinhamento na toalha quente, cuidados faciais e a celebração da estética urbana olindense.",
            badge_text="🔥 Barboterapia & Alquimia Capilar",
            button_text="Agendar Procedimento",
            button_url="/pedidos/carrinho/",
            slide_type="hero",
            order=3,
            overlay_darkness="medium",
        )
        self.stdout.write(self.style.SUCCESS("✅ 3 Banners Hero criados com a identidade de Olinda"))

        # 7. Depoimentos de Clientes (Prova Social Olindense)
        CustomerReview.objects.all().delete()
        reviews = [
            {
                "name": "Rafael Mendonça",
                "location": "Sítio Histórico, Olinda - PE",
                "rating": 5,
                "comment": "Experiência única nas ladeiras de Olinda! O corte do Eduardo é uma verdadeira consultoria de identidade. A tesoura dele respeita o estilo de cada um com muita conversa boa e acolhimento.",
                "source": "google",
                "order": 1,
            },
            {
                "name": "Mariana Bezerra",
                "location": "Carmo, Olinda - PE",
                "rating": 5,
                "comment": "Ambiente maravilhoso, acolhedor e seguro. Eduardo tem uma sensibilidade rara para ouvir o que a gente quer. Meu corte ficou com uma leveza incrível!",
                "source": "instagram",
                "order": 2,
            },
            {
                "name": "Lucas Alencar",
                "location": "Recife - PE",
                "rating": 5,
                "comment": "O ritual da barba com toalha quente é uma pausa necessária na semana. E o 'nevou' que ele faz é diferenciado demais, cabelo super hidratado e com cor impecável.",
                "source": "whatsapp",
                "order": 3,
            },
        ]
        for r in reviews:
            CustomerReview.objects.create(is_active=True, **r)
        self.stdout.write(self.style.SUCCESS("✅ Depoimentos olindenses configurados"))

        # 8. Configuração Centralizada da Home (HomePageConfig)
        conf, _ = HomePageConfig.objects.get_or_create(id=1)
        conf.announcement_active = True
        conf.announcement_badge = "📍 OLINDA • PE"
        conf.announcement_text = "Sua identidade cuidada com arte, respeito e alma olindense • Agende seu horário no WhatsApp"
        conf.announcement_link = "https://wa.me/558183983355"

        # Cards de Destaque
        conf.women_card_badge = "✂️ Todas as Gerações"
        conf.women_card_title = "Cortes Personalizados"
        conf.women_card_subtitle = "A tesoura não tem gênero. Cortes masculinos, femininos e infantis traduzindo a sua essência."
        conf.women_card_url = "/produtos/?category=cortes-personalizados"
        conf.women_card_btn_text = "Explorar Cortes"

        conf.men_card_badge = "🔥 Barboterapia & Alquimia"
        conf.men_card_title = "Barba na Toalha Quente & Nevou"
        conf.men_card_subtitle = "Alinhamento preciso com toalha quente, tratamentos para a pele e o autêntico nevou da cultura urbana."
        conf.men_card_url = "/produtos/?category=barba-bigode-cuidados-faciais"
        conf.men_card_btn_text = "Ver Rituais & Cores"

        # Seção Sobre / O Laboratório
        conf.store_badge = "📍 Sítio Histórico de Olinda"
        conf.store_title = "Cabeleireiro Eduardo Cardoso: Laboratório Artístico"
        conf.store_description = (
            "Muito mais que um salão ou uma barbearia tradicional, o espaço do Cabeleireiro Eduardo Cardoso "
            "é um autêntico laboratório artístico fincado nas ladeiras de Olinda. Construído com um propósito claro, "
            "o local funde um ecossistema completo de beleza com um ambiente de efervescência cultural. "
            "Aqui, a arte do cuidado pessoal se encontra com a riqueza da cultura popular pernambucana."
        )
        conf.store_address = "Sítio Histórico de Olinda, Olinda - PE, Brasil"
        conf.store_phone = "+55 81 8398-3355"
        conf.store_instagram_handle = "@eduardo_vaka_"
        conf.store_maps_url = "https://maps.google.com/?q=Sitio+Historico+de+Olinda+PE"
        conf.store_hours_text = "Terça a Sábado: 09h às 19h • Agendamentos pelo WhatsApp"

        # 4 Diferenciais
        conf.benefit1_icon = "solar:cup-star-bold-duotone"
        conf.benefit1_title = "Acolhimento & Cultura"
        conf.benefit1_subtitle = "Refúgio seguro, humano e radicalmente inclusivo nas ladeiras de Olinda"

        conf.benefit2_icon = "solar:users-group-rounded-bold-duotone"
        conf.benefit2_title = "Atendimento Humanizado"
        conf.benefit2_subtitle = "Escuta atenta e respeito absoluto à individualidade de cada história"

        conf.benefit3_icon = "solar:scissors-square-bold-duotone"
        conf.benefit3_title = "A Tesoura Não Tem Gênero"
        conf.benefit3_subtitle = "Cortes masculinos, femininos e infantis para todas as gerações"

        conf.benefit4_icon = "solar:fire-bold-duotone"
        conf.benefit4_title = "Alquimia & Nevou"
        conf.benefit4_subtitle = "Barba na toalha quente, cor, química segura e expressão urbana"

        # Depoimentos & Compartilhamento
        conf.reviews_active = True
        conf.reviews_title = "O que Dizem Nossos Clientes"
        conf.reviews_subtitle = "Sua identidade cuidada com arte, respeito e alma olindense."
        conf.og_share_title = "Cabeleireiro Eduardo Cardoso | Laboratório Artístico e Ecossistema de Beleza (Olinda - PE)"

        conf.save()
        self.stdout.write(self.style.SUCCESS("✅ Configurações da Página Inicial salvas com sucesso!"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Ecossistema de Eduardo Cardoso inicializado com sucesso total!"))

from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from larkon.catalog.models import (
    Brand,
    Category,
    Drop,
    Product,
    ProductVariant,
    ProductImage,
    CarouselSlide,
    CustomerReview,
    HomePageConfig,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com a identidade, serviços, ambiente e a Grife Da Lá D'eira da Vakaria em Olinda"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("💈 Iniciando o Seed da Vakaria & Grife Da Lá D'eira (Olinda - PE)..."))

        # 1. Superuser
        if not User.objects.filter(email="admin@vakaria.com.br").exists():
            User.objects.create_superuser("admin@vakaria.com.br", "admin123", name="Eduardo Cardoso")
            self.stdout.write(self.style.SUCCESS("✅ Superusuário criado: admin@vakaria.com.br / admin123"))

        # 2. Marcas Oficiais da Vakaria & Grife Da Lá D'eira
        brands_data = [
            {
                "name": "Grife Da Lá D'eira",
                "slug": "da-la-deira",
                "description": "Moda autoral, streetwear, bonés e cosméticos de barbearia inspirados na alma das ladeiras de Olinda.",
            },
            {
                "name": "Eduardo Cardoso Atelier",
                "slug": "eduardo-cardoso-atelier",
                "description": "Atendimento autoral com corte e visagismo personalizado no Sítio Histórico de Olinda.",
            },
            {
                "name": "Vakaria Barbearia",
                "slug": "vakaria-barbearia",
                "description": "Alinhamento preciso, toalha quente e cuidados masculinos para relaxamento pleno.",
            },
            {
                "name": "Alquimia Capilar Olinda",
                "slug": "alquimia-capilar-olinda",
                "description": "Cor, mechas, relaxamento seguro e a autêntica arte do 'nevou' olindense.",
            },
        ]

        brand_objs = {}
        for b_data in brands_data:
            slug = b_data.pop("slug")
            brand, _ = Brand.objects.update_or_create(
                slug=slug,
                defaults={"name": b_data["name"], "description": b_data["description"], "is_active": True}
            )
            brand_objs[slug] = brand
        self.stdout.write(self.style.SUCCESS(f"✅ {len(brand_objs)} Marcas/Linhas configuradas"))

        # 3. Categorias Principais
        # Categorias Pai
        cat_cortes, _ = Category.objects.update_or_create(
            slug="cortes-visagismo",
            defaults={"name": "Cortes & Visagismo", "gender_target": "U", "order": 1, "icon": "solar:scissors-square-bold-duotone", "is_active": True}
        )
        cat_barba, _ = Category.objects.update_or_create(
            slug="barba-rituais",
            defaults={"name": "Barba & Rituais", "gender_target": "M", "order": 2, "icon": "solar:shield-user-bold-duotone", "is_active": True}
        )
        cat_quimica, _ = Category.objects.update_or_create(
            slug="alquimia-capilar-cor",
            defaults={"name": "Alquimia Capilar & Cor", "gender_target": "U", "order": 3, "icon": "solar:fire-bold-duotone", "is_active": True}
        )
        cat_grife, _ = Category.objects.update_or_create(
            slug="grife-da-la-deira",
            defaults={"name": "Grife Da Lá D'eira", "gender_target": "U", "order": 4, "icon": "solar:t-shirt-bold-duotone", "is_active": True}
        )

        subcats = [
            # Cortes
            ("Cortes Masculinos Autorais", "cortes-masculinos-autorais", "M", cat_cortes, 1),
            ("Cortes Femininos & Visagismo", "cortes-femininos-visagismo", "F", cat_cortes, 2),
            ("Cortes Infantis & Juvenis", "cortes-infantis-juvenis", "U", cat_cortes, 3),
            # Barba
            ("Ritual da Barba com Toalha Quente", "ritual-barba-toalha-quente", "M", cat_barba, 1),
            ("Alinhamento & Design de Barba", "alinhamento-design-barba", "M", cat_barba, 2),
            ("Combo Cabelo & Barba Completa", "combo-cabelo-barba", "M", cat_barba, 3),
            # Alquimia
            ("O Autêntico Nevou Olindense", "nevou-olindense", "U", cat_quimica, 1),
            ("Coloração Artística & Mechas", "coloracao-artistica-mechas", "U", cat_quimica, 2),
            ("Cronograma & Tratamentos Capilares", "cronograma-tratamentos-capilares", "U", cat_quimica, 3),
            # Grife Da Lá D'eira
            ("Camisetas & Streetwear Olinda", "camisetas-streetwear-olinda", "U", cat_grife, 1),
            ("Acessórios das Ladeiras", "acessorios-das-ladeiras", "U", cat_grife, 2),
            ("Pomadas & Cuidados Barber", "pomadas-cuidados-barber", "U", cat_grife, 3),
        ]

        cat_objs = {}
        for name, slug, gender, parent, order in subcats:
            cat, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "gender_target": gender, "parent": parent, "order": order, "is_active": True}
            )
            cat_objs[slug] = cat
        self.stdout.write(self.style.SUCCESS("✅ Categorias e Subcategorias da Vakaria & Grife Da Lá D'eira configuradas"))

        # Desativar categorias antigas de teste que não fazem mais parte do escopo
        valid_slugs = ["cortes-visagismo", "barba-rituais", "alquimia-capilar-cor", "grife-da-la-deira"] + [s[1] for s in subcats]
        Category.objects.exclude(slug__in=valid_slugs).update(is_active=False)

        # 4. Drop
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

        # 5. Catálogo de Produtos & Serviços
        products_data = [
            # SERVIÇOS ✂️
            {
                "title": "Corte Autoral Eduardo Cardoso (Todas as Gerações)",
                "brand": brand_objs["eduardo-cardoso-atelier"],
                "category": cat_objs["cortes-masculinos-autorais"],
                "gender": "U",
                "price": 50.00,
                "compare_at_price": 60.00,
                "description": (
                    "A tesoura não tem gênero. Atendimento humanizado e visagismo que traduz sua personalidade. "
                    "Inclui lavagem, corte autoral milimétrico e finalização com pomada Da Lá D'eira."
                ),
                "fabric_composition": "Visagismo, Tesoura & Navalha",
                "care_instructions": "Manutenção recomendada a cada 20 a 30 dias.",
                "image_path": "products/corte_autoral_masculino.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "Tradicional / Social", "color": "Autoral", "stock": 99},
                    {"size": "Moderno / Fade", "color": "Autoral", "stock": 99},
                ],
            },
            {
                "title": "Corte Feminino Personalizado & Visagismo",
                "brand": brand_objs["eduardo-cardoso-atelier"],
                "category": cat_objs["cortes-femininos-visagismo"],
                "gender": "F",
                "price": 65.00,
                "compare_at_price": 75.00,
                "description": (
                    "Corte feito sob medida para realçar os traços e textura natural dos fios. "
                    "Leveza, movimento e harmonia com escuta atenta no ateliê de Olinda."
                ),
                "fabric_composition": "Corte a Seco ou Molhado com Finalização",
                "care_instructions": "Finalizado respeitando a curvatura do fio.",
                "image_path": "products/corte_feminino_visagismo.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "Curto / Pixie", "color": "Atelier", "stock": 99},
                    {"size": "Médio / Bob", "color": "Atelier", "stock": 99},
                    {"size": "Longo em Camadas", "color": "Atelier", "stock": 99},
                ],
            },
            {
                "title": "Corte Infantil & Juvenil com Acolhimento",
                "brand": brand_objs["eduardo-cardoso-atelier"],
                "category": cat_objs["cortes-infantis-juvenis"],
                "gender": "U",
                "price": 45.00,
                "compare_at_price": 50.00,
                "description": (
                    "Paciência, carinho e respeito ao tempo da criança. O momento do corte transformado "
                    "em uma experiência lúdica e leve no quintal de Olinda."
                ),
                "fabric_composition": "Ambiente Seguro, Afetivo e Pet Friendly",
                "care_instructions": "Sem pressa, com diálogo e total cuidado.",
                "image_path": "products/corte_infantil_juvenil.jpg",
                "is_featured": False,
                "variants": [
                    {"size": "Infantil (até 12 anos)", "color": "Kids", "stock": 99},
                ],
            },
            {
                "title": "Ritual da Barba na Toalha Quente & Óleos",
                "brand": brand_objs["vakaria-barbearia"],
                "category": cat_objs["ritual-barba-toalha-quente"],
                "gender": "M",
                "price": 45.00,
                "compare_at_price": 50.00,
                "description": (
                    "O ritual clássico de relaxamento. Aplicação de toalha quente no vapor aromático, "
                    "massagem facial, alinhamento preciso na navalha e hidratação com óleo Da Lá D'eira."
                ),
                "fabric_composition": "Toalha Quente, Óleos Nobres & Navalhete",
                "care_instructions": "Finalizado com pós-barba calmante refrescante.",
                "image_path": "products/ritual_barba_toalha.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "Barba Completa", "color": "Ritual VIP", "stock": 99},
                    {"size": "Desenho & Alinhamento", "color": "Ritual VIP", "stock": 99},
                ],
            },
            {
                "title": "Combo Completo: Corte Autoral + Ritual da Barba",
                "brand": brand_objs["vakaria-barbearia"],
                "category": cat_objs["combo-cabelo-barba"],
                "gender": "M",
                "price": 90.00,
                "compare_at_price": 105.00,
                "description": (
                    "A experiência completa do laboratório. Corte alinhado ao seu perfil + ritual da barba "
                    "com toalha quente e café especial passado na hora."
                ),
                "fabric_composition": "Visagismo + Ritual da Barba Completo",
                "care_instructions": "Duração média: 60 minutos de cuidado impecável.",
                "image_path": "products/combo_corte_barba.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "Sessão Completa", "color": "Olinda VIP", "stock": 99},
                ],
            },
            {
                "title": "O Autêntico Nevou Olindense — Descoloração Global",
                "brand": brand_objs["alquimia-capilar-olinda"],
                "category": cat_objs["nevou-olindense"],
                "gender": "U",
                "price": 120.00,
                "compare_at_price": 140.00,
                "description": (
                    "Celebrando o autêntico estilo 'nevou' da nossa cultura urbana. Descoloração segura com "
                    "proteção Plex anti-danos no couro cabeludo e matização platinada fria perfeita."
                ),
                "fabric_composition": "Descolorante Premium + Plex de Proteção",
                "care_instructions": "Acompanha orientação para manutenção e máscara de nutrição.",
                "image_path": "products/nevou_olindense.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "Cabelo Curto", "color": "Platinado Gelo", "stock": 99},
                    {"size": "Cabelo Médio", "color": "Platinado Gelo", "stock": 99},
                ],
            },
            {
                "title": "Cronograma de Tratamento: Nutrição & Reconstrução",
                "brand": brand_objs["alquimia-capilar-olinda"],
                "category": cat_objs["cronograma-tratamentos-capilares"],
                "gender": "U",
                "price": 75.00,
                "compare_at_price": 85.00,
                "description": (
                    "Alquimia pura para recuperar a saúde dos fios pós-sol, praia ou química. Terapia capilar "
                    "com massagem estimulante no couro cabeludo e óleos vegetais nobres."
                ),
                "fabric_composition": "Blend de Óleos Naturais & Manteiga de Karité",
                "care_instructions": "Devolve o brilho, maciez e vitalidade imediata aos fios.",
                "image_path": "products/tratamento_cronograma_capilar.png",
                "is_featured": False,
                "variants": [
                    {"size": "Sessão Intensiva", "color": "Spa Capilar", "stock": 99},
                ],
            },

            # GRIFE DA LÁ D'EIRA 👕💈
            {
                "title": "Camiseta Oversized Da Lá D'eira — Olinda Preta",
                "brand": brand_objs["da-la-deira"],
                "category": cat_objs["camisetas-streetwear-olinda"],
                "gender": "U",
                "price": 129.00,
                "compare_at_price": 149.00,
                "description": (
                    "A essência das ladeiras de Olinda em corte streetwear contemporâneo. 100% algodão pesado "
                    "penteado com estampa vintage 'Da Lá D'eira Olinda'. Gola canelada e caimento impecável."
                ),
                "fabric_composition": "100% Algodão Premium Heavyweight 240g",
                "care_instructions": "Lavar à mão ou ciclo delicado. Secar à sombra.",
                "image_path": "products/product_tshirt_daladeira.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "P", "color": "Preto Vintage", "stock": 15},
                    {"size": "M", "color": "Preto Vintage", "stock": 25},
                    {"size": "G", "color": "Preto Vintage", "stock": 20},
                    {"size": "GG", "color": "Preto Vintage", "stock": 10},
                ],
            },
            {
                "title": "Boné Dad Hat Bordado Da Lá D'eira — Vintage Charcoal",
                "brand": brand_objs["da-la-deira"],
                "category": cat_objs["acessorios-das-ladeiras"],
                "gender": "U",
                "price": 89.00,
                "compare_at_price": 99.00,
                "description": (
                    "Boné Dad Hat em sarja de algodão estonado com bordado de alta definição 'Da Lá D'eira'. "
                    "Fecho em fivela de latão envelhecido, aba curva e acabamento rústico com estética atemporal."
                ),
                "fabric_composition": "100% Sarja de Algodão Estonado com Bordado 3D",
                "care_instructions": "Limpeza suave com pano úmido.",
                "image_path": "products/product_bone_daladeira.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "Ajustável", "color": "Charcoal Estonado", "stock": 30},
                ],
            },
            {
                "title": "Pomada Modeladora Efeito Matte Da Lá D'eira (100ml)",
                "brand": brand_objs["da-la-deira"],
                "category": cat_objs["pomadas-cuidados-barber"],
                "gender": "U",
                "price": 55.00,
                "compare_at_price": 65.00,
                "description": (
                    "Fixação forte com acabamento 100% fosco (sem brilho). Ideal para penteados texturizados, "
                    "cortes autorais e finalização diária. À base de água, sai facilmente no banho sem deixar resíduos."
                ),
                "fabric_composition": "Argila Branca, Cera de Candelila & Extrato de Alecrim",
                "care_instructions": "Espalhe uma pequena quantidade nas mãos e aplique nos fios secos ou levemente úmidos.",
                "image_path": "products/product_pomada_matte.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "100ml", "color": "Matte Finish", "stock": 45},
                ],
            },
            {
                "title": "Óleo Hidratante para Barba Aromas de Olinda (30ml)",
                "brand": brand_objs["da-la-deira"],
                "category": cat_objs["pomadas-cuidados-barber"],
                "gender": "M",
                "price": 48.00,
                "compare_at_price": 55.00,
                "description": (
                    "Fórmula exclusiva com óleos vegetais de jojoba, argan e castanha-do-pará. Hidrata a barba, "
                    "elimina o frizz e perfuma com notas sutis de cravo, canela e cedro das ladeiras."
                ),
                "fabric_composition": "Blend 100% Vegetal Puro com Conta-Gotas",
                "care_instructions": "Aplique 3 a 5 gotas na palma das mãos e massageie da raiz às pontas da barba.",
                "image_path": "products/product_oleo_barba.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "30ml", "color": "Âmbar", "stock": 50},
                ],
            },
            {
                "title": "Balm Pós-Barba Refrescante & Hidratante Facial (80g)",
                "brand": brand_objs["da-la-deira"],
                "category": cat_objs["pomadas-cuidados-barber"],
                "gender": "U",
                "price": 45.00,
                "compare_at_price": 52.00,
                "description": (
                    "Acalma a pele imediatamente após o barbear. Fórmula leve com aloe vera, hortelã e camomila, "
                    "fechando os poros, combatendo a irritação e proporcionando frescor prolongado."
                ),
                "fabric_composition": "Lata de Alumínio Retrô com Aloe Vera & Mentol Natural",
                "care_instructions": "Aplique sobre o rosto e pescoço massageando suavemente após o barbear.",
                "image_path": "products/product_balm_posbarba.jpg",
                "is_featured": True,
                "variants": [
                    {"size": "80g", "color": "Refrescante", "stock": 40},
                ],
            },
        ]

        # Resetar produtos
        Product.objects.all().delete()

        for p_data in products_data:
            variants = p_data.pop("variants")
            image_path = p_data.pop("image_path")
            prod = Product.objects.create(drop=drop_olinda, is_active=True, **p_data)
            
            # Criar Imagem Principal
            ProductImage.objects.create(
                product=prod,
                image=image_path,
                alt_text=prod.title,
                is_cover=True,
                order=1,
            )

            # Criar Variantes
            for v_data in variants:
                ProductVariant.objects.create(
                    product=prod,
                    size=v_data["size"],
                    color=v_data["color"],
                    stock_quantity=v_data["stock"],
                )

        self.stdout.write(self.style.SUCCESS(f"✅ {len(products_data)} Produtos e Serviços com imagens cadastrados com sucesso!"))

        # 6. Slides de Carrossel (Hero Principal)
        CarouselSlide.objects.all().delete()
        CarouselSlide.objects.create(
            title="A Arte do Cuidado nas Ladeiras de Olinda",
            subtitle="Espaço acolhedor, cortes autorais e respeito à sua essência em pleno Sítio Histórico.",
            badge_text="💈 Cabeleireiro Eduardo Cardoso",
            button_text="Agendar Horário",
            button_url="/agenda/",
            slide_type="hero",
            order=1,
            overlay_darkness="medium",
            image_url="/static/images/vaka_hero_olinda.jpg",
        )
        CarouselSlide.objects.create(
            title="Cortes Autorais & Visagismo Humanizado",
            subtitle="A tesoura não tem gênero. Cuidado sob medida para quem busca expressar sua verdadeira identidade.",
            badge_text="✂️ Cortes de Todas as Gerações",
            button_text="Explorar Serviços",
            button_url="/produtos/?category=cortes-visagismo",
            slide_type="hero",
            order=2,
            overlay_darkness="medium",
            image_url="/static/images/hero_cut_inclusive.jpg",
        )
        CarouselSlide.objects.create(
            title="Ritual da Barba & O Autêntico Nevou",
            subtitle="Alinhamento na toalha quente, cuidados faciais e a celebração da estética urbana olindense.",
            badge_text="🔥 Ritual da Barba & Alquimia Capilar",
            button_text="Agendar Procedimento",
            button_url="/agenda/",
            slide_type="hero",
            order=3,
            overlay_darkness="medium",
            image_url="/static/images/hero_barber_towel.jpg",
        )
        self.stdout.write(self.style.SUCCESS("✅ 3 Banners Hero criados com a identidade de Olinda"))

        # 7. Depoimentos
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
                "comment": "O ritual da barba com toalha quente é uma pausa necessária na semana. E a pomada Da Lá D'eira é surreal de boa, fixa sem brilho nenhum.",
                "source": "whatsapp",
                "order": 3,
            },
        ]
        for r in reviews:
            CustomerReview.objects.create(is_active=True, **r)
        self.stdout.write(self.style.SUCCESS("✅ Depoimentos configurados"))

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
        conf.women_card_url = "/produtos/?category=cortes-visagismo"
        conf.women_card_btn_text = "Explorar Cortes"

        conf.men_card_badge = "🔥 Barba & Alquimia"
        conf.men_card_title = "Barba na Toalha Quente & Nevou"
        conf.men_card_subtitle = "Alinhamento preciso com toalha quente, tratamentos para a pele e o autêntico nevou da cultura urbana."
        conf.men_card_url = "/produtos/?category=barba-rituais"
        conf.men_card_btn_text = "Ver Rituais & Cores"

        conf.store_badge = "📍 Sítio Histórico de Olinda"
        conf.store_title = "Cabeleireiro Eduardo Cardoso: Laboratório Artístico"
        conf.store_description = (
            "Muito mais que um salão ou barbearia convencional: um laboratório artístico e humano nas ladeiras de Olinda. "
            "Aqui a tesoura não tem gênero, o atendimento é acolhedor e a sua identidade é tratada como arte."
        )
        conf.store_address = "Sítio Histórico de Olinda, Olinda - PE, Brasil"
        conf.store_phone = "+55 81 8398-3355"
        conf.store_instagram_handle = "@eduardo_vaka_"
        conf.store_hours_text = "Terça a Sábado: 09h às 19h (Com agendamento prévio)"
        conf.save()

        self.stdout.write(self.style.SUCCESS("🚀 Seed da Vakaria & Grife Da Lá D'eira concluído com total sucesso!"))

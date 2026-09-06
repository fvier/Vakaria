from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from larkon.catalog.models import Brand, Category, Drop, Product, ProductVariant, ProductImage

User = get_user_model()


class Command(BaseCommand):
    help = "Popula o banco de dados com marcas, categorias, drops e peças de moda da Vakaria"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🌱 Iniciando o Seed de Moda da Vakaria..."))

        # 1. Superuser
        if not User.objects.filter(email="admin@vakaria.com.br").exists():
            User.objects.create_superuser("admin@vakaria.com.br", "admin123", name="Administrador Vakaria")
            self.stdout.write(self.style.SUCCESS("✅ Superusuário criado: admin@vakaria.com.br / admin123"))

        # 2. Marcas Multimarcas
        brands_data = [
            {"name": "Animale", "description": "Sofisticação, estampas marcantes e alfaiataria premium feminina."},
            {"name": "Osklen", "description": "Moda sustentável, design contemporâneo e estilo casual chic."},
            {"name": "Farm Rio", "description": "Cores vivas, estampas tropicais exclusivas e alma carioca."},
            {"name": "Reserva", "description": "Autenticidade, alta qualidade em camisaria e básicos masculinos premium."},
            {"name": "Ricardo Almeida", "description": "O ápice da alfaiataria e alta costura masculina contemporânea."},
            {"name": "John John", "description": "Denimwear de luxo, moda jovem sofisticada e atitude urbana."},
            {"name": "Schutz", "description": "Calçados, bolsas e acessórios de design inovador e exclusivo."},
        ]

        brand_objs = {}
        for b_data in brands_data:
            brand, _ = Brand.objects.get_or_create(name=b_data["name"], defaults={"description": b_data["description"]})
            brand_objs[b_data["name"]] = brand
        self.stdout.write(self.style.SUCCESS(f"✅ {len(brand_objs)} Marcas cadastradas"))

        # 3. Categorias Principais
        cat_fem, _ = Category.objects.get_or_create(name="Moda Feminina", gender_target="F", defaults={"order": 1})
        cat_masc, _ = Category.objects.get_or_create(name="Moda Masculina", gender_target="M", defaults={"order": 2})
        cat_acess, _ = Category.objects.get_or_create(name="Acessórios & Bolsas", gender_target="U", defaults={"order": 3})

        subcats = [
            ("Vestidos & Macacões", "F", cat_fem),
            ("Alfaiataria Feminina", "F", cat_fem),
            ("Camisas & Tops", "F", cat_fem),
            ("Camisaria & Polos", "M", cat_masc),
            ("Alfaiataria Masculina", "M", cat_masc),
            ("Calças & Bermudas", "M", cat_masc),
            ("Bolsas & Calçados", "U", cat_acess),
        ]

        cat_objs = {}
        for name, gender, parent in subcats:
            cat, _ = Category.objects.get_or_create(name=name, gender_target=gender, defaults={"parent": parent})
            cat_objs[name] = cat
        self.stdout.write(self.style.SUCCESS("✅ Categorias Feminina, Masculina e Acessórios configuradas"))

        # 4. Drops Bi-Semanais
        drop_terca, _ = Drop.objects.get_or_create(
            title="Drop Terça #01 — Exclusividades Primavera & Resort",
            defaults={
                "edition": "DROP-2026-W36-TUE",
                "launch_date": date(2026, 9, 1),
                "description": "Seleção especial com linho puro, sedas e cores vibrantes para elevar sua estação.",
                "is_featured": True,
            }
        )

        drop_quinta, _ = Drop.objects.get_or_create(
            title="Drop Quinta #02 — Alfaiataria Noturna & Eventos",
            defaults={
                "edition": "DROP-2026-W36-THU",
                "launch_date": date(2026, 9, 3),
                "description": "Cortes precisos, blazers estruturados e vestidos de gala exclusivos.",
                "is_featured": True,
            }
        )
        self.stdout.write(self.style.SUCCESS("✅ Drops Bi-semanais criados"))

        # 5. Peças de Moda (Produtos)
        products_data = [
            {
                "title": "Vestido Midi Seda Estampa Jardim Tropical",
                "brand": brand_objs["Farm Rio"],
                "category": cat_objs["Vestidos & Macacões"],
                "drop": drop_terca,
                "gender": "F",
                "price": 898.00,
                "compare_at_price": 1050.00,
                "description": "Vestido midi em seda pura com decote transpassado e estampa autoral exclusiva Farm Rio. Caimento fluido impecável.",
                "fabric_composition": "100% Seda Pura",
                "is_featured": True,
                "is_exclusive": True,
                "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=800&q=80",
                "variants": [
                    {"size": "P", "color": "Estampado", "sku": "FRM-VEST-P", "stock": 2},
                    {"size": "M", "color": "Estampado", "sku": "FRM-VEST-M", "stock": 3},
                    {"size": "G", "color": "Estampado", "sku": "FRM-VEST-G", "stock": 1},
                ]
            },
            {
                "title": "Blazer Alfaiataria Slim Fit Linho Areia",
                "brand": brand_objs["Ricardo Almeida"],
                "category": cat_objs["Alfaiataria Masculina"],
                "drop": drop_quinta,
                "gender": "M",
                "price": 2490.00,
                "compare_at_price": 2890.00,
                "description": "Blazer clássico desestruturado em puro linho italiano. Lapela notch, dois botões em madrepérola e forro interno em cetim maquinetado.",
                "fabric_composition": "100% Linho Italiano",
                "is_featured": True,
                "is_exclusive": True,
                "image_url": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80",
                "variants": [
                    {"size": "48 (M)", "color": "Areia Natural", "sku": "RA-BLAZ-48", "stock": 2},
                    {"size": "50 (G)", "color": "Areia Natural", "sku": "RA-BLAZ-50", "stock": 2},
                    {"size": "52 (GG)", "color": "Areia Natural", "sku": "RA-BLAZ-52", "stock": 1},
                ]
            },
            {
                "title": "Camisa Linho Puro Gola Padre Manga Longa",
                "brand": brand_objs["Osklen"],
                "category": cat_objs["Camisaria & Polos"],
                "drop": drop_terca,
                "gender": "M",
                "price": 647.00,
                "compare_at_price": 720.00,
                "description": "Camisa masculina de linho nobre com gola padre. Toque suave e modelagem comfort contemporânea.",
                "fabric_composition": "100% Linho Europeu Certificado",
                "is_featured": True,
                "is_exclusive": False,
                "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=800&q=80",
                "variants": [
                    {"size": "P", "color": "Branco Off", "sku": "OSK-CAM-P", "stock": 4},
                    {"size": "M", "color": "Branco Off", "sku": "OSK-CAM-M", "stock": 5},
                    {"size": "G", "color": "Branco Off", "sku": "OSK-CAM-G", "stock": 3},
                ]
            },
            {
                "title": "Conjunto Alfaiataria Blazer Cropped & Calça Wide Leg",
                "brand": brand_objs["Animale"],
                "category": cat_objs["Alfaiataria Feminina"],
                "drop": drop_quinta,
                "gender": "F",
                "price": 1890.00,
                "compare_at_price": 2190.00,
                "description": "Conjunto sofisticado em crepe acetinado. Blazer cropped com ombreiras estruturadas e calça wide leg de cintura alta com pregas frontais.",
                "fabric_composition": "78% Acetato, 22% Viscose",
                "is_featured": True,
                "is_exclusive": True,
                "image_url": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80",
                "variants": [
                    {"size": "36 (PP)", "color": "Preto Noite", "sku": "ANM-CONJ-36", "stock": 1},
                    {"size": "38 (P)", "color": "Preto Noite", "sku": "ANM-CONJ-38", "stock": 2},
                    {"size": "40 (M)", "color": "Preto Noite", "sku": "ANM-CONJ-40", "stock": 2},
                ]
            },
            {
                "title": "Bolsa Couro Legítimo Estruturada com Alça Corrente",
                "brand": brand_objs["Schutz"],
                "category": cat_objs["Bolsas & Calçados"],
                "drop": drop_terca,
                "gender": "U",
                "price": 1250.00,
                "compare_at_price": 1390.00,
                "description": "Bolsa tiracolo em couro nobre trabalhado com fecho banhado a ouro e acabamento impecável.",
                "fabric_composition": "100% Couro Bovino Premium",
                "is_featured": True,
                "is_exclusive": True,
                "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=800&q=80",
                "variants": [
                    {"size": "Único", "color": "Caramelo", "sku": "STZ-BAG-CAR", "stock": 3},
                    {"size": "Único", "color": "Preto", "sku": "STZ-BAG-BLK", "stock": 2},
                ]
            },
            {
                "title": "Polo Pima Cotton Touch Super Soft",
                "brand": brand_objs["Reserva"],
                "category": cat_objs["Camisaria & Polos"],
                "drop": drop_terca,
                "gender": "M",
                "price": 389.00,
                "compare_at_price": 420.00,
                "description": "Camisa polo confeccionada em algodão Pima peruano com toque extra macio e logo minimalista bordado no peito.",
                "fabric_composition": "100% Algodão Pima Peruano",
                "is_featured": False,
                "is_exclusive": False,
                "image_url": "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?auto=format&fit=crop&w=800&q=80",
                "variants": [
                    {"size": "P", "color": "Azul Marinho", "sku": "RSV-POL-P", "stock": 4},
                    {"size": "M", "color": "Azul Marinho", "sku": "RSV-POL-M", "stock": 6},
                    {"size": "G", "color": "Azul Marinho", "sku": "RSV-POL-G", "stock": 5},
                    {"size": "GG", "color": "Azul Marinho", "sku": "RSV-POL-GG", "stock": 2},
                ]
            },
        ]

        for p_data in products_data:
            variants = p_data.pop("variants")
            image_url = p_data.pop("image_url")
            product, created = Product.objects.get_or_create(
                title=p_data["title"],
                defaults=p_data
            )
            if created:
                ProductImage.objects.create(
                    product=product,
                    image_url=image_url,
                    alt_text=product.title,
                    is_cover=True,
                    order=1
                )
                for var in variants:
                    ProductVariant.objects.create(
                        product=product,
                        size=var["size"],
                        color=var["color"],
                        sku=var["sku"],
                        stock_quantity=var["stock"],
                    )
        self.stdout.write(self.style.SUCCESS(f"✅ {len(products_data)} Peças de moda exclusivas cadastradas com variações e fotos"))

        self.stdout.write(self.style.SUCCESS("\n🎉 Seed da Vakaria concluído com sucesso total!"))

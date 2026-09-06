import pytest
from decimal import Decimal
from django.urls import reverse
from django.test import Client
from larkon.users.models import User
from larkon.catalog.models import Brand, Category, Drop, Product, CarouselSlide, LinktreeItem, HomePageConfig
from larkon.orders.models import ProductReservation


@pytest.mark.django_db
class TestVakariaFlow:
    def test_landing_page_loads(self, client: Client):
        response = client.get(reverse("catalog:home"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Vakaria" in content
        assert "558183983355" in content

    def test_catalog_and_brands_load(self, client: Client):
        res_prod = client.get(reverse("catalog:product_grid"))
        assert res_prod.status_code == 200

        res_brands = client.get(reverse("catalog:brand_list"))
        assert res_brands.status_code == 200

    def test_cart_loads(self, client: Client):
        response = client.get(reverse("orders:cart"))
        assert response.status_code == 200

    def test_login_page_renders_cleanly(self, client: Client):
        response = client.get(reverse("account_login"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Vakaria" in content
        assert "toggle-password" in content
        assert "Cockpit Comercial" in content

    def test_direct_email_password_login(self, client: Client):
        user = User.objects.create_user(
            email="testuser@vakaria.com.br",
            password="testpassword123",
            name="Test User",
        )
        response = client.post(
            reverse("account_login"),
            {"login": "testuser@vakaria.com.br", "password": "testpassword123"},
            follow=True,
        )
        assert response.status_code == 200
        assert response.redirect_chain[0][0] == reverse("pages:dashboard")

    def test_dashboard_welcome_arena_loads(self, client: Client):
        user = User.objects.create_user(
            email="admin_test@vakaria.com.br",
            password="password123",
            name="Admin User",
            is_staff=True,
        )
        client.force_login(user)
        response = client.get(reverse("pages:dashboard"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Arena de Vendas & Performance" in content
        assert "Faturamento da Equipe" in content
        assert "Vakaria ERP" in content

    def test_linktree_public_page_and_click_tracking(self, client: Client):
        item = LinktreeItem.objects.create(
            title="WhatsApp VIP Teste",
            url="https://wa.me/558183983355",
            style="success",
            is_active=True,
            order=1,
        )
        # Test public page loads
        response = client.get("/links/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Vakaria Barbearia" in content
        assert "WhatsApp VIP Teste" in content

        # Test click tracking redirect
        click_res = client.get(reverse("pages:linktree_click", kwargs={"pk": item.pk}))
        assert click_res.status_code == 302
        assert click_res.url == "https://wa.me/558183983355"
        item.refresh_from_db()
        assert item.clicks_count == 1

        # Test Luiza Fit dedicated /tree page
        luiza_tree_res = client.get("/tree/")
        assert luiza_tree_res.status_code == 200
        luiza_content = luiza_tree_res.content.decode("utf-8")
        assert "Luiza Fit" in luiza_content
        assert "99341-3058" in luiza_content
        assert "useluizafit" in luiza_content
        assert "logoluiza.png" in luiza_content

    def test_brand_showroom_and_filter_flow(self, client: Client):
        # Create test brands
        nike, _ = Brand.objects.get_or_create(name="Nike", slug="nike", is_active=True)
        lacoste, _ = Brand.objects.get_or_create(name="Lacoste", slug="lacoste", is_active=True)
        ck, _ = Brand.objects.get_or_create(name="Calvin Klein", slug="calvin-klein", is_active=True)
        tommy, _ = Brand.objects.get_or_create(name="Tommy Hilfiger", slug="tommy-hilfiger", is_active=True)
        caunt, _ = Brand.objects.get_or_create(name="Caunt Jeans", slug="caunt-jeans", is_active=True)

        # Test Brand Showroom page loads
        response = client.get(reverse("catalog:brand_list"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Marcas Oficiais" in content
        assert "Nike" in content
        assert "Calvin Klein" in content
        assert "Tommy Hilfiger" in content
        assert "Caunt Jeans" in content
        assert "calvin-klein.png" in content
        assert "tommy-hilfiger.png" in content
        assert "caunt-jeans.png" in content

        # Test Brand Filter in Product Grid
        grid_res = client.get("/produtos/?brand=calvin-klein")
        assert grid_res.status_code == 200
        grid_content = grid_res.content.decode("utf-8")
        assert "Calvin Klein" in grid_content

    def test_quick_edit_product_and_stock_flow(self, client: Client):
        from larkon.catalog.models import ProductVariant, ProductImage
        from django.core.files.uploadedfile import SimpleUploadedFile

        brand, _ = Brand.objects.get_or_create(name="Nike", slug="nike", is_active=True)
        cat, _ = Category.objects.get_or_create(name="Camisas", slug="camisas", is_active=True)
        product = Product.objects.create(
            title="Camisa Nike Dri-FIT Original",
            slug="camisa-nike-dri-fit",
            brand=brand,
            category=cat,
            price=199.90,
            gender="M",
            is_active=True,
        )
        ProductVariant.objects.create(
            product=product,
            size="M",
            stock_quantity=10,
            sku="nike-m-01"
        )

        admin = User.objects.create_user(
            email="staff_editor@vakaria.com.br",
            password="password123",
            name="Staff Editor",
            is_staff=True,
        )
        client.force_login(admin)

        # 1. Fetch Edit Data
        data_res = client.get(reverse("catalog:product_edit_data", kwargs={"pk": product.id}))
        assert data_res.status_code == 200
        data_json = data_res.json()
        assert data_json["title"] == "Camisa Nike Dri-FIT Original"
        assert "M" in data_json["sizes"]
        assert data_json["is_in_stock"] is True

        # 2. Quick Edit POST: update title, price, add sizes (P, M, G, GG, 40)
        image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82"
        uploaded_img = SimpleUploadedFile("nova_foto.png", image_content, content_type="image/png")

        edit_res = client.post(
            reverse("catalog:quick_edit_product", kwargs={"pk": product.id}),
            {
                "title": "Camisa Nike Dri-FIT Pro Editada",
                "price": "249,90",
                "brand": brand.id,
                "category": cat.id,
                "gender": "M",
                "is_in_stock": "1",
                "sizes": ["P", "M", "G", "GG", "40", "39/40"],
                "cover_image": uploaded_img,
                "ajax": "1",
            }
        )
        assert edit_res.status_code == 200
        assert edit_res.json()["success"] is True

        # Refresh from DB
        product.refresh_from_db()
        assert product.title == "Camisa Nike Dri-FIT Pro Editada"
        assert float(product.price) == 249.90
        assert product.cover_image is not None
        assert set(product.variants.filter(stock_quantity__gt=0).values_list("size", flat=True)) == {"P", "M", "G", "GG", "40", "39/40"}

        # 3. Test mark as Esgotado / Out of Stock
        edit_esgotado = client.post(
            reverse("catalog:quick_edit_product", kwargs={"pk": product.id}),
            {
                "title": "Camisa Nike Dri-FIT Pro Editada",
                "price": "249,90",
                "brand": brand.id,
                "category": cat.id,
                "gender": "M",
                "sizes": ["M"],
                "ajax": "1",
            }
        )
        assert edit_esgotado.status_code == 200
        product.refresh_from_db()
        assert product.in_stock is False
        assert product.total_stock == 0

    def test_admin_carousel_and_linktree_management(self, client: Client):
        user = User.objects.create_user(
            email="gestor@vakaria.com.br",
            password="password123",
            name="Gestor Loja",
            is_staff=True,
        )
        client.force_login(user)

        # Test Carousel Admin
        car_res = client.get(reverse("pages:admin_carousel"))
        assert car_res.status_code == 200
        assert "Gerenciador de Banners" in car_res.content.decode("utf-8")

        # Test Create Carousel Slide via POST
        post_slide = client.post(
            reverse("pages:admin_carousel"),
            {
                "title": "Drop Verão Exclusivo",
                "subtitle": "Peças autorais limitadas",
                "badge_text": "✨ Novidade",
                "button_text": "Ver Coleção",
                "button_url": "/produtos/",
                "slide_type": "hero",
                "order": 1,
            },
            follow=True,
        )
        assert post_slide.status_code == 200
        assert CarouselSlide.objects.filter(title="Drop Verão Exclusivo").exists()

        # Test Linktree Admin default (Vakaria tab)
        link_res = client.get(reverse("pages:admin_linktree") + "?tab=vakaria")
        assert link_res.status_code == 200
        content_ghf = link_res.content.decode("utf-8")
        assert "Gerenciador de Linktree" in content_ghf
        assert "Vakaria Barbearia" in content_ghf
        assert "Luiza Fit" in content_ghf

        # Create link for Luiza Fit via POST
        create_luiza_res = client.post(
            reverse("pages:admin_linktree"),
            {
                "action": "create",
                "page_type": "luiza_fit",
                "title": "Conjuntos Fitness Sem Costura",
                "subtitle": "Tecnologia Seamless Premium",
                "url": "/produtos/?category=luiza-fit",
                "style": "rose",
                "icon": "bx bx-star",
                "order": 10,
                "is_highlighted": "1",
            },
            follow=True,
        )
        assert create_luiza_res.status_code == 200
        luiza_item = LinktreeItem.objects.filter(title="Conjuntos Fitness Sem Costura", page_type="luiza_fit").first()
        assert luiza_item is not None
        assert luiza_item.style == "rose"
        assert luiza_item.is_highlighted is True

        # Test Quick Data JSON endpoint
        data_res = client.get(reverse("pages:admin_linktree_data", kwargs={"pk": luiza_item.pk}))
        assert data_res.status_code == 200
        data_json = data_res.json()
        assert data_json["success"] is True
        assert data_json["title"] == "Conjuntos Fitness Sem Costura"
        assert data_json["page_type"] == "luiza_fit"

        # Edit link via POST
        edit_res = client.post(
            reverse("pages:admin_linktree"),
            {
                "action": "edit",
                "pk": luiza_item.pk,
                "page_type": "luiza_fit",
                "title": "Conjuntos Fitness Seamless Editado",
                "subtitle": "Alta Compressão e Zero Transparência",
                "url": "/produtos/?category=luiza-fit",
                "style": "champagne",
                "icon": "bx bx-store-alt",
                "order": 1,
            },
            follow=True,
        )
        assert edit_res.status_code == 200
        luiza_item.refresh_from_db()
        assert luiza_item.title == "Conjuntos Fitness Seamless Editado"
        assert luiza_item.style == "champagne"

        # Verify it appears on public /tree/
        public_tree = client.get("/tree/")
        assert public_tree.status_code == 200
        assert "Conjuntos Fitness Seamless Editado" in public_tree.content.decode("utf-8")

    def test_category_tree_hierarchy_and_filtering(self, client: Client):
        # Create brand
        brand = Brand.objects.create(name="Reserva")

        # Create parent category
        parent_cat = Category.objects.create(name="CAMISAS", slug="camisas", gender_target="M", order=1)
        
        # Create subcategories
        child_pima = Category.objects.create(name="MALHA PIMA LEGÍTIMA", slug="camisas-malha-pima-legitima", parent=parent_cat, gender_target="M", order=1)
        child_oversized = Category.objects.create(name="OVERSIZED", slug="camisas-oversized", parent=parent_cat, gender_target="M", order=2)

        # Create product in child category
        p1 = Product.objects.create(
            title="Camisa Pima Premium Black",
            slug="camisa-pima-premium-black",
            brand=brand,
            category=child_pima,
            price=249.90,
            gender="M",
            is_active=True,
        )

        p2 = Product.objects.create(
            title="Camisa Oversized Street",
            slug="camisa-oversized-street",
            brand=brand,
            category=child_oversized,
            price=199.90,
            gender="M",
            is_active=True,
        )

        # 1. Filter by parent category (CAMISAS) should return both child products
        res_parent = client.get(reverse("catalog:product_grid") + "?category=camisas")
        assert res_parent.status_code == 200
        content_parent = res_parent.content.decode("utf-8")
        assert "Camisa Pima Premium Black" in content_parent
        assert "Camisa Oversized Street" in content_parent
        assert "accordionVakaria" in content_parent
        assert "CAMISAS" in content_parent

        # 2. Filter by specific subcategory (MALHA PIMA) should only return p1
        res_child = client.get(reverse("catalog:product_grid") + "?category=camisas-malha-pima-legitima")
        assert res_child.status_code == 200
        content_child = res_child.content.decode("utf-8")
        assert "Camisa Pima Premium Black" in content_child
        assert "Camisa Oversized Street" not in content_child

    def test_quick_create_product_and_ajax_cart(self, client: Client):
        admin = User.objects.create_user(
            email="staff_tester@vakaria.com.br",
            password="password123",
            name="Staff Tester",
            is_staff=True,
        )
        client.force_login(admin)

        brand = Brand.objects.create(name="Hugo Boss")
        cat = Category.objects.create(name="MALHA PIMA", slug="camisas-malha-pima")

        # 1. Test quick create product via POST
        post_data = {
            "title": "Camisa Polo Hugo Boss Elegance",
            "price": "299,90",
            "brand": brand.id,
            "category": cat.id,
            "gender": "M",
            "sizes": ["P", "M", "G"],
            "colors": ["Preto", "Branco"],
            "is_exclusive": "1",
            "is_featured": "1",
        }
        res = client.post(reverse("catalog:quick_create_product"), post_data, follow=True)
        assert res.status_code == 200
        created_p = Product.objects.filter(title="Camisa Polo Hugo Boss Elegance").first()
        assert created_p is not None
        assert float(created_p.price) == 299.90
        # 3 sizes x 2 colors = 6 variants
        assert created_p.variants.count() == 6

        # 2. Test 1-click add to cart via AJAX
        cart_res = client.post(
            reverse("orders:add_to_cart"),
            {"product_id": created_p.id, "size": "M", "ajax": "1"},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert cart_res.status_code == 200
        data = cart_res.json()
        assert data["success"] is True
        assert data["cart_total_items"] == 1
        assert "Camisa Polo Hugo Boss Elegance" in data["message"]

        # 3. Test that admin bar, modals and color-size matrix containers render for staff user
        grid_res = client.get(reverse("catalog:product_grid"))
        assert grid_res.status_code == 200
        grid_html = grid_res.content.decode("utf-8")
        assert "Modo Administrador" in grid_html
        assert "quickProductModal" in grid_html
        assert "deleteProductModal" in grid_html
        assert "quickColorSizeMatrixContainer" in grid_html
        assert "editColorSizeMatrixContainer" in grid_html
        assert "MALHA PIMA" in grid_html

    def test_anonymous_cannot_create_or_delete_products(self, client: Client):
        brand = Brand.objects.create(name="Reserva")
        cat = Category.objects.create(name="Bermudas", slug="bermudas-reserva")
        p = Product.objects.create(title="Bermuda Reserva", slug="bermuda-reserva", brand=brand, category=cat, price=150.0)

        # Anonymous POST to quick_create should redirect to login
        res_create = client.post(reverse("catalog:quick_create_product"), {"title": "Hack Peça"})
        assert res_create.status_code in [302, 403]

        # Anonymous POST to quick_delete should redirect to login
        res_del = client.post(reverse("catalog:quick_delete_product", kwargs={"pk": p.id}), {"action": "delete"})
        assert res_del.status_code in [302, 403]
        assert Product.objects.filter(id=p.id).exists()

        # Anonymous view of grid should NOT contain admin buttons
        grid_res = client.get(reverse("catalog:product_grid"))
        grid_html = grid_res.content.decode("utf-8")
        assert "Modo Administrador" not in grid_html
        assert "btn-delete-product" not in grid_html
        assert "btn-edit-product" not in grid_html

    def test_staff_can_delete_and_archive_product(self, client: Client):
        admin = User.objects.create_user(
            email="admin_del@vakaria.com.br",
            password="password123",
            name="Admin Del",
            is_staff=True,
        )
        client.force_login(admin)

        brand = Brand.objects.create(name="Osklen")
        cat = Category.objects.create(name="Tênis", slug="tenis-osklen")
        p1 = Product.objects.create(title="Tênis Osklen Riva", slug="tenis-osklen-riva", brand=brand, category=cat, price=450.0, is_active=True)
        p2 = Product.objects.create(title="Tênis Osklen Soho", slug="tenis-osklen-soho", brand=brand, category=cat, price=490.0, is_active=True)

        # 1. Archive p1 (soft delete)
        res_archive = client.post(
            reverse("catalog:quick_delete_product", kwargs={"pk": p1.id}),
            {"action": "archive", "ajax": "1"},
            headers={"x-requested-with": "XMLHttpRequest"}
        )
        assert res_archive.status_code == 200
        p1.refresh_from_db()
        assert p1.is_active is False

        # 2. Hard delete p2
        res_delete = client.post(
            reverse("catalog:quick_delete_product", kwargs={"pk": p2.id}),
            {"action": "delete", "ajax": "1"},
            headers={"x-requested-with": "XMLHttpRequest"}
        )
        assert res_delete.status_code == 200
        assert not Product.objects.filter(id=p2.id).exists()

    def test_variants_matrix_and_color_image_flow(self, client: Client):
        import json
        brand, _ = Brand.objects.get_or_create(name="Hugo Boss", slug="hugo-boss", is_active=True)
        cat, _ = Category.objects.get_or_create(name="Camisas Pima", slug="camisas-pima", is_active=True)
        
        admin = User.objects.create_user(
            email="matrix_admin@vakaria.com.br",
            password="password123",
            name="Matrix Admin",
            is_staff=True,
        )
        client.force_login(admin)

        # 1. Cadastrar produto com matriz de variantes (Vermelho: P, M, G, GG | Azul: P, M, G)
        matrix_payload = [
            {
                "name": "Vermelho",
                "hex": "#ef4444",
                "sizes": [
                    {"size": "P", "stock": 2},
                    {"size": "M", "stock": 4},
                    {"size": "G", "stock": 1},
                    {"size": "GG", "stock": 2}
                ]
            },
            {
                "name": "Azul",
                "hex": "#2563eb",
                "sizes": [
                    {"size": "P", "stock": 1},
                    {"size": "M", "stock": 3},
                    {"size": "G", "stock": 2}
                ]
            }
        ]

        create_res = client.post(
            reverse("catalog:quick_create_product"),
            {
                "title": "Camisa Pima Hugo Boss Matrix",
                "price": "289,90",
                "brand": brand.id,
                "category": cat.id,
                "gender": "M",
                "variants_matrix_json": json.dumps(matrix_payload),
                "ajax": "1"
            },
            headers={"x-requested-with": "XMLHttpRequest"}
        )
        assert create_res.status_code == 200
        p_id = create_res.json()["product_id"]

        product = Product.objects.get(id=p_id)
        assert product.title == "Camisa Pima Hugo Boss Matrix"
        assert product.variants.count() == 7  # 4 do vermelho + 3 do azul
        assert product.variants.filter(color="Vermelho").count() == 4
        assert product.variants.filter(color="Azul").count() == 3

        # 2. Consultar JSON para Quick View
        view_res = client.get(reverse("catalog:product_edit_data", kwargs={"pk": p_id}))
        assert view_res.status_code == 200
        data = view_res.json()
        assert len(data["available_colors"]) == 2
        assert len(data["variants_matrix"]) == 2
        
        red_entry = next(c for c in data["variants_matrix"] if c["name"] == "Vermelho")
        assert len(red_entry["sizes"]) == 4
        
        blue_entry = next(c for c in data["variants_matrix"] if c["name"] == "Azul")
        assert len(blue_entry["sizes"]) == 3

    def test_product_reservation_and_crm_admin_flow(self, client: Client):
        from larkon.orders.models import ProductReservation

        brand, _ = Brand.objects.get_or_create(name="Lacoste", slug="lacoste", is_active=True)
        cat, _ = Category.objects.get_or_create(name="Polos", slug="polos", is_active=True)
        product = Product.objects.create(
            title="Camisa Polo Lacoste Classic Fit",
            slug="camisa-polo-lacoste-classic-fit",
            brand=brand,
            category=cat,
            price=399.90,
            gender="M",
            is_active=True,
        )

        # 1. Cliente público cria reserva via AJAX
        res_post = client.post(
            reverse("orders:create_reservation"),
            {
                "product_id": product.id,
                "customer_name": "Dr. Carlos Eduardo",
                "customer_phone": "(83) 99876-5432",
                "color": "Preto",
                "size": "GG",
                "notes": "Favor avisar assim que chegar o lote novo!",
            },
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert res_post.status_code == 200
        res_json = res_post.json()
        assert res_json["success"] is True
        assert "registrada com sucesso" in res_json["message"]

        reservation = ProductReservation.objects.get(id=res_json["reservation_id"])
        assert reservation.customer_name == "Dr. Carlos Eduardo"
        assert reservation.customer_phone == "(83) 99876-5432"
        assert reservation.color == "Preto"
        assert reservation.size == "GG"
        assert reservation.status == "pending"
        assert reservation.notified_at is None

        # 2. Verifica link VIP humanizado do WhatsApp
        wa_link = reservation.generate_whatsapp_vip_link()
        assert "wa.me/5583998765432" in wa_link
        assert "Camisa%20Polo%20Lacoste%20Classic%20Fit" in wa_link
        assert "24%20horas" in wa_link

        # 3. Usuário anônimo é bloqueado em /reservas/
        anon_res = client.get("/reservas/")
        assert anon_res.status_code in [302, 403]

        # 4. Staff acessa painel de reservas (/reservas/)
        staff = User.objects.create_user(
            email="staff_crm@vakaria.com.br",
            password="password123",
            name="Staff CRM",
            is_staff=True,
        )
        client.force_login(staff)

        admin_res = client.get("/reservas/")
        assert admin_res.status_code == 200
        admin_content = admin_res.content.decode("utf-8")
        assert "Fila de Espera &amp; Reservas de Peças" in admin_content or "Fila de Espera & Reservas de Peças" in admin_content
        assert "Dr. Carlos Eduardo" in admin_content
        assert "Camisa Polo Lacoste Classic Fit" in admin_content
        assert "Avisar Peça Chegou" in admin_content

        # 5. Staff atualiza status para 'notified'
        status_res = client.post(
            reverse("orders:update_reservation_status", kwargs={"pk": reservation.id}),
            {"status": "notified"},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert status_res.status_code == 200
        assert status_res.json()["success"] is True
        reservation.refresh_from_db()
        assert reservation.status == "notified"
        assert reservation.notified_at is not None

        # 6. Staff atualiza status para 'converted' (venda concluída)
        status_conv = client.post(
            reverse("orders:update_reservation_status", kwargs={"pk": reservation.id}),
            {"status": "converted"},
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert status_conv.status_code == 200
        reservation.refresh_from_db()
        assert reservation.status == "converted"

    def test_manual_order_creation_pos_whatsapp_flow(self, client: Client):
        import json
        from larkon.catalog.models import ProductVariant
        from larkon.orders.models import Order

        brand, _ = Brand.objects.get_or_create(name="Calvin Klein", slug="calvin-klein", is_active=True)
        cat, _ = Category.objects.get_or_create(name="Camisetas", slug="camisetas", is_active=True)
        product = Product.objects.create(
            title="Camiseta Calvin Klein Jeans Logo",
            slug="camiseta-calvin-klein-jeans-logo",
            brand=brand,
            category=cat,
            price=189.90,
            gender="M",
            is_active=True,
        )
        v_m = ProductVariant.objects.create(
            product=product,
            size="M",
            color="Preto",
            stock_quantity=5,
            sku="ck-preto-m",
        )
        v_g = ProductVariant.objects.create(
            product=product,
            size="G",
            color="Branco",
            stock_quantity=3,
            sku="ck-branco-g",
        )

        # 1. Usuário anônimo é bloqueado
        anon_get = client.get(reverse("orders:manual_order_create"))
        assert anon_get.status_code in [302, 403]

        # 2. Staff acessa tela de PDV
        staff = User.objects.create_user(
            email="staff_pos@vakaria.com.br",
            password="password123",
            name="Staff POS",
            is_staff=True,
        )
        client.force_login(staff)

        pos_page = client.get(reverse("orders:manual_order_create"))
        assert pos_page.status_code == 200
        content = pos_page.content.decode("utf-8")
        assert "Lançamento de Pedidos" in content
        assert "Camiseta Calvin Klein Jeans Logo" in content

        # 3. Staff cria pedido manual (2x Preto M + 1x Branco G)
        items_payload = [
            {
                "product_id": product.id,
                "variant_id": v_m.id,
                "size": "M",
                "color": "Preto",
                "quantity": 2,
                "unit_price": "189.90",
            },
            {
                "product_id": product.id,
                "variant_id": v_g.id,
                "size": "G",
                "color": "Branco",
                "quantity": 1,
                "unit_price": "189.90",
            }
        ]

        post_res = client.post(
            reverse("orders:manual_order_create"),
            {
                "customer_name": "Lucas Alencar",
                "customer_phone": "(83) 98888-7777",
                "payment_method": "pix",
                "delivery_method": "motoboy",
                "origin": "whatsapp",
                "status": "confirmed",
                "shipping_cost": "10.00",
                "discount": "15.00",
                "shipping_address": "Av. Presidente João Pessoa, 400 - Centro",
                "city": "Cajazeiras",
                "state": "PB",
                "notes": "Entregar até às 18h",
                "items_json": json.dumps(items_payload),
                "ajax": "1",
            },
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert post_res.status_code == 200
        res_data = post_res.json()
        assert res_data["success"] is True
        assert "order_number" in res_data
        assert "receipt_whatsapp_link" in res_data

        order = Order.objects.get(order_number=res_data["order_number"])
        assert order.customer_name == "Lucas Alencar"
        assert order.customer_phone == "(83) 98888-7777"
        assert order.payment_method == "pix"
        assert order.delivery_method == "motoboy"
        assert order.origin == "whatsapp"
        assert order.status == "confirmed"
        # Subtotal: 3x 189.90 = 569.70; Total: 569.70 + 10.00 - 15.00 = 564.70
        assert float(order.subtotal) == 569.70
        assert float(order.total) == 564.70
        assert order.items.count() == 2

        # 4. Verifica baixa automática no estoque
        v_m.refresh_from_db()
        v_g.refresh_from_db()
        assert v_m.stock_quantity == 3  # 5 - 2 = 3
        assert v_g.stock_quantity == 2  # 3 - 1 = 2

        # 5. Verifica link do comprovante com chave PIX
        receipt_link = order.generate_receipt_whatsapp_link()
        assert "wa.me/5583988887777" in receipt_link
        assert "Comprovante%20de%20Pedido" in receipt_link
        assert "Lucas%20Alencar" in receipt_link
        assert "8183983355" in receipt_link

    def test_crm_search_and_labels_and_reservation_conversion(self, client: Client):
        import json
        from larkon.catalog.models import ProductVariant
        from larkon.orders.models import Order, ProductReservation

        brand, _ = Brand.objects.get_or_create(name="Tommy Hilfiger", slug="tommy-hilfiger", is_active=True)
        cat, _ = Category.objects.get_or_create(name="Camisas", slug="camisas-th", is_active=True)
        product = Product.objects.create(
            title="Camisa Tommy Hilfiger Classic",
            slug="camisa-tommy-hilfiger-classic",
            brand=brand,
            category=cat,
            price=299.90,
            gender="M",
            is_active=True,
        )
        variant = ProductVariant.objects.create(
            product=product,
            size="G",
            color="Azul Marinho",
            stock_quantity=10,
            sku="th-marinho-g",
        )

        staff = User.objects.create_user(
            email="staff_advanced@vakaria.com.br",
            password="password123",
            name="Staff Advanced",
            is_staff=True,
        )
        client.force_login(staff)

        # 1. Cria um pedido anterior para alimentar o CRM
        prev_order = Order.objects.create(
            customer_name="Mariana Souza",
            customer_phone="(83) 99123-4567",
            shipping_address="Rua Padre Rolim, 150",
            city="Cajazeiras",
            state="PB",
            subtotal=299.90,
            total=299.90,
            status="delivered",
            origin="whatsapp",
        )

        # 2. Testa busca CRM por nome ou telefone
        search_res = client.get(reverse("orders:customer_search") + "?q=Mariana")
        assert search_res.status_code == 200
        search_json = search_res.json()
        assert len(search_json["customers"]) >= 1
        customer_info = search_json["customers"][0]
        assert customer_info["name"] == "Mariana Souza"
        assert customer_info["phone"] == "(83) 99123-4567"
        assert customer_info["shipping_address"] == "Rua Padre Rolim, 150"
        assert customer_info["total_orders"] >= 1
        assert float(customer_info["total_spent"]) >= 299.90

        # 3. Cria uma reserva prévia
        reservation = ProductReservation.objects.create(
            product=product,
            customer_name="Mariana Souza",
            customer_phone="(83) 99123-4567",
            color="Azul Marinho",
            size="G",
            status="pending",
        )

        # 4. Converte a reserva em venda através do PDV
        items_payload = [
            {
                "product_id": product.id,
                "variant_id": variant.id,
                "size": "G",
                "color": "Azul Marinho",
                "quantity": 1,
                "unit_price": "299.90",
            }
        ]

        conv_res = client.post(
            reverse("orders:manual_order_create"),
            {
                "customer_name": "Mariana Souza",
                "customer_phone": "(83) 99123-4567",
                "payment_method": "pix",
                "delivery_method": "correios",
                "shipping_cost": "25.00",
                "shipping_address": "Rua Padre Rolim, 150",
                "city": "Cajazeiras",
                "state": "PB",
                "reservation_id": reservation.id,
                "items_json": json.dumps(items_payload),
                "ajax": "1",
            },
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert conv_res.status_code == 200
        conv_json = conv_res.json()
        assert conv_json["success"] is True

        # Verifica se a reserva virou 'converted'
        reservation.refresh_from_db()
        assert reservation.status == "converted"

        new_order = Order.objects.get(order_number=conv_json["order_number"])

        # 5. Testa visualização e impressão da etiqueta de envio
        label_res = client.get(reverse("orders:order_label_print", kwargs={"order_number": new_order.order_number}))
        assert label_res.status_code == 200
        label_html = label_res.content.decode("utf-8")
        assert "VAKARIA" in label_html
        assert "Destinatário" in label_html
        assert "Mariana Souza" in label_html
        assert "Rua Padre Rolim, 150" in label_html
        assert "Azul Marinho" in label_html

        # 6. Testa disparo de status para WhatsApp
        status_res = client.get(
            reverse(
                "orders:order_status_whatsapp",
                kwargs={"order_number": new_order.order_number, "status_type": "shipped"},
            )
            + "?tracking_code=BR123456789PB",
            headers={"x-requested-with": "XMLHttpRequest"},
        )
        assert status_res.status_code == 200
        status_json = status_res.json()
        assert status_json["success"] is True
        assert "whatsapp_link" in status_json
        assert "BR123456789PB" in status_json["whatsapp_link"]
        assert "wa.me/5583991234567" in status_json["whatsapp_link"]

    def test_per_color_size_matrix_creation_and_filtering(self, client: Client):
        admin = User.objects.create_user(
            email="matrix_admin@vakaria.com.br",
            password="password123",
            name="Matrix Admin",
            is_staff=True,
        )
        client.force_login(admin)

        brand = Brand.objects.create(name="Lacoste", slug="lacoste")
        cat = Category.objects.create(name="Camisas Polo", slug="camisas-polo")

        import json
        matrix_payload = [
            {
                "name": "Preto",
                "hex": "#0f172a",
                "sizes": [
                    {"size": "P", "stock": 10},
                    {"size": "M", "stock": 5},
                    {"size": "G", "stock": 8}
                ]
            },
            {
                "name": "Azul Marinho",
                "hex": "#1e3a8a",
                "sizes": [
                    {"size": "G", "stock": 4},
                    {"size": "GG", "stock": 6}
                ]
            }
        ]

        post_data = {
            "title": "Polo Lacoste Pima Two Tone",
            "price": "349,90",
            "brand": brand.id,
            "category": cat.id,
            "gender": "M",
            "variants_matrix_json": json.dumps(matrix_payload),
            "is_in_stock": "1",
        }
        res = client.post(reverse("catalog:quick_create_product"), post_data, follow=True)
        assert res.status_code == 200

        product = Product.objects.filter(title="Polo Lacoste Pima Two Tone").first()
        assert product is not None
        # Preto has 3 sizes (P, M, G), Azul Marinho has 2 sizes (G, GG) -> 5 variants total
        assert product.variants.count() == 5
        
        preto_sizes = list(product.variants.filter(color="Preto").values_list("size", flat=True))
        assert set(preto_sizes) == {"P", "M", "G"}

        marinho_sizes = list(product.variants.filter(color="Azul Marinho").values_list("size", flat=True))
        assert set(marinho_sizes) == {"G", "GG"}

        # Check dados-edicao endpoint
        edit_data_res = client.get(reverse("catalog:product_edit_data", kwargs={"pk": product.id}))
        assert edit_data_res.status_code == 200
        edit_data = edit_data_res.json()
        assert len(edit_data["variants_matrix"]) == 2
        assert edit_data["variants_matrix"][0]["name"] == "Preto"
        assert len(edit_data["variants_matrix"][0]["sizes"]) == 3
        assert edit_data["variants_matrix"][1]["name"] == "Azul Marinho"
        assert len(edit_data["variants_matrix"][1]["sizes"]) == 2

        # Check product details page
        det_res = client.get(product.get_absolute_url())
        assert det_res.status_code == 200
        det_html = det_res.content.decode("utf-8")
        assert "Polo Lacoste Pima Two Tone" in det_html
        assert "Preto" in det_html
        assert "Azul Marinho" in det_html

    def test_admin_manual_reservation_creation(self, client):
        user = User.objects.create_user(
            email="admin_res@vakaria.com.br",
            password="pass123",
            name="Admin Res",
            is_staff=True,
        )
        client.force_login(user)

        brand = Brand.objects.create(name="Reserva", slug="reserva-res")
        cat = Category.objects.create(name="Camisas", slug="camisas-res")
        product = Product.objects.create(
            title="Camisa Linho Reserva",
            slug="camisa-linho-reserva",
            price=Decimal("289.90"),
            brand=brand,
            category=cat,
            is_active=True,
        )

        # GET admin reservations page
        get_res = client.get(reverse("orders:admin_reservations"))
        assert get_res.status_code == 200
        assert "Nova Reserva Manual" in get_res.content.decode("utf-8")
        assert "Camisa Linho Reserva" in get_res.content.decode("utf-8")

        # POST create manual reservation
        post_data = {
            "product_id": product.id,
            "customer_name": "Juliana Lima",
            "customer_phone": "(83) 98888-7777",
            "size": "M",
            "color": "Branco Off",
            "notes": "Cliente VIP, avisar com prioridade.",
        }
        post_res = client.post(reverse("orders:admin_reservations"), post_data, follow=True)
        assert post_res.status_code == 200

        res_obj = ProductReservation.objects.filter(customer_name="Juliana Lima").first()
        assert res_obj is not None
        assert res_obj.product == product
        assert res_obj.customer_phone == "(83) 98888-7777"
        assert res_obj.size == "M"
        assert res_obj.color == "Branco Off"
        assert res_obj.status == "pending"
        assert res_obj.notes == "Cliente VIP, avisar com prioridade."

    def test_admin_home_cms_flow(self, client):
        admin = User.objects.create_user(
            email="home_cms_admin@vakaria.com.br",
            password="pass12345",
            name="Home CMS Admin",
            is_staff=True,
        )
        client.force_login(admin)

        # GET admin home cms page
        get_res = client.get(reverse("pages:admin_home_cms"))
        assert get_res.status_code == 200
        content = get_res.content.decode("utf-8")
        assert "Gerenciador da Página Inicial" in content
        assert "Banners do Topo" in content
        assert "Cards das Coleções" in content
        assert "Loja Física" in content

        # POST save collection cards
        cards_post_data = {
            "action": "save_cards",
            "women_card_badge": "👗 Vestidos & Linho",
            "women_card_title": "Coleção Feminina Primavera",
            "women_card_subtitle": "Vestidos fluidos e alfaiataria premium.",
            "women_card_url": "/produtos/?gender=F&category=vestidos",
            "women_card_btn_text": "Explorar Feminino",
            "men_card_badge": "👔 Camisaria Nobre",
            "men_card_title": "Coleção Masculina Linho",
            "men_card_subtitle": "Camisas em linho puro e polos Reserva.",
            "men_card_url": "/produtos/?gender=M&category=camisas",
            "men_card_btn_text": "Explorar Masculino",
        }
        res_cards = client.post(reverse("pages:admin_home_cms"), cards_post_data, follow=True)
        assert res_cards.status_code == 200

        config = HomePageConfig.get_config()
        assert config.women_card_title == "Coleção Feminina Primavera"
        assert config.men_card_title == "Coleção Masculina Linho"

        # POST save store info
        store_post_data = {
            "action": "save_store",
            "store_badge": "📍 Centro de Cajazeiras - PB",
            "store_title": "Conheça a Loja Conceito Vakaria",
            "store_description": "Venha tomar um café expresso conosco e conhecer nosso provador VIP.",
            "store_address": "Rua José Pires Braga 120, Centro, Cajazeiras - PB",
            "store_phone": "+55 81 8398-3355",
            "store_instagram_handle": "@eduardo_vaka_",
            "store_maps_url": "https://maps.google.com/?q=Vakaria",
            "store_status_badge": "Aberto até 18h",
        }
        res_store = client.post(reverse("pages:admin_home_cms"), store_post_data, follow=True)
        assert res_store.status_code == 200

        config.refresh_from_db()
        assert config.store_title == "Conheça a Loja Conceito Vakaria"
        assert config.store_status_badge == "Aberto até 18h"

        # POST create banner with new style fields
        banner_post_data = {
            "action": "create_banner",
            "title": "Drop Exclusivo Linho & Seda",
            "subtitle": "Peças limitadas com frete grátis para Cajazeiras",
            "badge_text": "✨ LANÇAMENTO",
            "button_text": "Ver Drop",
            "button_url": "/produtos/?drop=linho-seda",
            "slide_type": "hero",
            "order": 1,
            "image_url": "https://images.unsplash.com/photo-test",
            "overlay_darkness": "dark",
            "text_alignment": "center",
            "button_style": "gold",
        }
        res_banner = client.post(reverse("pages:admin_home_cms"), banner_post_data, follow=True)
        assert res_banner.status_code == 200

        slide = CarouselSlide.objects.filter(title="Drop Exclusivo Linho & Seda").first()
        assert slide is not None
        assert slide.badge_text == "✨ LANÇAMENTO"
        assert slide.overlay_darkness == "dark"
        assert slide.text_alignment == "center"
        assert slide.button_style == "gold"

        # Test quick data JSON
        data_res = client.get(reverse("pages:admin_carousel_data", kwargs={"pk": slide.pk}))
        assert data_res.status_code == 200
        data_json = data_res.json()
        assert data_json["success"] is True
        assert data_json["title"] == "Drop Exclusivo Linho & Seda"
        assert data_json["overlay_darkness"] == "dark"
        assert data_json["text_alignment"] == "center"

        # Test CustomerReview CRUD via Admin CMS
        review_post_data = {
            "action": "create_review",
            "name": "Dra. Beatriz Sales",
            "location": "Cliente VIP • Cajazeiras PB",
            "rating": 5,
            "comment": "As roupas da Farm e Animale são maravilhosas! Atendimento de primeira.",
            "source": "google",
            "order": 1,
            "avatar_url": "https://images.unsplash.com/photo-avatar",
        }
        res_rev = client.post(reverse("pages:admin_home_cms"), review_post_data, follow=True)
        assert res_rev.status_code == 200

        from larkon.catalog.models import CustomerReview
        review = CustomerReview.objects.filter(name="Dra. Beatriz Sales").first()
        assert review is not None
        assert review.rating == 5
        assert review.source == "google"
        assert review.initial_letter == "D"
        assert review.final_avatar_url == "https://images.unsplash.com/photo-avatar"

        # Test review quick data JSON
        rev_data_res = client.get(reverse("pages:admin_review_data", kwargs={"pk": review.pk}))
        assert rev_data_res.status_code == 200
        rev_json = rev_data_res.json()
        assert rev_json["success"] is True
        assert rev_json["name"] == "Dra. Beatriz Sales"

        # Test review toggle
        toggle_res = client.post(
            reverse("pages:admin_review_toggle", kwargs={"pk": review.pk}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert toggle_res.status_code == 200
        assert toggle_res.json()["is_active"] is False
        review.refresh_from_db()
        assert review.is_active is False

        # Toggle back to active
        client.post(
            reverse("pages:admin_review_toggle", kwargs={"pk": review.pk}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        review.refresh_from_db()
        assert review.is_active is True

        # Check public landing page reflects dynamic content
        public_res = client.get(reverse("catalog:home"))
        assert public_res.status_code == 200
        public_html = public_res.content.decode("utf-8")
        assert "Coleção Feminina Primavera" in public_html
        assert "Coleção Masculina Linho" in public_html
        assert "Conheça a Loja Conceito Vakaria" in public_html
        assert "Drop Exclusivo Linho &amp; Seda" in public_html or "Drop Exclusivo Linho & Seda" in public_html
        assert "Dra. Beatriz Sales" in public_html
        assert "overlay-dark" in public_html

    def test_inventory_management_entradas_saidas(self, client: Client):
        from larkon.catalog.models import Product, ProductVariant, Brand, Category, StockMovement

        admin_user = User.objects.create_user(
            email="estoquista@vakaria.com.br",
            password="password123",
            name="Gerente de Estoque",
            is_staff=True,
        )
        client.force_login(admin_user)

        brand = Brand.objects.create(name="Vakaria Premium", slug="vakaria-premium", is_active=True)
        cat = Category.objects.create(name="Camisas Sociais", slug="camisas-sociais", is_active=True)
        product = Product.objects.create(
            title="Camisa Linho Nobre Reserva Especial",
            slug="camisa-linho-nobre-reserva-especial",
            brand=brand,
            category=cat,
            price=Decimal("389.00"),
            cost_price=Decimal("150.00"),
            gender="M",
            is_active=True,
        )

        var_p = ProductVariant.objects.create(product=product, size="P", color="Branco", stock_quantity=2, sku="LNH-BR-P")
        var_m = ProductVariant.objects.create(product=product, size="M", color="Branco", stock_quantity=5, sku="LNH-BR-M")
        var_g = ProductVariant.objects.create(product=product, size="G", color="Branco", stock_quantity=0, sku="LNH-BR-G")

        # 1. Access Inventory Page
        res = client.get(reverse("catalog:admin_inventory"))
        assert res.status_code == 200
        html = res.content.decode("utf-8")
        assert "Controle de Estoque &amp; Grade" in html or "Controle de Estoque & Grade" in html
        assert "Camisa Linho Nobre Reserva Especial" in html

        # 2. Test Stock In (Entrada)
        stock_in_res = client.post(
            reverse("catalog:admin_inventory"),
            {
                "action": "stock_in",
                "variant_id": var_g.id,
                "quantity": 10,
                "reason": "purchase",
                "cost_price": "145.00",
                "invoice_number": "NF-99881",
                "notes": "Lote novo recebido do fornecedor",
                "ajax": "1",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert stock_in_res.status_code == 200
        var_g.refresh_from_db()
        assert var_g.stock_quantity == 10
        assert StockMovement.objects.filter(variant=var_g, movement_type="IN", quantity=10).exists()

        # 3. Test Stock Out (Saída)
        stock_out_res = client.post(
            reverse("catalog:admin_inventory"),
            {
                "action": "stock_out",
                "variant_id": var_m.id,
                "quantity": 2,
                "reason": "sale",
                "invoice_number": "PED-VIP-101",
                "notes": "Venda presencial na loja física",
                "ajax": "1",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert stock_out_res.status_code == 200
        var_m.refresh_from_db()
        assert var_m.stock_quantity == 3
        assert StockMovement.objects.filter(variant=var_m, movement_type="OUT", quantity=2).exists()

        # 4. Test Stock Out Insufficient
        out_err_res = client.post(
            reverse("catalog:admin_inventory"),
            {
                "action": "stock_out",
                "variant_id": var_p.id,
                "quantity": 999,
                "reason": "sale",
                "ajax": "1",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert out_err_res.status_code == 400
        var_p.refresh_from_db()
        assert var_p.stock_quantity == 2

        # 5. Test Quick Balance Adjust
        adjust_res = client.post(
            reverse("catalog:admin_inventory"),
            {
                "action": "quick_adjust",
                "variant_id": var_p.id,
                "new_stock": 7,
                "notes": "Contagem física de balanço",
                "ajax": "1",
            },
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert adjust_res.status_code == 200
        var_p.refresh_from_db()
        assert var_p.stock_quantity == 7
        assert StockMovement.objects.filter(variant=var_p, movement_type="ADJUST", new_stock=7).exists()

        # 6. Test Batch Grid Entry (Grade Rápida)
        batch_res = client.post(
            reverse("catalog:admin_inventory"),
            {
                "action": "batch_grid_in",
                "product_id": product.id,
                f"size_qty_{var_p.id}": "3",
                f"size_qty_{var_m.id}": "4",
                f"size_qty_{var_g.id}": "5",
                "reason": "purchase",
                "invoice_number": "NF-GRADE-01",
            },
            follow=True,
        )
        assert batch_res.status_code == 200
        var_p.refresh_from_db()
        var_m.refresh_from_db()
        var_g.refresh_from_db()
        assert var_p.stock_quantity == 10  # 7 + 3
        assert var_m.stock_quantity == 7   # 3 + 4
        assert var_g.stock_quantity == 15  # 10 + 5

        # 7. Test Variant History JSON API
        hist_res = client.get(reverse("catalog:admin_variant_history", kwargs={"pk": var_p.id}))
        assert hist_res.status_code == 200
        hist_json = hist_res.json()
        assert hist_json["success"] is True
        assert len(hist_json["history"]) >= 2
        assert hist_json["history"][0]["type"] in ["IN", "OUT", "ADJUST"]

    def test_home_promo_and_countdown_timer(self, client: Client):
        from larkon.catalog.models import HomePageConfig

        admin_user = User.objects.create_user(
            email="gerentecms@vakaria.com.br",
            password="password123",
            name="Gerente de Marketing",
            is_staff=True,
        )
        client.force_login(admin_user)

        # 1. Access CMS Promo tab
        res_cms = client.get(reverse("pages:admin_home_cms") + "?tab=promo")
        assert res_cms.status_code == 200
        assert "Promoções &amp; Timer" in res_cms.content.decode("utf-8") or "Promoções & Timer" in res_cms.content.decode("utf-8")

        # 2. Save Promo settings via POST
        save_res = client.post(
            reverse("pages:admin_home_cms"),
            {
                "action": "save_promo",
                "promo_active": "1",
                "promo_badge": "⚡ DROP RELÂMPAGO DE 48H",
                "promo_title": "Vestidos de Seda com até 35% OFF",
                "promo_subtitle": "Apenas neste fim de semana. Peças exclusivas por tempo limitado.",
                "promo_discount_badge": "-35% OFF",
                "promo_button_text": "Garantir no WhatsApp",
                "promo_button_url": "/produtos/?gender=F",
                "promo_stock_alert_text": "⚠️ Apenas 3 peças no tamanho M",
                "promo_top_ticker_active": "1",
                "promo_preset": "48h",
            },
            follow=True,
        )
        assert save_res.status_code == 200

        config = HomePageConfig.get_config()
        assert config.promo_active is True
        assert config.promo_title == "Vestidos de Seda com até 35% OFF"
        assert config.promo_discount_badge == "-35% OFF"
        assert config.promo_end_date is not None
        assert config.is_promo_running is True

        # 3. Check public landing page reflects the new promo section and countdown
        home_res = client.get(reverse("catalog:home"))
        assert home_res.status_code == 200
        html = home_res.content.decode("utf-8")
        assert "Explore por Estilo ou Ofertas" in html
        assert "Coleções em Destaque" in html
        assert "Ofertas Relâmpago" in html
        assert "Vestidos de Seda com até 35% OFF" in html
        assert "-35% OFF" in html
        assert "promoDays" in html
        assert "promoHours" in html












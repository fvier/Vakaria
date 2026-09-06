import os
import sys
from pathlib import Path
import django

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.utils.text import slugify
from larkon.catalog.models import Category

TAXONOMY = [
    # -------------------------------------------------------------
    # 1. GRIFE HF - MASCULINO & GERAL
    # -------------------------------------------------------------
    {
        "name": "CAMISAS",
        "gender": "M",
        "icon": "solar:t-shirt-bold-duotone",
        "order": 1,
        "children": [
            {"name": "VESTUÁRIO MULTIMARCAS PREMIUM", "order": 1},
            {"name": "TIME COM FRASE", "order": 2},
            {"name": "POLIAMIDA PREMIUM", "order": 3},
            {"name": "POLO DE SITE", "order": 4},
            {"name": "MALHA CHINESA", "order": 5},
            {"name": "MALHA PIMA LEGÍTIMA", "order": 6},
            {"name": "OVERSIZED", "order": 7},
            {"name": "SOCIAL PREMIUM", "order": 8},
        ]
    },
    {
        "name": "BERMUDAS PREMIUM",
        "gender": "M",
        "icon": "solar:box-minimalistic-bold-duotone",
        "order": 2,
        "children": [
            {"name": "SARJA", "order": 1},
            {"name": "JEANS", "order": 2},
            {"name": "ALFAIATARIA", "order": 3},
            {"name": "ELASTANO", "order": 4},
            {"name": "ELASTANO TAILANDÊS", "order": 5},
            {"name": "TACTEL COM ELASTANO", "order": 6},
            {"name": "CARGO", "order": 7},
        ]
    },
    {
        "name": "DRIFIT LINHA GOLD",
        "gender": "M",
        "icon": "solar:bolt-bold-duotone",
        "order": 3,
        "children": [
            {"name": "KIT DRIFIT", "order": 1},
            {"name": "CAMISAS DRIFIT", "order": 2},
            {"name": "BERMUDAS DRIFIT", "order": 3},
        ]
    },
    {
        "name": "REGATAS",
        "gender": "M",
        "icon": "solar:t-shirt-bold-duotone",
        "order": 4,
        "children": [
            {"name": "TIME COM FRASE", "order": 1},
            {"name": "AMERICANA", "order": 2},
            {"name": "MACHÃO", "order": 3},
            {"name": "TRADICIONAL", "order": 4},
        ]
    },
    {
        "name": "CALÇAS",
        "gender": "M",
        "icon": "solar:hanger-bold-duotone",
        "order": 5,
        "children": [
            {"name": "JEANS SKINNY", "order": 1},
            {"name": "JEANS SLIM", "order": 2},
            {"name": "ALFAIATARIA SLIM FIT", "order": 3},
            {"name": "MALHA CHINESA", "order": 4},
            {"name": "CALÇA TREINO NACIONAL", "order": 5},
            {"name": "CARGO", "order": 6},
            {"name": "JOGGER", "order": 7},
        ]
    },
    {
        "name": "CALÇADOS PREMIUM",
        "gender": "U",
        "icon": "solar:sneakers-bold-duotone",
        "order": 6,
        "children": [
            {"name": "TÊNIS", "order": 1},
            {"name": "CHINELO", "order": 2},
        ]
    },
    {
        "name": "ACESSÓRIOS PREMIUM",
        "gender": "U",
        "icon": "solar:watch-round-bold-duotone",
        "order": 7,
        "children": [
            {"name": "BONÉS", "order": 1},
            {"name": "MEIAS", "order": 2},
            {"name": "PERFUMES", "order": 3},
            {"name": "CARTEIRAS", "order": 4},
            {"name": "RELÓGIOS", "order": 5},
        ]
    },
    {
        "name": "ROUPA ÍNTIMA",
        "gender": "M",
        "icon": "solar:shield-star-bold-duotone",
        "order": 8,
        "children": [
            {"name": "CUECAS", "order": 1},
            {"name": "SUNGA TECNOLÓGICA", "order": 2},
        ]
    },

    # -------------------------------------------------------------
    # 2. LUIZA FIT (MODA FEMININA PREMIUM)
    # -------------------------------------------------------------
    {
        "name": "LUIZA FIT",
        "gender": "F",
        "icon": "solar:stars-minimalistic-bold-duotone",
        "order": 20,
        "children": [
            {"name": "CONJUNTO DE CALÇAS", "order": 1},
            {"name": "CONJUNTO DE SHORTS", "order": 2},
            {"name": "MACACÃO", "order": 3},
            {"name": "MACAQUINHO", "order": 4},
            {"name": "LEGGING", "order": 5},
            {"name": "SHORT", "order": 6},
            {"name": "BLUSAS", "order": 7},
            {"name": "VESTIDOS", "order": 8},
            {"name": "ACESSÓRIOS", "order": 9},
        ]
    }
]

def seed_categories():
    print("🌱 Iniciando o cadastro da taxonomia de categorias...")
    total_parents = 0
    total_children = 0

    # Limpeza / Migração de slug antigo se existir
    old_cat = Category.objects.filter(slug="use-luiza-fit-moda-feminina-premium").first()
    if old_cat:
        old_cat.children.all().delete()
        old_cat.delete()

    for item in TAXONOMY:
        parent_slug = slugify(item["name"])
        parent_cat, p_created = Category.objects.get_or_create(
            slug=parent_slug,
            defaults={
                "name": item["name"],
                "gender_target": item["gender"],
                "icon": item["icon"],
                "order": item["order"],
                "is_active": True,
            }
        )
        if not p_created:
            parent_cat.name = item["name"]
            parent_cat.gender_target = item["gender"]
            parent_cat.icon = item["icon"]
            parent_cat.order = item["order"]
            parent_cat.is_active = True
            parent_cat.save()

        total_parents += 1
        status_p = "CRIADA" if p_created else "ATUALIZADA"
        print(f"[{status_p}] Categoria Pai: {parent_cat.name} ({parent_cat.get_gender_target_display()})")

        for child in item.get("children", []):
            child_slug = slugify(f"{parent_cat.name}-{child['name']}")
            child_cat, c_created = Category.objects.get_or_create(
                slug=child_slug,
                defaults={
                    "name": child["name"],
                    "gender_target": item["gender"],
                    "parent": parent_cat,
                    "order": child["order"],
                    "is_active": True,
                }
            )
            if not c_created:
                child_cat.name = child["name"]
                child_cat.gender_target = item["gender"]
                child_cat.parent = parent_cat
                child_cat.order = child["order"]
                child_cat.is_active = True
                child_cat.save()

            total_children += 1
            status_c = "CRIADA" if c_created else "ATUALIZADA"
            print(f"  └── [{status_c}] Subcategoria: {child_cat.name}")

    print(f"\n✅ Concluído! Total: {total_parents} categorias principais e {total_children} subcategorias cadastradas.")

if __name__ == "__main__":
    seed_categories()

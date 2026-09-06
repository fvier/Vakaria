def store_info(request):
    """Disponibiliza os dados de contato, endereço e redes sociais da Grife HF globalmente em todos os templates."""
    return {
        "STORE_NAME": "Grife HF Multimarcas",
        "STORE_ADDRESS": "Rua José Pires Braga 120, Cajazeiras PB, 58900-000, Brasil",
        "STORE_CITY": "Cajazeiras - PB",
        "STORE_PHONE": "+55 83 9165-0137",
        "STORE_WHATSAPP_NUMBER": "558391650137",
        "STORE_WHATSAPP_URL": "https://wa.me/558391650137",
        "STORE_WHATSAPP_GROUP_URL": "https://chat.whatsapp.com/EoQm1858BrK36Uvjs6dYRG?mode=gi_t",
        "STORE_INSTAGRAM_URL": "https://www.instagram.com/grifehfmultimarcascz/",
        "STORE_INSTAGRAM_HANDLE": "@grifehfmultimarcascz",
    }

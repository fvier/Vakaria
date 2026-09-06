from django.conf import settings

def store_info(request):
    """Disponibiliza os dados de contato, endereço e redes sociais do Cabeleireiro Eduardo Cardoso globalmente em todos os templates."""
    info = getattr(settings, "VAKARIA_INFO", {})
    return {
        "STORE_NAME": info.get("NAME", "Cabeleireiro Eduardo Cardoso"),
        "STORE_ADDRESS": info.get("ADDRESS", "Sítio Histórico de Olinda, Olinda - PE, Brasil"),
        "STORE_CITY": info.get("CITY", "Olinda - PE"),
        "STORE_PHONE": info.get("PHONE", "+55 81 8398-3355"),
        "STORE_WHATSAPP_NUMBER": "558183983355",
        "STORE_WHATSAPP_URL": info.get("WHATSAPP_URL", "https://wa.me/558183983355"),
        "STORE_WHATSAPP_GROUP_URL": info.get("WHATSAPP_GROUP_URL", "https://chat.whatsapp.com/EoQm1858BrK36Uvjs6dYRG"),
        "STORE_INSTAGRAM_URL": info.get("INSTAGRAM_URL", "https://www.instagram.com/eduardo_vaka_/"),
        "STORE_INSTAGRAM_HANDLE": info.get("INSTAGRAM_HANDLE", "@eduardo_vaka_"),
    }

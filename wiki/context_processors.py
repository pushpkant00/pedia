from django.conf import settings


def site(request):
    return {
        'site_name': getattr(settings, 'WIKI_NAME', 'Pedia'),
        'site_tagline': getattr(settings, 'WIKI_TAGLINE', ''),
    }

from django.conf import settings

def pubname_setting(request):
    return {'TILLWEB_PUBNAME': settings.TILLWEB_PUBNAME}

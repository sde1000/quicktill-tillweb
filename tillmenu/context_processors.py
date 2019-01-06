from django.conf import settings

def food_menu_editor_setting(request):
    return {'FOOD_MENU_EDITOR': getattr(settings, 'FOOD_MENU_EDITOR', False)}
            

from parameters.models import Locales


def get_locale(code):
    lang = False
    if code.find("-") > 0:
        try:
            locale = Locales.objects.get(locale__icontains=code)
            return locale
        except Locales.DoesNotExist:
            lang = code.split("-")[0]
    if lang:
        try:
            locale = Locales.objects.get(lang__icontains=lang)
            return locale
        except Locales.DoesNotExist:
            return False
    else:
        return False
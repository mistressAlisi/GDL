from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from modeltranslation.translator import register, TranslationOptions
from .models import VHostMenuEntry, VHostDomain, VHostSideBarEntry, VHostSideBarSubmenuEntry, \
    VHostUserSideBarEntry, VHostUserMenuEntry, VHostUserSideBarSubmenuEntry, VHostMenuSubmenuEntry


@register(VHostDomain)
class VHostDomainTranslationOptions(TranslationOptions):
    fields = ('domain_intro_header', 'domain_intro_body','footer_left','footer_centre','footer_right')
@admin.register(VHostDomain)
class VHostDomainAdmin(TranslationAdmin):
    pass






@register(VHostMenuEntry)
class VHostMenuEntryTranslationOptions(TranslationOptions):
    fields = ('name','help_text')
@admin.register(VHostMenuEntry)
class VHostMenuEntryAdmin(TranslationAdmin):
    pass


@register(VHostMenuSubmenuEntry)
class VHostMenuSubmenuEntryTranslationOptions(TranslationOptions):
    fields = ('name','help_text')
@admin.register(VHostMenuSubmenuEntry)
class VHostMenuSubmenuEntry(TranslationAdmin):
    pass




@register(VHostSideBarEntry)
class VHostSideBarEntryTranslationOptions(TranslationOptions):
    fields = ('name','help_text')
@admin.register(VHostSideBarEntry)
class VHostSideBarEntryAdmin(TranslationAdmin):
    pass




@register(VHostSideBarSubmenuEntry)
class VHostSideBarSubmenuEntryTranslationOptions(TranslationOptions):
    fields = ('name','help_text')


@admin.register(VHostSideBarSubmenuEntry)
class VHostSideBarSubmenuEntryAdmin(TranslationAdmin):
    list_filter = ["menu","locale","url"]
    search_fields = ["url","name","help_text" ]

@register(VHostUserSideBarEntry)
class VHostUserSideBarEntryTranslationOptions(TranslationOptions):
    fields = ('name','help_text')
@admin.register(VHostUserSideBarEntry)
class VHostUserSideBarEntryAdmin(TranslationAdmin):
    pass


@register(VHostUserMenuEntry)
class VHostUserMenuEntryTranslationOptions(TranslationOptions):
    fields = ('name','help_text')
@admin.register(VHostUserMenuEntry)
class VHostUserMenuEntryAdmin(TranslationAdmin):
    pass

@register(VHostUserSideBarSubmenuEntry)
class VHostUserSideBarSubmenuTranslationOptions(TranslationOptions):
    fields = ('name','help_text')
@admin.register(VHostUserSideBarSubmenuEntry)
class VHostUserSideBarSubmenuEntryAdmin(TranslationAdmin):
    pass

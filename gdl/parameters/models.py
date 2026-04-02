import uuid
from uuid import uuid4

from django.contrib import admin
from django.contrib.auth.models import Permission, Group as PermissionGroup
from django.db import models
from django.db.models import CheckConstraint, Q, JSONField
from django.forms.models import model_to_dict
from django.utils import translation
from modeltranslation.admin import TranslationAdmin


# Timezones:
class Timezone(models.Model):
    class Meta:
        ordering  = ('timezone',)
    tz = models.TextField(verbose_name='TimeZone Code',default='America/New_York')
    timezone = models.TextField(verbose_name='TimeZone Name',default='America/New_York')
    offset = models.TextField(verbose_name='TimeZone Code',default='-05:00')
    active = models.BooleanField(verbose_name="Active",default=True)
    def __str__(self):
            return f"{self.timezone} ({self.offset})"

@admin.register(Timezone)
class TimezoneAdmin(admin.ModelAdmin):
    pass

# Timezones:
class Locales(models.Model):
    class Meta:
        ordering  = ['lang']
        unique_together = (('lang',"locale"))
    lang = models.TextField(verbose_name='Language Code',default='en')
    locale = models.TextField(verbose_name='Locale and Country Code',default='en-CA',unique=True)
    name = models.TextField(verbose_name='Locale Name ',default='English (Canada)')
    use_24h = models.BooleanField(verbose_name="Use 24 Hours",default=True)
    active = models.BooleanField(verbose_name="Active",default=True)
    def __str__(self):
            return f"{self.name} ({self.locale})"

@admin.register(Locales)
class LocalesAdmin(admin.ModelAdmin):
    pass


# Themes:
class Theme(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.TextField(verbose_name="Theme Name", help_text="Theme Name", default="Athena")
    slug = models.TextField(verbose_name="Theme Slug", help_text="Theme Slug",unique=True)
    path = models.TextField(verbose_name="Theme Path", help_text="Theme Path")
    active = models.BooleanField(verbose_name="Active",default=True)
    reg_active = models.BooleanField(verbose_name="Registration Active", default=True)
    def __str__(self):
        return f"{self.slug}/{self.name}"

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    pass

class ThemeStyleSheet(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    theme = models.ForeignKey(Theme,on_delete=models.CASCADE,verbose_name="Theme", help_text="Parent Theme")
    css_file_path = models.TextField(verbose_name="CSS to Include (Path)")
    order = models.IntegerField(verbose_name="Order By",default=0)
    active = models.BooleanField(verbose_name="Active",default=True)
    def __str__(self):
        return f"{self.theme.slug}/{self.theme.name}->{self.css_file_path}"


@admin.register(ThemeStyleSheet)
class ThemeStyleSheetAdmin(admin.ModelAdmin):
    pass



# Create your models here.

class VHost(models.Model):
    class Meta:
        ordering = ('name',)
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.TextField(verbose_name="VHost Name", help_text="VHost Name", default="Athena",unique=True)
    email_domain = models.TextField(verbose_name="Vhost Domain FQDN For Emails", help_text="Domain FQDN for Vhost", default="athena.fqdn")
    active = models.BooleanField(verbose_name="Active",default=True)
    reg_active = models.BooleanField(verbose_name="Registration Active", default=True)

    def __str__(self):
        return f"{self.name}"

@admin.register(VHost)
class VHostAdmin(admin.ModelAdmin):
    pass

class VHostDomain(models.Model):
    class Meta:
        unique_together = ('domain_fqdn','vhost')
    FRONTEND_CHOICES = (('lob','Standard Frontend Lobby'),('kio','Kiosk Mode'))
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host", null=True, blank=True)
    domain_fqdn = models.TextField(verbose_name="Vhost Domain FQDN", help_text="Domain FQDN for Vhost", default="athena.fqdn", unique=True)
    default_manager = models.ForeignKey("management.Manager",verbose_name="Default Manager to assign new accounts to",on_delete=models.SET_NULL,null=True,blank=True)
    domain_addr = models.GenericIPAddressField(verbose_name="VHost IP Addr", help_text="VHost IP Address", default="127.0.0.1")
    website_name = models.TextField(verbose_name="Website Name", help_text="If specified; this name will override the VHost name in the UI",null=True,blank=True)
    frontend = models.CharField(verbose_name="Frontend Selection",choices=FRONTEND_CHOICES,default="lob")
    demo_mode = models.BooleanField(verbose_name="Domain in Demo Mode", default=False)
    demo_login_redirect_url = models.TextField(verbose_name="Demo Login Redirect URL",max_length=255,null=True,blank=True)
    login_redirect_url = models.TextField(verbose_name="Login Redirect URL", max_length=255, null=True,blank=True)
    website_icon = models.ImageField(verbose_name="Website Navbar Icon",null=True,blank=True)
    show_website_name = models.BooleanField(verbose_name="Show Website Name",help_text="Show the website text next to the icon in the navbar?", default=False)
    include_theme_files = models.BooleanField(verbose_name="Include Theme Files",default=False,help_text="Include the files from the template directory into the relevant app places?")
    show_domain_intro_text = models.BooleanField(verbose_name="Show Domain Intro Text",default=False,help_text="Show Domain Intro Text in the main Landing UI instead of the default texts?")
    domain_intro_header = models.TextField(verbose_name="Domain Intro Header",null=True,blank=True)
    domain_intro_body = models.TextField(verbose_name="Domain Intro Text Body",null=True,blank=True)
    show_domain_footer_text = models.BooleanField(verbose_name="Show Domain Intro Text", default=False,  help_text="Show Domain Footer Text in the main Landing UI instead of the default texts?")
    footer_left = models.TextField(verbose_name="Domain Text/html for footer left", null=True, blank=True)
    footer_centre = models.TextField(verbose_name="Domain Text/html for footer centre", null=True, blank=True)
    footer_right = models.TextField(verbose_name="Domain Text/html for footer right", null=True, blank=True)
    icon_redirect_url = models.TextField(verbose_name="Redirect URL for icon", null=True, blank=True,default="#")
    theme = models.ForeignKey(Theme,on_delete=models.SET_NULL,verbose_name="Theme",help_text="Theme",null=True,blank=True)
    email_domain = models.TextField(verbose_name="Vhost Domain FQDN For Emails", help_text="Domain FQDN for Vhost", default="athena.fqdn")
    welcome_email_template_file = models.TextField(verbose_name="Welcome Email Template File (Path)",null=True,blank=True)
    active = models.BooleanField(verbose_name="Active", default=True)

    def __str__(self):
        return f"{self.vhost.name}: [{self.domain_fqdn}]@{self.domain_addr}"



class VHostDomainCSS(models.Model):
    class Meta:
        ordering = ('vhost','ordering_key')
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    domain = models.ForeignKey(VHostDomain, on_delete=models.CASCADE, verbose_name="Domain")
    css_file_path = models.TextField(verbose_name="CSS File Path",help_text="CSS File Path to include (relative to /static)")
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=1)
    def __str__(self):
        return f"CSS file for {self.vhost.name}/{self.domain}: {self.css_file_path}"
@admin.register(VHostDomainCSS)
class VHostDomainCSSAdmin(admin.ModelAdmin):
    pass

class AccountParameters(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid.uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host", null=True, blank=True)
    new_account_free_play = models.DecimalField(max_digits=20,decimal_places=5,default=10000,verbose_name="New Account Free Play Credit",help_text="This amount will be added as free play to newly registered accounts.")
    min_wager = models.DecimalField(max_digits=10,decimal_places=2,default=100,verbose_name="Minimum Wager",help_text="The default minimum amount for a wager")
    max_wager = models.DecimalField(max_digits=10,decimal_places=2,default=3000,verbose_name="Maximum Wager",help_text="The default maximum amount for a wager")
    initial_credit = models.DecimalField(max_digits=10, decimal_places=2, default=10000, verbose_name="Initial Credit", help_text="The default initial credit for a new account")
    enable_new_acct_free_play = models.BooleanField(help_text="Enable New Account Free Play credits", verbose_name="New Account Free Play Credit Enabled", default=False)
    ping_offline_threshold = models.IntegerField(default=10, verbose_name="Ping Offline Timeout Threshold", help_text="Timeout for PING interval in seconds for Accounts.")
    account_perf_warning_threshold = models.DecimalField(default=51,verbose_name="Account Performance: Warning Threshold:",help_text="This percentage will trigger a warning for a high performance account if the win/loss ratio exceeds this threshold.",max_digits=6,decimal_places=2)
    account_perf_alarm_threshold = models.DecimalField(default=70, verbose_name="Account Performance: Alarm Threshold:", help_text="This percentage will trigger an alarm for a high performance account if the win/loss ratio exceeds this threshold.",max_digits=6,decimal_places=2)
    def __str__(self):
        return f"Parameters for {self.vhost}"


@admin.register(AccountParameters)
class AccountParametersAdmin(admin.ModelAdmin):
    pass




class VHostMenuEntry(models.Model):
    class Meta:
        ordering = ('vhost','ordering_key')
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, verbose_name="Virtual Host", null=True, blank=True,on_delete=models.CASCADE)
    domains = models.ManyToManyField(VHostDomain, verbose_name="Domain",blank=True)
    managers = models.ManyToManyField('management.Manager', verbose_name="Agent", blank=True)
    on_click = models.TextField(verbose_name="On Click Action",null=True,blank=True)
    url = models.TextField(verbose_name="Menu Entry URL", default="#")
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=1)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, verbose_name="Permission", null=True,
                                   blank=True)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.SET_NULL, verbose_name="Permission Group",
                                         null=True, blank=True)
    icon = models.TextField(verbose_name="Icon Class", null=True, blank=True)
    name = models.TextField(verbose_name="Menu Entry Name", null=True, blank=True)
    help_text = models.TextField(verbose_name="Menu Entry Help Text", null=True, blank=True)
    active = models.BooleanField(verbose_name="Entry Active",default=True)
    def has_submenus(self):

        return len(VHostMenuSubmenuEntry.objects.filter(menu=self,active=True)) >= 1
    def get_submenus(self):
        return VHostMenuSubmenuEntry.objects.filter(menu=self,active=True).order_by('ordering_key')
    def __str__(self):
        return f"{self.vhost}: {self.name}-> OC[{self.on_click}]/URL[{self.url}]"

class VHostMenuSubmenuEntry(models.Model):
    class Meta:
        ordering = ('menu','ordering_key')

    uuid = models.UUIDField(primary_key=True,default=uuid4)
    menu = models.ForeignKey(VHostMenuEntry, on_delete=models.CASCADE, verbose_name="Virtual Host")
    url = models.TextField(verbose_name="Menu Entry URL", default="#")
    target_url = models.TextField(verbose_name="Menu Entry Data Target URL",blank=True,null=True)
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=1)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, verbose_name="Permission", null=True,
                                   blank=True)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.SET_NULL, verbose_name="Permission Group",
                                         null=True, blank=True)
    icon = models.TextField(verbose_name="Icon Class", null=True, blank=True)
    on_click = models.TextField(verbose_name="On Click Action",null=True,blank=True)

    name = models.TextField(verbose_name="Menu Entry Name", null=True, blank=True)
    help_text = models.TextField(verbose_name="Menu Entry Help Text", null=True, blank=True)
    active = models.BooleanField(verbose_name="Entry Active",default=True)
    def __str__(self):
        return f"[Admin/Agent]:  Submenu for {self.menu.name}->{self.name}-> OC[{self.on_click}]/URL[{self.url}]"




class VHostSideBarEntry(models.Model):
    class Meta:
        ordering = ('vhost','ordering_key')
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    domains = models.ManyToManyField(VHostDomain, verbose_name="Domain",blank=True)
    managers = models.ManyToManyField('management.Manager', verbose_name="Agent", blank=True)
    on_click = models.TextField(verbose_name="On Click Action",null=True,blank=True)
    url = models.TextField(verbose_name="Menu Entry URL", default="#")
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=1)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, verbose_name="Permission", null=True,
                                   blank=True)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.SET_NULL, verbose_name="Permission Group",
                                         null=True, blank=True)
    icon = models.TextField(verbose_name="Icon Class", null=True, blank=True)
    name = models.TextField(verbose_name="Menu Entry Name", null=True, blank=True)
    help_text = models.TextField(verbose_name="Menu Entry Help Text", null=True, blank=True)
    active = models.BooleanField(verbose_name="Entry Active",default=True)
    def get_submenus(self,locale,user_permissions=None):
        if not user_permissions:
            return VHostSideBarSubmenuEntry.objects.filter(menu=self,locale=locale).order_by('ordering_key')
        else:
            return VHostSideBarSubmenuEntry.objects.filter(Q(menu=self, locale=locale)&Q(Q(permission__isnull=True)|Q(permission__in=user_permissions))).order_by('ordering_key')

    def __str__(self):
        return f"[Admin/Agent]: {self.vhost.name}: {self.name}-> OC[{self.on_click}]/URL[{self.url}]"


class VHostSideBarSubmenuEntry(models.Model):
    class Meta:
        ordering = ('menu','ordering_key')
        unique_together = (('menu','locale','url'))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    menu = models.ForeignKey(VHostSideBarEntry, on_delete=models.CASCADE, verbose_name="Virtual Host")
    url = models.TextField(verbose_name="Menu Entry URL", default="#")
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=1)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, verbose_name="Permission", null=True,
                                   blank=True)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.SET_NULL, verbose_name="Permission Group",
                                         null=True, blank=True)
    icon = models.TextField(verbose_name="Icon Class", null=True, blank=True)
    on_click = models.TextField(verbose_name="On Click Action",null=True,blank=True)
    locale = models.ForeignKey(Locales, on_delete=models.CASCADE, verbose_name="Locale")
    name = models.TextField(verbose_name="Menu Entry Name", null=True, blank=True)
    help_text = models.TextField(verbose_name="Menu Entry Help Text", null=True, blank=True)
    active = models.BooleanField(verbose_name="Entry Active",default=True)
    def __str__(self):
        return f"[Admin/Agent]:  Submenu for {self.menu.name}->{self.name}->  OC[{self.on_click}]/URL[{self.url}]"




class VHostUserSideBarEntry(models.Model):
    class Meta:
        ordering = ('vhost','ordering_key')
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    domains = models.ManyToManyField(VHostDomain, verbose_name="Domain",blank=True)
    app_mode = models.TextField(verbose_name="App Mode", null=True, blank=True)
    managers = models.ManyToManyField('management.Manager', verbose_name="Agent", blank=True)
    on_click = models.TextField(verbose_name="On Click Action",null=True,blank=True)
    url = models.TextField(verbose_name="Menu Entry URL", default="#")
    target_url = models.TextField(verbose_name="Menu Entry Data Target URL",blank=True,null=True)
    html_target = models.TextField(verbose_name="Menu Entry HTML Target (such as _blank)",blank=True,null=True)
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=1)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, verbose_name="Permission",null=True, blank=True)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.SET_NULL, verbose_name="Permission Group",null=True, blank=True)
    icon = models.TextField(verbose_name="Icon Class", null=True, blank=True)
    name = models.TextField(verbose_name="Menu Entry Name", null=True, blank=True)
    help_text = models.TextField(verbose_name="Menu Entry Help Text", null=True, blank=True)
    active = models.BooleanField(verbose_name="Entry Active",default=True)
    def get_submenus(self,app_mode=False,permissions=False,locale=False):
        kwq = {"menu":self,"active":True}
        if app_mode:
            kwq["app_mode"] = app_mode
        else:
            kwq["app_mode__isnull"] = True
        if locale:
            #kwq["locale"] = locale
            translation.activate(locale)
        if permissions:
            kwq["permission__in"] = permissions
        retlist = []
        for vho in VHostUserSideBarSubmenuEntry.objects.filter(**kwq).order_by(
            'ordering_key'):
            dat = model_to_dict(vho)
            dat["uuid"] = str(dat["uuid"])
            dat["menu"] = str(dat["menu"])
            retlist.append(dat)

        return retlist


    def __str__(self):
        return f"{self.vhost.name}: {self.name}->[{self.app_mode}]-> OC[{self.on_click}]/URL[{self.url}]"



class VHostUserSideBarSubmenuEntry(models.Model):
    class Meta:
        ordering = ('menu','ordering_key')
        unique_together = (('menu','locale','url'))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    menu = models.ForeignKey(VHostUserSideBarEntry, on_delete=models.CASCADE, verbose_name="Virtual Host")
    url = models.TextField(verbose_name="Menu Entry URL", default="#")
    target_url = models.TextField(verbose_name="Menu Entry Data Target URL",blank=True,null=True)
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=1)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, verbose_name="Permission",null=True, blank=True)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.SET_NULL, verbose_name="Permission Group",null=True, blank=True)
    html_target = models.TextField(verbose_name="Menu Entry HTML Target (such as _blank)", blank=True, null=True)
    icon = models.TextField(verbose_name="Icon Class", null=True, blank=True)
    on_click = models.TextField(verbose_name="On Click Action",null=True,blank=True)
    locale = models.ForeignKey(Locales, on_delete=models.CASCADE, verbose_name="Locale")
    name = models.TextField(verbose_name="Menu Entry Name", null=True, blank=True)
    help_text = models.TextField(verbose_name="Menu Entry Help Text", null=True, blank=True)
    active = models.BooleanField(verbose_name="Entry Active",default=True)
    app_mode = models.TextField(verbose_name="App Mode", null=True, blank=True)
    managers = models.ManyToManyField('management.Manager', verbose_name="Agent", blank=True)
    def __str__(self):
        return f"Submenu for {self.menu.app_mode}->{self.menu.name}->{self.name}-> OC[{self.on_click}]/URL[{self.url}]"


class VHostUserMenuEntry(models.Model):
    class Meta:
        ordering = ('vhost','ordering_key')
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    domains = models.ManyToManyField(VHostDomain,verbose_name="Domain",blank=True)
    on_click = models.TextField(verbose_name="On Click Action",null=True,blank=True)
    managers = models.ManyToManyField('management.Manager', verbose_name="Agent", blank=True)
    app_mode = models.TextField(verbose_name="App Mode",null=True,blank=True)
    url = models.TextField(verbose_name="Menu Entry URL", default="#")
    ordering_key = models.IntegerField(verbose_name="Ordering Key",default=1)
    permission = models.ForeignKey(Permission, on_delete=models.SET_NULL, verbose_name="Permission",null=True, blank=True)
    permission_group = models.ForeignKey(PermissionGroup, on_delete=models.SET_NULL, verbose_name="Permission Group",null=True, blank=True)
    icon = models.TextField(verbose_name="Icon Class", null=True, blank=True)
    name = models.TextField(verbose_name="Menu Entry Name", null=True, blank=True)
    help_text = models.TextField(verbose_name="Menu Entry Help Text", null=True, blank=True)
    active = models.BooleanField(verbose_name="Entry Active",default=True)
    def __str__(self):
        return f"{self.vhost.name}: {self.name}->[{self.app_mode}]-> OC[{self.on_click}]/URL[{self.url}]"




class VHostCryptoParameters(models.Model):
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.OneToOneField(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    crypto_enabled = models.BooleanField(verbose_name="Crypto Transactions enabled for VHost", default=False)
    cpay_merchantid = models.TextField(verbose_name="CoinPayments Merchant ID")
    cpay_ipn = models.TextField(verbose_name="CoinPayments Merchant IPN Secret")
    cpay_pubkey = models.TextField(verbose_name="CoinPayments Merchant Public Key")
    cpay_privkey = models.TextField(verbose_name="CoinPayments Merchant Private Key")
    cpay_exchange_fee = models.DecimalField(max_digits=20,decimal_places=5,default=0.025,verbose_name="CoinPayments Merchant Fee Percentage")
    token_base_currency_xrate = models.DecimalField(max_digits=20, decimal_places=5, default=1, verbose_name="Token exchange rate versus reference Currency")
    token_base_currency = models.CharField(verbose_name="Token exchange base currency code", max_length=20, default="USDT")
    def __str__(self):
        return f"VHost Crypto Parameters for {self.vhost}."

@admin.register(VHostCryptoParameters)
class VHostCryptoParametersAdmin(admin.ModelAdmin):
    list_filter = ["vhost"]

class VHostCryptoExchangeCurrencies(models.Model):
    class Meta:
        unique_together = (("vhost", "symbol"))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE, verbose_name="Virtual Host")
    symbol = models.CharField(verbose_name="Exchange Currency Code", max_length=20)
    name = models.CharField(verbose_name="Exchange Currency Name", max_length=200)
    active = models.BooleanField(verbose_name="Exchange Currency Active", default=True)
    def __str__(self):
        return f"{self.symbol}/{self.name}"


@admin.register(VHostCryptoExchangeCurrencies)
class VHostCryptoExchangeCurrenciesAdmin(admin.ModelAdmin):
    list_filter = ["vhost","symbol"]



class VHostParameterRegistry(models.Model):
    class Meta:
        unique_together = (("vhost","name","application"))
    uuid = models.UUIDField(primary_key=True,default=uuid4)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    name = models.TextField(verbose_name="Parameter Name")
    application = models.TextField(verbose_name="Parameter Application",blank=True,null=True)
    created = models.DateTimeField(verbose_name="Parameter Created",auto_now_add=True)
    updated = models.DateTimeField(verbose_name="Parameter Updated",auto_now=True)
    value_text = models.TextField(verbose_name="Parameter Value Text",blank=True,null=True)
    value_bin = models.TextField(verbose_name="Parameter Value Bin",blank=True,null=True)
    value_int = models.TextField(verbose_name="Parameter Value Int",blank=True,null=True)
    value_json = JSONField(verbose_name="Parameter Value JSON",blank=True,null=True)
    def __str__(self):
        return f"Registry {self.vhost}: {self.name}"


@admin.register(VHostParameterRegistry)
class VHostParameterRegistryAdmin(admin.ModelAdmin):
    list_filter = ["vhost","application","name"]
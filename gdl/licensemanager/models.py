from uuid import uuid4

from django.contrib import admin
from django.db import models

from parameters.models import VHost


# Create your models here.

class VHostLicenseSettings(models.Model):
    uuid = models.UUIDField(default=uuid4,primary_key=True)
    vhost = models.OneToOneField(VHost, on_delete=models.CASCADE)
    activation_begins = models.DateTimeField(null=True, blank=True)
    activation_ends = models.DateTimeField(null=True, blank=True)
    maximum_agents = models.IntegerField(default=10)
    maximum_accounts = models.IntegerField(default=100)
    maximum_bet = models.IntegerField(default=1000)
    revenue_share_pct = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    licence_holder_name = models.TextField(null=True, blank=True)
    licence_holder_email = models.TextField(null=True, blank=True)
    licence_number = models.TextField()
    licence_payload = models.BinaryField(null=True, blank=True)
    licence_json_payload = models.JSONField(null=True, blank=True)
    licence_fingerprint = models.BinaryField(null=True, blank=True)
    licence_ca = models.BinaryField(null=True, blank=True)
    licence_cert = models.BinaryField(null=True, blank=True)
    licence_key = models.BinaryField(null=True, blank=True)
    licence_pubkey = models.BinaryField(null=True, blank=True)
    def __str__(self):
        return f"VHost: {self.vhost.name}  - Licensing "
@admin.register(VHostLicenseSettings)
class VHostLicenseSettingsAdmin(admin.ModelAdmin):
    pass

class ApplicationStudio(models.Model):
    uuid = models.UUIDField(default=uuid4,primary_key=True)
    name = models.TextField(verbose_name="Application Studio Name")
    slug = models.TextField(verbose_name="Application Studio Slug",unique=True)
    website = models.TextField(verbose_name="Application Studio Website")
    description = models.TextField(verbose_name="Application Studio Description")
    email = models.TextField(verbose_name="Application Studio Email Contact")
    address = models.TextField(verbose_name="Application Studio Address")
    def __str__(self):
        return f"ApplicationStudio: {self.name}"

@admin.register(ApplicationStudio)
class ApplicationStudioAdmin(admin.ModelAdmin):
        pass


class AvailableApplication(models.Model):
    class Meta:
        unique_together = ("slug", "studio")
    uuid = models.UUIDField(default=uuid4,primary_key=True)
    name = models.TextField(verbose_name="Application Name")
    version = models.TextField(verbose_name="Application Version")
    url_root = models.TextField(verbose_name="Application URL Root")
    studio = models.ForeignKey(ApplicationStudio,on_delete=models.RESTRICT,verbose_name="Application Studio")
    slug = models.SlugField(verbose_name="Application Slug")
    backend = models.TextField(verbose_name="Application Backend Model",blank=True,null=True)
    frontend = models.TextField(verbose_name="Application Frontend Name",blank=True,null=True)
    grader = models.TextField(verbose_name="Application Grader Name",blank=True,null=True)
    agent = models.TextField(verbose_name="Application Agent Name",blank=True,null=True)
    management = models.TextField(verbose_name="Application Management Name",blank=True,null=True)
    card_image = models.ImageField(verbose_name="Application Card Image",blank=True,null=True)
    card_logo = models.ImageField(verbose_name="Application Card Logo",blank=True,null=True)
    uses_channels = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.name}"


@admin.register(AvailableApplication)
class AvailableApplicationAdmin(admin.ModelAdmin):
    pass


class VHostLicencedApplications(models.Model):
    class Meta:
        unique_together = ("vhost", "application")
    uuid = models.UUIDField(default=uuid4,primary_key=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    application = models.ForeignKey(AvailableApplication, on_delete=models.CASCADE)
    activation_begins = models.DateTimeField(null=True, blank=True)
    activation_ends = models.DateTimeField(null=True, blank=True)
    profit_share_pct = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    operation_expense_pct = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    other_expenses_pct = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    maximum_agents = models.IntegerField(default=10)
    maximum_accounts = models.IntegerField(default=100)
    maximum_bet = models.IntegerField(default=1000)
    licence_number = models.TextField()
    licence_holder_name = models.TextField()
    licence_payload = models.BinaryField(null=True, blank=True)
    licence_json_payload = models.JSONField(null=True, blank=True)
    licence_fingerprint = models.BinaryField(null=True, blank=True)
    licence_ca = models.BinaryField(null=True, blank=True)
    licence_cert = models.BinaryField(null=True, blank=True)
    licence_key = models.BinaryField(null=True, blank=True)
    licence_pubkey = models.BinaryField(null=True, blank=True)
    def __str__(self):
        return f"VHost: {self.vhost.name}  - {self.application.name} Licensing "
@admin.register(VHostLicencedApplications)
class VHostLicencedApplicationsAdmin(admin.ModelAdmin):
    pass


class VHostLicensedApplicationAccountingSetupEntry(models.Model):
    uuid = models.UUIDField(default=uuid4,primary_key=True)
    vhost = models.ForeignKey(VHost, on_delete=models.CASCADE)
    application = models.ForeignKey(AvailableApplication, on_delete=models.CASCADE)
    name = models.TextField(verbose_name="Entry Name")
    percentage = models.IntegerField(default=0,verbose_name="Entry Percentage (for deductions)")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"VHost: {self.vhost.name}  - {self.application.name} Licensing Accounting Expense Entry: {self.name}: {self.percentage}%"


@admin.register(VHostLicensedApplicationAccountingSetupEntry)
class VHostLicensedApplicationAccountingSetupEntryAdmin(admin.ModelAdmin):
    pass

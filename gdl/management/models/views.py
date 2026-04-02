from django.contrib import admin
from django.db import models

from account.models import Account
from parameters.models import VHost


class MV_LiabilityView(models.Model):
    class Meta:
        managed = False
        db_table = "mv_wager_liability"
    vhost  = models.ForeignKey(VHost,on_delete=models.SET_NULL, null=True)
    wager_count = models.BigIntegerField()
    total_risk = models.DecimalField(max_digits=20, decimal_places=2)
    total_win = models.DecimalField(max_digits=20, decimal_places=2)
    factor = models.DecimalField(max_digits=20, decimal_places=8)


@admin.register(MV_LiabilityView)
class MV_LiabilityViewAdmin(admin.ModelAdmin):
    pass


class MV_AccountActiveThisWeek(models.Model):
    class Meta:
        managed = False
        db_table = "mv_account_active_this_week"
    id = models.UUIDField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    vhost_id = models.UUIDField(null=True)
    domain_id = models.UUIDField(null=True)
    week_start = models.DateTimeField()

@admin.register(MV_AccountActiveThisWeek)
class MV_AccountActiveThisWeekAdmin(admin.ModelAdmin):
    pass

class MV_AccountActiveToday(models.Model):
    class Meta:
        managed = False
        db_table = "mv_account_active_today"
    id = models.UUIDField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    vhost_id = models.UUIDField(null=True)
    domain_id = models.UUIDField(null=True)


@admin.register(MV_AccountActiveToday)
class MV_AccountActiveTodayAdmin(admin.ModelAdmin):
    pass

class MV_AccountsCreatedThisWeek(models.Model):
    class Meta:
        managed = False
        db_table = "mv_account_created_this_week"
    id = models.UUIDField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    vhost_id = models.UUIDField(null=True)
    domain_id = models.UUIDField(null=True)
    week_start = models.DateTimeField()

@admin.register(MV_AccountsCreatedThisWeek)
class MV_AccountsCreatedThisWeekAdmin(admin.ModelAdmin):
    pass

class MV_AccountsCreatedToday(models.Model):
    class Meta:
        managed = False
        db_table = "mv_account_created_today"
    id = models.UUIDField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    vhost_id = models.UUIDField(null=True)
    domain_id = models.UUIDField(null=True)

@admin.register(MV_AccountsCreatedToday)
class MV_AccountsCreatedTodayAdmin(admin.ModelAdmin):
    pass




class MV_TicketStatsBase(models.Model):
    id = models.UUIDField(primary_key=True)
    period_start = models.DateTimeField()
    tickets_sold = models.BigIntegerField()
    ticket_volume = models.DecimalField(max_digits=20, decimal_places=5)
    ticket_wins = models.DecimalField(max_digits=20, decimal_places=5)
    ticket_losses = models.DecimalField(max_digits=20, decimal_places=5)
    class Meta:
        abstract = True
        managed = False


class MV_TicketDetailsBase(models.Model):
    id = models.UUIDField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    manager = models.ForeignKey('management.Manager',on_delete=models.SET_NULL, null=True)
    wager = models.ForeignKey('wager.Wager',on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    vhost = models.ForeignKey('parameters.VHost',on_delete=models.SET_NULL, null=True)
    risk = models.DecimalField(max_digits=20, decimal_places=5)
    win = models.DecimalField(max_digits=20, decimal_places=5)
    grade_outcome = models.CharField(max_length=20, null=True)
    graded_at  = models.DateTimeField(null=True)

    class Meta:
        abstract = True
        managed = False



class MV_TicketStatsDaily(MV_TicketStatsBase):
    day_net = models.DecimalField(max_digits=20, decimal_places=5)

    class Meta:
        managed = False
        db_table = "mv_ticket_stats_daily"
        verbose_name = "Ticket Stats (Daily)"
        verbose_name_plural = "Ticket Stats (Daily)"

@admin.register(MV_TicketStatsDaily)
class MV_TicketStatsDailyAdmin(admin.ModelAdmin):
    pass


class MV_TicketStatsWeek(MV_TicketStatsBase):
    week_net = models.DecimalField(max_digits=20, decimal_places=5)
    class Meta:
        managed = False
        db_table = "mv_ticket_stats_week"
        verbose_name = "Ticket Stats (This Week)"
        verbose_name_plural = "Ticket Stats (This Week)"

@admin.register(MV_TicketStatsWeek)
class MV_TicketStatsWeekAdmin(admin.ModelAdmin):
    pass

class MV_TicketStatsLastWeek(MV_TicketStatsBase):
    week_net = models.DecimalField(max_digits=20, decimal_places=5)

    class Meta:
        managed = False
        db_table = "mv_ticket_stats_last_week"
        verbose_name = "Ticket Stats (Last Week)"
        verbose_name_plural = "Ticket Stats (Last Week)"

@admin.register(MV_TicketStatsLastWeek)
class MV_TicketStatsLastWeekAdmin(admin.ModelAdmin):
    pass

class MV_TicketStatsMonth(MV_TicketStatsBase):
    month_net = models.DecimalField(max_digits=20, decimal_places=5)

    class Meta:
        managed = False
        db_table = "mv_ticket_stats_month"
        verbose_name = "Ticket Stats (Running Month)"
        verbose_name_plural = "Ticket Stats (Running Month)"

@admin.register(MV_TicketStatsMonth)
class MV_TicketStatsMonthAdmin(admin.ModelAdmin):
    pass



class MV_TicketsMonthDetails(MV_TicketDetailsBase):
    month_start = models.DateTimeField()
    month_end = models.DateTimeField()
    class Meta:
        managed = False
        db_table = "mv_tickets_month_details"

@admin.register(MV_TicketsMonthDetails)
class MV_TicketsMonthDetailsAdmin(admin.ModelAdmin):
    pass


class MV_TicketsDailyDetails(MV_TicketDetailsBase):
    day_start = models.DateTimeField()
    day_end = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "mv_tickets_day_details"


@admin.register(MV_TicketsDailyDetails)
class MV_TicketsDailyDetailsAdmin(admin.ModelAdmin):
    pass


class MV_TicketsWeekDetails(MV_TicketDetailsBase):
    week_start = models.DateTimeField()
    week_end = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "mv_tickets_week_details"


@admin.register(MV_TicketsWeekDetails)
class MV_TicketsWeekDetailsAdmin(admin.ModelAdmin):
    pass

class MV_TicketsLastWeekDetails(MV_TicketDetailsBase):
    week_start = models.DateTimeField()
    week_end = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "mv_tickets_lastweek_details"


@admin.register(MV_TicketsLastWeekDetails)
class MV_TicketsLastWeekDetailsAdmin(admin.ModelAdmin):
    pass
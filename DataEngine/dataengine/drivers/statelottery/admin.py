from django.contrib import admin
from django.utils.html import format_html

from .models import LotteryGame, LotteryDraw, LotteryScrapeLog


@admin.register(LotteryGame)
class LotteryGameAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'state',
        'game_type',
        'active',
        'main_numbers_display',
        'bonus_numbers_display',
        'updated_at',
    ]
    list_filter = ['state', 'game_type', 'active']
    search_fields = ['name', 'slug']
    ordering = ['state', 'name']

    readonly_fields = ['uuid', 'created_at', 'updated_at']

    fieldsets = (
        (None, {
            'fields': ('uuid', 'state', 'name', 'slug', 'url', 'active')
        }),
        ('Game Format', {
            'fields': (
                'game_type',
                'main_count',
                'main_range_min',
                'main_range_max',
                'bonus_count',
                'bonus_range_min',
                'bonus_range_max',
                'is_positional',
            )
        }),
        ('Configuration', {
            'fields': ('schedule', 'selectors', 'parser_config'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def main_numbers_display(self, obj):
        return f"{obj.main_count} from {obj.main_range_min}-{obj.main_range_max}"
    main_numbers_display.short_description = 'Main Numbers'

    def bonus_numbers_display(self, obj):
        if obj.bonus_count > 0:
            return f"{obj.bonus_count} from {obj.bonus_range_min}-{obj.bonus_range_max}"
        return "-"
    bonus_numbers_display.short_description = 'Bonus Numbers'


@admin.register(LotteryDraw)
class LotteryDrawAdmin(admin.ModelAdmin):
    list_display = [
        'game',
        'draw_date',
        'draw_label',
        'numbers_display',
        'scrape_success',
        'created_at',
    ]
    list_filter = ['game__state', 'game', 'scrape_success', 'draw_date']
    search_fields = ['game__name', 'draw_number']
    ordering = ['-draw_date', '-draw_datetime']
    date_hierarchy = 'draw_date'

    readonly_fields = ['uuid', 'created_at', 'updated_at', 'numbers_display']

    fieldsets = (
        (None, {
            'fields': ('uuid', 'game', 'draw_date', 'draw_datetime', 'draw_label', 'draw_number')
        }),
        ('Results', {
            'fields': ('main_numbers', 'bonus_numbers', 'numbers_display')
        }),
        ('Scrape Info', {
            'fields': ('scrape_success', 'raw_response'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(LotteryScrapeLog)
class LotteryScrapeLogAdmin(admin.ModelAdmin):
    list_display = [
        'game',
        'attempted_at',
        'success_display',
        'retry_count',
        'scrape_duration_ms',
        'draw_found',
    ]
    list_filter = ['success', 'game__state', 'game']
    search_fields = ['game__name', 'error_message']
    ordering = ['-attempted_at']
    date_hierarchy = 'attempted_at'

    readonly_fields = ['uuid', 'attempted_at']

    fieldsets = (
        (None, {
            'fields': ('uuid', 'game', 'attempted_at')
        }),
        ('Result', {
            'fields': ('success', 'draw_found', 'scrape_duration_ms', 'retry_count')
        }),
        ('Error Details', {
            'fields': ('error_message', 'screenshot_path'),
            'classes': ('collapse',),
        }),
    )

    def success_display(self, obj):
        if obj.success:
            return format_html('<span style="color: green;">&#10004;</span>')
        return format_html('<span style="color: red;">&#10008;</span>')
    success_display.short_description = 'Success'

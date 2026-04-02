import uuid
from django.db import models


class LotteryGame(models.Model):
    """
    Defines a lottery game configuration for scraping.
    Each game belongs to a state and has specific rules for number formats,
    draw schedules, and scraping selectors.
    """
    GAME_TYPE_CHOICES = [
        ('pool', 'Pool'),           # Pick N unique numbers from range (e.g., NY Lotto)
        ('positional', 'Positional'),  # Digits 0-9 in positions (e.g., Daily 4)
        ('bonus', 'Bonus'),         # Pool + separate bonus number(s) (e.g., Powerball)
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost_id = models.UUIDField(null=True, blank=True, db_index=True, help_text="VHost UUID reference (cross-database)")
    # Identification
    state = models.CharField(max_length=10, help_text="State code (e.g., NY, CA, MULTI)")
    name = models.CharField(max_length=100, help_text="Display name (e.g., New York Lotto)")
    slug = models.SlugField(unique=True, help_text="URL-safe identifier (e.g., ny-lotto)")
    url = models.URLField(help_text="Scrape target URL")

    # Game type and format
    game_type = models.CharField(max_length=20, choices=GAME_TYPE_CHOICES, default='pool')
    main_count = models.IntegerField(help_text="Number of main numbers to pick")
    main_range_min = models.IntegerField(default=1, help_text="Minimum value for main numbers")
    main_range_max = models.IntegerField(help_text="Maximum value for main numbers")
    bonus_count = models.IntegerField(default=0, help_text="Number of bonus numbers (0 if none)")
    bonus_range_min = models.IntegerField(null=True, blank=True, help_text="Minimum value for bonus")
    bonus_range_max = models.IntegerField(null=True, blank=True, help_text="Maximum value for bonus")
    is_positional = models.BooleanField(default=False, help_text="True for positional games like Daily 4")

    # Schedule configuration (stored as JSON)
    # Format: {"days": ["wednesday", "saturday"], "times": [{"time": "20:15", "label": null}], "timezone": "America/New_York"}
    schedule = models.JSONField(default=dict, help_text="Draw schedule configuration")

    # Scraping configuration (stored as JSON, database-driven)
    # Format: {"winning_numbers": ".ball", "bonus_number": ".bonus-ball", "draw_date": ".draw-date"}
    selectors = models.JSONField(default=dict, help_text="CSS selectors for scraping")

    # Parser configuration (stored as JSON)
    # Format: {"number_extractor": "text_content", "date_format": "%A, %B %d, %Y"}
    parser_config = models.JSONField(default=dict, help_text="Parsing rules")

    # Status
    active = models.BooleanField(default=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    class Meta:
        ordering = ['state', 'name']
        verbose_name = "Lottery Game"
        verbose_name_plural = "Lottery Games"

    def __str__(self):
        return f"{self.state} - {self.name}"

    def get_scraper_class(self):
        """Return the appropriate scraper class for this game's state."""
        from ..scrapers import get_scraper_for_state
        return get_scraper_for_state(self.state)

    @property
    def main_range(self):
        """Return the range for main numbers as a tuple."""
        return (self.main_range_min, self.main_range_max)

    @property
    def bonus_range(self):
        """Return the range for bonus numbers as a tuple, or None if no bonus."""
        if self.bonus_count > 0 and self.bonus_range_min and self.bonus_range_max:
            return (self.bonus_range_min, self.bonus_range_max)
        return None

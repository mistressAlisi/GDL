import uuid
from django.db import models
from .game import LotteryGame


class LotteryDraw(models.Model):
    """
    Stores the results of a lottery draw.
    Supports multiple draws per day (midday/evening) via draw_label.
    """
    DRAW_LABEL_CHOICES = [
        ('midday', 'Midday'),
        ('evening', 'Evening'),
        ('morning', 'Morning'),
        ('night', 'Night'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost_id = models.UUIDField(null=True, blank=True, db_index=True, help_text="VHost UUID reference (cross-database)")

    # Link to game
    game = models.ForeignKey(
        LotteryGame,
        on_delete=models.CASCADE,
        related_name='draws'
    )

    # Draw timing
    draw_date = models.DateField(help_text="Date of the draw")
    draw_datetime = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Exact draw time if known"
    )
    draw_label = models.CharField(
        max_length=20,
        choices=DRAW_LABEL_CHOICES,
        null=True,
        blank=True,
        help_text="Label for multi-draw days (midday, evening, etc.)"
    )
    draw_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Official draw number if available"
    )

    # Results
    main_numbers = models.JSONField(
        default=list,
        help_text="List of main winning numbers"
    )
    bonus_numbers = models.JSONField(
        default=list,
        help_text="List of bonus numbers (empty if none)"
    )

    # Scrape metadata
    raw_response = models.TextField(
        blank=True,
        default='',
        help_text="Scraped HTML for debugging"
    )
    scrape_success = models.BooleanField(
        default=True,
        help_text="Whether the scrape succeeded"
    )
    manual_override = models.BooleanField(
        default=False,
        help_text="Whether this draw was manually entered/corrected"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('game', 'draw_date', 'draw_label')
        ordering = ['-draw_date', '-draw_datetime']
        verbose_name = "Lottery Draw"
        verbose_name_plural = "Lottery Draws"

    def __str__(self):
        label = f" ({self.draw_label})" if self.draw_label else ""
        return f"{self.game.name} - {self.draw_date}{label}"

    @property
    def numbers_display(self):
        """Return a formatted string of the winning numbers."""
        main = ', '.join(str(n) for n in self.main_numbers)
        if self.bonus_numbers:
            bonus = ', '.join(str(n) for n in self.bonus_numbers)
            return f"{main} + {bonus}"
        return main

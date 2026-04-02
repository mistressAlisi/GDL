import uuid
from django.db import models
from .game import LotteryGame
from .draw import LotteryDraw


class LotteryScrapeLog(models.Model):
    """
    Logs every scrape attempt for monitoring and debugging.
    Tracks success/failure, error messages, and retry counts.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    vhost_id = models.UUIDField(null=True, blank=True, db_index=True, help_text="VHost UUID reference (cross-database)")
    # Link to game
    game = models.ForeignKey(
        LotteryGame,
        on_delete=models.CASCADE,
        related_name='scrape_logs'
    )

    # Scrape details
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the scrape was attempted"
    )
    success = models.BooleanField(
        default=False,
        help_text="Whether the scrape succeeded"
    )
    error_message = models.TextField(
        blank=True,
        default='',
        help_text="Error details if scrape failed"
    )
    retry_count = models.IntegerField(
        default=0,
        help_text="Number of retries before this attempt"
    )

    # Result link (if successful)
    draw_found = models.ForeignKey(
        LotteryDraw,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scrape_logs',
        help_text="The draw record created/found if successful"
    )

    # Additional metadata
    scrape_duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Time taken to scrape in milliseconds"
    )
    screenshot_path = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text="Path to failure screenshot if captured"
    )

    class Meta:
        ordering = ['-attempted_at']
        verbose_name = "Scrape Log"
        verbose_name_plural = "Scrape Logs"

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.game.name} - {self.attempted_at} - {status}"

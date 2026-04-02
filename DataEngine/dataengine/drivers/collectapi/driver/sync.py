import logging
from datetime import datetime, timedelta
from django.utils.timezone import now, make_aware
from django.db import transaction
from django.conf import settings

from dataengine.drivers.collectapi.api import CollectAPIClient
from dataengine.drivers.collectapi.models import (
    LotteryType, LotteryDraw, LotterySyncStatus, LotteryPayoutConfig
)
from matches.models import Match
from sports.models import Sport


class CollectAPIDriver:
    """Main driver class for syncing lottery data from CollectAPI"""
    
    def __init__(self, vhost, logger=None):
        self.vhost = vhost
        self.logger = logger or logging.getLogger(__name__)
        self.client = CollectAPIClient(vhost, logger)
        self.name = "CollectAPI Lottery Driver"
        
    def setup_lottery_types(self):
        """Initialize lottery types in the database"""
        lottery_configs = [
            {
                "name": "USA Powerball",
                "slug": "usa-powerball",
                "api_endpoint": "usaPowerball",
                "checker_endpoint": "usaPowerballChecker"
            },
            {
                "name": "USA Mega Millions",
                "slug": "usa-megamillions",
                "api_endpoint": "usaMegaMillions",
                "checker_endpoint": "usaMegaMillionsChecker"
            }
        ]
        
        for config in lottery_configs:
            lottery_type, created = LotteryType.objects.get_or_create(
                vhost=self.vhost,
                slug=config["slug"],
                defaults={
                    "name": config["name"],
                    "api_endpoint": config["api_endpoint"],
                    "checker_endpoint": config["checker_endpoint"],
                    "active": True
                }
            )
            if created:
                self.logger.info(f"Created lottery type: {lottery_type.name}")
            else:
                self.logger.info(f"Lottery type already exists: {lottery_type.name}")
                
        return LotteryType.objects.filter(vhost=self.vhost, active=True)
    
    def create_lottery_match(self, lottery_draw):
        """Create a match for a lottery draw"""
        # Get or create lottery sport
        sport, _ = Sport.objects.get_or_create(
            name=lottery_draw.lottery_type.name,
            defaults={
                'vhost': self.vhost,
                'active': True
            }
        )
        
        # Create unique match ID
        match_id = f"{lottery_draw.lottery_type.slug}_{lottery_draw.draw_date}"
        
        # Create or update match
        match, created = Match.objects.get_or_create(
            id=match_id,
            defaults={
                'sport': sport,
                'vhost': self.vhost,
                'commence_time': lottery_draw.draw_datetime or make_aware(
                    datetime.combine(lottery_draw.draw_date, datetime.min.time())
                ),
                'is_outrights': True,
                'name': f"{lottery_draw.lottery_type.name} - {lottery_draw.draw_date}",
                'base_line': 10000,  # Default multiplier
                'open': True,
                'active': True,
                'finished': False
            }
        )
        
        if created:
            self.logger.info(f"Created match for {lottery_draw.lottery_type.name} draw on {lottery_draw.draw_date}")
        
        # If we have results, mark the match as finished
        if lottery_draw.main_numbers and len(lottery_draw.main_numbers) > 0:
            if not match.finished:
                match.finished = True
                match.open = False
                match.finished_at = now()
                match.status_short = "FINAL"
                match.status_long = "Draw Complete"
                match.scoring_data = {
                    "main_numbers": lottery_draw.main_numbers,
                    "bonus_numbers": lottery_draw.bonus_numbers,
                    "multiplier": lottery_draw.multiplier
                }
                match.save()
                self.logger.info(f"Marked match {match_id} as finished with results")
        
        return match
    
    def sync_powerball(self):
        """Sync latest Powerball results"""
        try:
            lottery_type = LotteryType.objects.get(
                vhost=self.vhost,
                slug="usa-powerball"
            )
        except LotteryType.DoesNotExist:
            self.logger.error("Powerball lottery type not found. Run setup first.")
            return None, None
        
        # Get latest results from API
        response = self.client.get_powerball()
        if not response:
            self._update_sync_status(lottery_type, success=False, 
                                    error="Failed to fetch Powerball data")
            return None, None
        
        # Parse response
        parsed_data = self.client.parse_powerball_response(response)
        if not parsed_data:
            self._update_sync_status(lottery_type, success=False,
                                    error="Failed to parse Powerball response")
            return None, None
        
        # Save or update draw
        with transaction.atomic():
            draw, created = LotteryDraw.objects.update_or_create(
                lottery_type=lottery_type,
                draw_date=parsed_data["draw_date"],
                defaults={
                    "main_numbers": parsed_data["main_numbers"],
                    "bonus_numbers": parsed_data["bonus_numbers"],
                    "multiplier": parsed_data.get("multiplier"),
                    "jackpot_amount": parsed_data.get("jackpot_amount"),
                    "next_jackpot": parsed_data.get("next_jackpot"),
                    "raw_response": parsed_data["raw_response"],
                    "updated_at": now()
                }
            )
            
            action = "Created" if created else "Updated"
            self.logger.info(f"{action} Powerball draw for {draw.draw_date}")
            
            # Create or update match for this draw
            match = self.create_lottery_match(draw)
            
            self._update_sync_status(lottery_type, success=True,
                                    last_draw_date=draw.draw_date)
            
            # Return draw and match for further processing
            return draw, match
        
        return None, None
    
    def sync_megamillions(self):
        """Sync latest Mega Millions results"""
        try:
            lottery_type = LotteryType.objects.get(
                vhost=self.vhost,
                slug="usa-megamillions"
            )
        except LotteryType.DoesNotExist:
            self.logger.error("Mega Millions lottery type not found. Run setup first.")
            return None, None
        
        # Get latest results from API
        response = self.client.get_megamillions()
        if not response:
            self._update_sync_status(lottery_type, success=False,
                                    error="Failed to fetch Mega Millions data")
            return None, None
        
        # Parse response
        parsed_data = self.client.parse_megamillions_response(response)
        if not parsed_data:
            self._update_sync_status(lottery_type, success=False,
                                    error="Failed to parse Mega Millions response")
            return None, None
        
        # Save or update draw
        with transaction.atomic():
            draw, created = LotteryDraw.objects.update_or_create(
                lottery_type=lottery_type,
                draw_date=parsed_data["draw_date"],
                defaults={
                    "main_numbers": parsed_data["main_numbers"],
                    "bonus_numbers": parsed_data["bonus_numbers"],
                    "multiplier": parsed_data.get("multiplier"),
                    "jackpot_amount": parsed_data.get("jackpot_amount"),
                    "next_jackpot": parsed_data.get("next_jackpot"),
                    "raw_response": parsed_data["raw_response"],
                    "updated_at": now()
                }
            )
            
            action = "Created" if created else "Updated"
            self.logger.info(f"{action} Mega Millions draw for {draw.draw_date}")
            
            # Create or update match for this draw
            match = self.create_lottery_match(draw)
            
            self._update_sync_status(lottery_type, success=True,
                                    last_draw_date=draw.draw_date)
            
            # Return draw and match for further processing
            return draw, match
        
        return None, None
    
    def sync_all(self):
        """Sync all active lottery types"""
        results = {}
        
        # Ensure lottery types are set up
        self.setup_lottery_types()
        
        # Sync Powerball
        self.logger.info("Syncing Powerball...")
        results["powerball"] = self.sync_powerball()
        
        # Sync Mega Millions
        self.logger.info("Syncing Mega Millions...")
        results["megamillions"] = self.sync_megamillions()
        
        return results
    
    def _update_sync_status(self, lottery_type, success=True, error=None, last_draw_date=None):
        """Update sync status for a lottery type"""
        status, created = LotterySyncStatus.objects.get_or_create(
            lottery_type=lottery_type,
            defaults={
                "last_sync": now(),
                "success": success,
                "error_message": error,
                "sync_count": 1
            }
        )
        
        if not created:
            status.last_sync = now()
            status.success = success
            status.error_message = error
            status.sync_count += 1
            
        if last_draw_date:
            status.last_draw_date = last_draw_date
            
        status.save()
        
    def check_ticket(self, lottery_slug, numbers, bonus_number, multiplier=False, account=None):
        """
        Check a lottery ticket against the latest draw
        
        Args:
            lottery_slug: 'usa-powerball' or 'usa-megamillions'
            numbers: List of main numbers
            bonus_number: Powerball or Megaball number
            multiplier: Power Play or Megaplier selected
            account: Optional account to associate with check
        """
        try:
            lottery_type = LotteryType.objects.get(
                vhost=self.vhost,
                slug=lottery_slug
            )
            
            # Get latest draw
            latest_draw = LotteryDraw.objects.filter(
                lottery_type=lottery_type
            ).first()
            
            if not latest_draw:
                self.logger.error(f"No draws found for {lottery_slug}")
                return None
            
            # Call appropriate checker API
            if lottery_slug == "usa-powerball":
                response = self.client.check_powerball_ticket(
                    numbers, bonus_number, multiplier
                )
            elif lottery_slug == "usa-megamillions":
                response = self.client.check_megamillions_ticket(
                    numbers, bonus_number, multiplier
                )
            else:
                self.logger.error(f"Unknown lottery slug: {lottery_slug}")
                return None
            
            if response and response.get("result"):
                result = response["result"]
                
                # Create ticket check record
                from dataengine.drivers.collectapi.models import LotteryTicketCheck
                
                ticket_check = LotteryTicketCheck.objects.create(
                    lottery_draw=latest_draw,
                    account=account,
                    user_main_numbers=numbers,
                    user_bonus_number=bonus_number,
                    user_multiplier=multiplier,
                    main_matches=result.get("mainMatches", 0),
                    bonus_match=result.get("bonusMatch", False),
                    prize_tier=result.get("prizeTier"),
                    prize_amount=result.get("prizeAmount", 0),
                    is_winner=result.get("isWinner", False)
                )
                
                return ticket_check
                
        except Exception as e:
            self.logger.error(f"Error checking ticket: {e}")
            return None


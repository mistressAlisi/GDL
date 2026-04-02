import json
import logging
import re
import requests
from datetime import datetime, timedelta
from decimal import Decimal
from django.utils.timezone import now
from parameters.models import VHostParameterRegistry


class CollectAPIClient:
    BASE_URL = "https://api.collectapi.com/chancegame"
    
    def __init__(self, vhost, logger=None):
        self.vhost = vhost
        self.logger = logger or logging.getLogger(__name__)
        self.api_key = None
        self.regappid = "dataengine.drivers.collectapi"
        
    def _get_api_key(self):
        if not self.api_key:
            try:
                api_key_param = VHostParameterRegistry.objects.get(
                    vhost=self.vhost,
                    application=self.regappid,
                    name="api_key"
                )
                self.api_key = api_key_param.value_text
            except VHostParameterRegistry.DoesNotExist:
                self.logger.error(f"API key not configured for vhost {self.vhost}")
                raise ValueError("CollectAPI key not configured")
        return self.api_key
    
    def _make_request(self, endpoint, method="GET", data=None):
        url = f"{self.BASE_URL}/{endpoint}"
        headers = {
            "Authorization": f"apikey {self._get_api_key()}",
            "content-type": "application/json"
        }
        
        try:
            self.logger.info(f"Making {method} request to {url} with headers: {headers}")
            
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                self.logger.info(f"Successful response from {endpoint}")
                return result
            else:
                self.logger.error(f"API returned success=false for {endpoint}: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {endpoint}: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response from {endpoint}: {e}")
            return None
    
    def get_powerball(self):
        """Get latest USA Powerball results"""
        return self._make_request("usaPowerball")
    
    def get_megamillions(self):
        """Get latest USA Mega Millions results"""
        return self._make_request("usaMegaMillions")
    
    def check_powerball_ticket(self, numbers, powerball, powerplay=False):
        """
        Check a Powerball ticket against the latest draw
        
        Args:
            numbers: List of 5 main numbers
            powerball: The Powerball number
            powerplay: Whether Power Play was selected
        """
        data = {
            "numbers": numbers,
            "powerball": powerball,
            "powerplay": powerplay
        }
        return self._make_request("usaPowerballChecker", method="POST", data=data)
    
    def check_megamillions_ticket(self, numbers, megaball, megaplier=False):
        """
        Check a Mega Millions ticket against the latest draw
        
        Args:
            numbers: List of 5 main numbers
            megaball: The Megaball number
            megaplier: Whether Megaplier was selected
        """
        data = {
            "numbers": numbers,
            "megaball": megaball,
            "megaplier": megaplier
        }
        return self._make_request("usaMegaMillionsChecker", method="POST", data=data)
    
    def _parse_jackpot_amount(self, jackpot_str):
        """
        Parse jackpot amount strings like '$1.79 Billion' or '$300 Million' to Decimal
        
        Args:
            jackpot_str: String representation of jackpot (e.g., '$1.79 Billion')
            
        Returns:
            Decimal: The numeric value or None if parsing fails
        """
        if not jackpot_str:
            return None
            
        if isinstance(jackpot_str, (int, float)):
            return Decimal(str(jackpot_str))
            
        try:
            # Remove $ and any commas
            clean_str = str(jackpot_str).replace('$', '').replace(',', '').strip()
            
            # Handle billion/million/thousand suffixes
            multipliers = {
                'billion': 1000000000,
                'million': 1000000,
                'thousand': 1000,
                'k': 1000,
                'm': 1000000,
                'b': 1000000000
            }
            
            # Check for multiplier words
            for suffix, multiplier in multipliers.items():
                if suffix in clean_str.lower():
                    # Extract the numeric part
                    numeric_part = re.findall(r'[\d.]+', clean_str)
                    if numeric_part:
                        value = Decimal(numeric_part[0]) * multiplier
                        return value
            
            # If no multiplier, try to parse as regular number
            numeric_part = re.findall(r'[\d.]+', clean_str)
            if numeric_part:
                return Decimal(numeric_part[0])
                
        except Exception as e:
            self.logger.warning(f"Failed to parse jackpot amount '{jackpot_str}': {e}")
            
        return None
    
    def parse_powerball_response(self, response):
        """Parse Powerball API response into structured data"""
        if not response or not response.get("result"):
            return None
            
        result = response["result"]
        
        # Parse draw date
        draw_date_str = result.get("date", "")
        try:
            draw_date = datetime.strptime(draw_date_str, "%Y-%m-%d").date()
        except:
            draw_date = now().date()
        
        # Parse numbers
        numbers = result.get("numbers", [])
        powerball = result.get("powerball")
        powerplay = result.get("powerplay")
        
        # Parse jackpot
        jackpot = self._parse_jackpot_amount(result.get("jackpot", 0))
        next_jackpot = self._parse_jackpot_amount(result.get("nextJackpot", 0))
        
        return {
            "draw_date": draw_date,
            "main_numbers": numbers,
            "bonus_numbers": [powerball] if powerball else [],
            "multiplier": powerplay,
            "jackpot_amount": jackpot,
            "next_jackpot": next_jackpot,
            "raw_response": result
        }
    
    def parse_megamillions_response(self, response):
        """Parse Mega Millions API response into structured data"""
        if not response or not response.get("result"):
            return None
            
        result = response["result"]
        
        # Parse draw date
        draw_date_str = result.get("date", "")
        try:
            draw_date = datetime.strptime(draw_date_str, "%Y-%m-%d").date()
        except:
            draw_date = now().date()
        
        # Parse numbers
        numbers = result.get("numbers", [])
        megaball = result.get("megaball")
        megaplier = result.get("megaplier")
        
        # Parse jackpot
        jackpot = self._parse_jackpot_amount(result.get("jackpot", 0))
        next_jackpot = self._parse_jackpot_amount(result.get("nextJackpot", 0))
        
        return {
            "draw_date": draw_date,
            "main_numbers": numbers,
            "bonus_numbers": [megaball] if megaball else [],
            "multiplier": megaplier,
            "jackpot_amount": jackpot,
            "next_jackpot": next_jackpot,
            "raw_response": result
        }

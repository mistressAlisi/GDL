import logging
from django.utils.timezone import now, localdate

from dataengine.drivers.collectapi.driver.sync import CollectAPIDriver
from dataengine.drivers.collectapi.models import LotteryDraw, LotteryType
from qualifier.modules.lottery import LotteryQualifier
from matches.models import Match
from matches.signals import states as state_signals
from parameters.models import VHost
from wager.models import Wager


logger = logging.getLogger(__name__)


def sync_lottery_draws(vhost_uuid=None):
    """
    Sync lottery draws from CollectAPI and create matches
    
    Args:
        vhost_uuid: Optional VHost UUID, if not provided uses default
    
    Returns:
        dict: Summary of sync results
    """
    
    # Get VHost
    if vhost_uuid:
        try:
            vhost = VHost.objects.get(uuid=vhost_uuid)
        except VHost.DoesNotExist:
            logger.error(f"VHost {vhost_uuid} not found")
            return {"error": "VHost not found"}
    else:
        # Get default VHost or first active one
        vhost = VHost.objects.filter(active=True).first()
        if not vhost:
            logger.error("No active VHost found")
            return {"error": "No active VHost found"}
    
    # Initialize driver
    driver = CollectAPIDriver(vhost, logger)
    
    results = {
        "vhost": str(vhost.uuid),
        "timestamp": now().isoformat(),
        "powerball": None,
        "megamillions": None,
        "errors": []
    }
    
    # Setup lottery types if needed
    driver.setup_lottery_types()
    
    # Sync Powerball
    try:
        logger.info("Syncing Powerball...")
        draw, match = driver.sync_powerball()
        
        if draw and match:
            results["powerball"] = {
                "draw_date": str(draw.draw_date),
                "match_id": match.id,
                "finished": match.finished,
                "numbers": draw.main_numbers,
                "bonus": draw.bonus_numbers
            }
            
            # If match is finished (has results), trigger qualification
            if match.finished:
                qualify_lottery_draw(str(match.uuid))
                results["powerball"]["qualification_triggered"] = True
        else:
            results["errors"].append("Failed to sync Powerball")
            
    except Exception as e:
        logger.error(f"Error syncing Powerball: {e}")
        results["errors"].append(f"Powerball sync error: {str(e)}")
    
    # Sync Mega Millions
    try:
        logger.info("Syncing Mega Millions...")
        draw, match = driver.sync_megamillions()
        
        if draw and match:
            results["megamillions"] = {
                "draw_date": str(draw.draw_date),
                "match_id": match.id,
                "finished": match.finished,
                "numbers": draw.main_numbers,
                "bonus": draw.bonus_numbers
            }
            
            # If match is finished (has results), trigger qualification
            if match.finished:
                qualify_lottery_draw(str(match.uuid))
                results["megamillions"]["qualification_triggered"] = True
        else:
            results["errors"].append("Failed to sync Mega Millions")
            
    except Exception as e:
        logger.error(f"Error syncing Mega Millions: {e}")
        results["errors"].append(f"Mega Millions sync error: {str(e)}")
    
    logger.info(f"Lottery sync completed: {results}")
    return results


def qualify_lottery_draw(match_uuid):
    """
    Qualify all lottery wagers for a specific draw
    
    Args:
        match_uuid: UUID of the Match representing the lottery draw
    
    Returns:
        dict: Summary of qualification results
    """
    
    try:
        match = Match.objects.get(uuid=match_uuid)
    except Match.DoesNotExist:
        logger.error(f"Match {match_uuid} not found")
        return {"error": "Match not found"}
    
    # Check if match is finished
    if not match.finished:
        logger.warning(f"Match {match.id} is not finished yet, skipping qualification")
        return {"error": "Match not finished"}
    
    # Initialize qualifier
    qualifier = LotteryQualifier()
    
    # Qualify all wagers for this draw
    results = qualifier.qualify_lottery_wagers_for_match(match)
    
    # Add match info to results
    results["match_id"] = match.id
    results["match_name"] = match.name
    
    # Send signal that match qualification is complete
    if results["total"] > 0:
        state_signals.signal_match_qualified.send(
            sender=LotteryQualifier,
            match=match,
            qualified_count=results["winners"] + results["losers"],
            winner_count=results["winners"]
        )
    
    logger.info(f"Lottery qualification completed for {match.id}: {results}")
    return results


def sync_and_qualify_all_lotteries():
    """
    Combined task to sync all lottery draws and qualify wagers.
    This should be scheduled to run after each draw time.
    """
    
    logger.info("Starting comprehensive lottery sync and qualification...")
    
    # Get all active VHosts
    vhosts = VHost.objects.filter(active=True)
    
    all_results = []
    
    for vhost in vhosts:
        logger.info(f"Processing VHost: {vhost}")
        
        # Sync draws for this VHost
        sync_results = sync_lottery_draws(str(vhost.uuid))
        all_results.append(sync_results)
    
    return {
        "timestamp": now().isoformat(),
        "vhosts_processed": vhosts.count(),
        "results": all_results
    }


def create_upcoming_lottery_matches():
    """
    Create matches for upcoming lottery draws (for betting purposes).
    This should run daily to ensure upcoming draws have matches available.
    """
    
    from datetime import datetime, timedelta
    
    results = {
        "created_matches": [],
        "errors": []
    }
    
    # Get all active lottery types
    lottery_types = LotteryType.objects.filter(active=True)
    
    for lottery_type in lottery_types:
        try:
            # Determine next draw dates based on lottery schedule
            today = localdate().isoformat()
            next_draws = []
            
            if "powerball" in lottery_type.slug.lower():
                # Powerball draws on Wednesday and Saturday
                for i in range(7):
                    check_date = today + timedelta(days=i)
                    # 2 = Wednesday, 5 = Saturday
                    if check_date.weekday() in [2, 5]:
                        next_draws.append(check_date)
                        if len(next_draws) >= 2:  # Get next 2 draws
                            break
                            
            elif "megamillions" in lottery_type.slug.lower():
                # Mega Millions draws on Tuesday and Friday
                for i in range(7):
                    check_date = today + timedelta(days=i)
                    # 1 = Tuesday, 4 = Friday
                    if check_date.weekday() in [1, 4]:
                        next_draws.append(check_date)
                        if len(next_draws) >= 2:  # Get next 2 draws
                            break
            
            # Create matches for upcoming draws
            for draw_date in next_draws:
                # Check if draw already exists
                exists = LotteryDraw.objects.filter(
                    lottery_type=lottery_type,
                    draw_date=draw_date
                ).exists()
                
                if not exists:
                    # Create placeholder draw
                    draw = LotteryDraw.objects.create(
                        lottery_type=lottery_type,
                        draw_date=draw_date,
                        draw_datetime=datetime.combine(
                            draw_date,
                            datetime.strptime("23:00", "%H:%M").time()
                        )
                    )
                    
                    # Create match for betting
                    driver = CollectAPIDriver(lottery_type.vhost, logger)
                    match = driver.create_lottery_match(draw)
                    
                    results["created_matches"].append({
                        "lottery": lottery_type.name,
                        "draw_date": str(draw_date),
                        "match_id": match.id
                    })
                    
                    logger.info(f"Created match for {lottery_type.name} on {draw_date}")
                    
        except Exception as e:
            logger.error(f"Error creating matches for {lottery_type.name}: {e}")
            results["errors"].append(f"{lottery_type.name}: {str(e)}")
    
    return results
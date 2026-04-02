import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from kombu.abstract import Object

from ..models import LotteryGame

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = Path(__file__).parent.parent / 'config' / 'games'


def load_game_config(config_path: str) -> Dict:
    """
    Load a single game configuration from a YAML file.

    Args:
        config_path: Path to the YAML config file

    Returns:
        Dict with game configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Validate required fields
    required_fields = ['state', 'name', 'slug', 'url', 'format', 'schedule', 'selectors']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field '{field}' in {config_path}")

    return config


def load_all_configs(config_dir: Optional[str] = None) -> List[Dict]:
    """
    Load all game configurations from the config directory.

    Args:
        config_dir: Optional path to config directory. Uses default if not specified.

    Returns:
        List of game configuration dicts
    """
    if config_dir:
        config_path = Path(config_dir)
    else:
        config_path = CONFIG_DIR

    if not config_path.exists():
        logger.warning(f"Config directory does not exist: {config_path}")
        return []

    configs = []
    for yaml_file in config_path.glob('*.yaml'):
        try:
            config = load_game_config(str(yaml_file))
            configs.append(config)
            logger.info(f"Loaded config: {yaml_file.name}")
        except Exception as e:
            logger.error(f"Error loading config {yaml_file}: {e}")

    # Also check .yml extension
    for yml_file in config_path.glob('*.yml'):
        try:
            config = load_game_config(str(yml_file))
            configs.append(config)
            logger.info(f"Loaded config: {yml_file.name}")
        except Exception as e:
            logger.error(f"Error loading config {yml_file}: {e}")

    return configs


def sync_games_from_configs(config_dir: Optional[str] = None, dry_run: bool = False, vhost: object = None) -> Dict:
    """
    Sync LotteryGame records from YAML config files.
    Creates new games and updates existing ones.

    Args:
        config_dir: Optional path to config directory
        dry_run: If True, don't save changes to database

    Returns:
        Dict with counts: {'created': N, 'updated': N, 'errors': N}
    """
    configs = load_all_configs(config_dir)

    results = {'created': 0, 'updated': 0, 'errors': 0, 'games': []}

    for config in configs:
        try:
            game_data = _config_to_game_data(config)

            if dry_run:
                logger.info(f"[DRY RUN] Would sync game: {game_data['slug']}")
                results['games'].append(game_data)
                continue

            game, created = LotteryGame.objects.update_or_create(
                vhost_id=vhost.uuid if vhost else None,
                slug=game_data['slug'],
                defaults=game_data
            )

            if created:
                results['created'] += 1
                logger.info(f"Created game: {game.name}")
            else:
                results['updated'] += 1
                logger.info(f"Updated game: {game.name}")

            results['games'].append(game)

        except Exception as e:
            results['errors'] += 1
            logger.error(f"Error syncing game config: {e}")

    return results


def _config_to_game_data(config: Dict) -> Dict:
    """
    Convert a YAML config dict to LotteryGame field data.

    Args:
        config: YAML config dict

    Returns:
        Dict suitable for LotteryGame.objects.create() or update_or_create()
    """
    format_config = config.get('format', {})
    main_range = format_config.get('main_range', [1, 99])
    bonus_range = format_config.get('bonus_range', [])

    return {
        'state': config['state'].upper(),
        'name': config['name'],
        'slug': config['slug'],
        'url': config['url'],
        'game_type': config.get('game_type', 'pool'),
        'main_count': format_config.get('main_count', 6),
        'main_range_min': main_range[0] if main_range else 1,
        'main_range_max': main_range[1] if len(main_range) > 1 else 99,
        'bonus_count': format_config.get('bonus_count', 0),
        'bonus_range_min': bonus_range[0] if bonus_range else None,
        'bonus_range_max': bonus_range[1] if bonus_range and len(bonus_range) > 1 else None,
        'is_positional': format_config.get('is_positional', False),
        'schedule': config.get('schedule', {}),
        'selectors': config.get('selectors', {}),
        'parser_config': config.get('parser', {}),
        'active': config.get('active', True),
    }


def get_config_template() -> str:
    """Return a template YAML config for reference."""
    return '''# Lottery Game Configuration Template
state: NY
name: "New York Lotto"
slug: ny-lotto
url: "https://nylottery.ny.gov/draw-game?game=lotto"
game_type: pool  # pool, positional, or bonus

format:
  main_count: 6
  main_range: [1, 59]
  bonus_count: 1
  bonus_range: [1, 59]
  is_positional: false

schedule:
  days: [wednesday, saturday]
  times:
    - time: "20:15"
      label: null  # or "midday", "evening" for multi-draw games
  timezone: "America/New_York"

selectors:
  winning_numbers: ".winning-numbers .ball"
  bonus_number: ".bonus-ball"
  draw_date: ".draw-date"
  draw_number: ".draw-number"

parser:
  number_extractor: "text_content"  # or "attribute:data-value"
  date_format: "%A, %B %d, %Y"

active: true
'''

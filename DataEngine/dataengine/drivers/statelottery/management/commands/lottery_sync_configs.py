import logging

from django.core.management.base import BaseCommand

from dataengine.drivers.statelottery.driver.config_loader import (
    sync_games_from_configs,
    get_config_template,
    load_all_configs,
)
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Sync lottery games from YAML config files'

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs="+")

        parser.add_argument(
            '-d', '--config-dir',
            type=str,
            help='Path to config directory (default: uses built-in config/games/)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all config files found'
        )
        parser.add_argument(
            '--template',
            action='store_true',
            help='Print a template YAML config'
        )

    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        config_dir = options.get('config_dir')
        dry_run = options['dry_run']
        list_only = options['list']
        show_template = options['template']

        logging.basicConfig(level=logging.INFO)

        if show_template:
            self.stdout.write("Template YAML config:")
            self.stdout.write("-" * 40)
            self.stdout.write(get_config_template())
            return

        if list_only:
            configs = load_all_configs(config_dir)
            self.stdout.write(f"Found {len(configs)} config file(s):")
            for config in configs:
                self.stdout.write(f"  - {config.get('slug')}: {config.get('name')} ({config.get('state')})")
            return

        self.stdout.write("Syncing games from config files...")
        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN - no changes will be made]"))
        self.stdout.write("")

        results = sync_games_from_configs(config_dir, dry_run=dry_run,vhost=vHost)

        self.stdout.write("")
        self.stdout.write("Results:")
        self.stdout.write(f"  Created: {results['created']}")
        self.stdout.write(f"  Updated: {results['updated']}")
        self.stdout.write(f"  Errors: {results['errors']}")

        if results['games']:
            self.stdout.write("")
            self.stdout.write("Games:")
            for game in results['games']:
                if dry_run:
                    self.stdout.write(f"  - {game['slug']}: {game['name']}")
                else:
                    self.stdout.write(f"  - {game.slug}: {game.name}")

        if results['errors'] > 0:
            self.stdout.write(self.style.ERROR("\nSome configs failed to sync. Check logs for details."))
        else:
            self.stdout.write(self.style.SUCCESS("\nSync completed successfully!"))

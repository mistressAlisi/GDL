from django.core.management.base import BaseCommand
import asyncio, json, websockets, uuid
from game.gdlgdlcore.utils.colorize  import colorize, reset_progress
from parameters.models import VHost


class Command(BaseCommand):
    help = 'Test GDL GPU async daemon with sample params'

    def add_arguments(self, parser):
        parser.add_argument("vhost", type=str, nargs="+")
        parser.add_argument('--no-stream', action='store_true', help='Buffer results and print at the end')
        parser.add_argument('--uri', type=str, default='ws://localhost:8765', help='Daemon websocket URI')

    async def _run_test(self, vhost, stream=True, uri='ws://localhost:8765'):
        req_id = str(uuid.uuid4())
        settings = {
            'vhost': str(vhost.uuid),
            'min_payout': 5000,
            'depth': 5,
            'stake': 2,
            'count': 20,
            'serialise': True,
            'neg_limit': -200,
            'juice': 0.05,
            'events_within': 36 * 3600,

        }
        reset_progress(settings['count'])

        async with websockets.connect(uri) as ws:
            await ws.send(json.dumps({
                'action': 'generate',
                'request_id': req_id,
                'filters': {},
                'settings': settings,
            }))

            buffer = []
            async for raw in ws:
                msg = json.loads(raw)
                if msg.get('request_id') != req_id:
                    continue

                if stream:
                    self.stdout.write('>> ' + colorize(msg))
                else:
                    buffer.append(msg)

                if msg.get('type') in ('complete', 'error'):
                    break

            if not stream:
                self.stdout.write(json.dumps(buffer, indent=2))

    def handle(self, *args, **options):
        vHost = VHost.objects.get(pk=options["vhost"][0])
        asyncio.run(self._run_test(vhost=vHost,stream=not options['no_stream'], uri=options.get('uri')))

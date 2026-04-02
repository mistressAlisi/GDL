from wager.models import Wager


def close_nodes(wager):
    if "nodes" in wager.bet_data:
        for nuuid in wager.bet_data["nodes"]:
            try:
                wchi = Wager.objects.get(uuid=nuuid)
                wchi.executed = True
                wchi.closed = True
                wchi.save()
            except Wager.DoesNotExist:
                pass
    return True
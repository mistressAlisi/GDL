from datetime import timedelta
from django.utils.timezone import now
from game.gdlfront.models import GDLTicketCartCache


def _store_ticket(ticket, vhost, vdomain, account):
    """
    Shared ORM persistence helper for tickets.
    Accepts either POST-style data or GPU-streamed ticket dicts.
    """

    # Normalize fields from ticket dict
    matches = ticket.get("matches") or ticket.get("muuids", [])
    types = ticket.get("types") or ticket.get("outcomes", [])
    lines = ticket.get("lines", [])
    outcome_meta = ticket.get("outcome_meta", [])
    stake = int(ticket.get("stake") or ticket.get("total_stake", 0))
    returns = int(ticket.get("returns") or ticket.get("total_returns", 0))
    depth = int(ticket.get("mlen") or ticket.get("depth") or len(matches))
    uuid_val = ticket.get("uuid")

    ticketData = {
        "matches": matches,
        "mlen": depth,
        "types": types,
        "returns": returns,
        "stake": stake,
        "lines": lines,
        "outcome_meta": outcome_meta,
        "status": "C",
    }

    selected_expires_at = now() + timedelta(minutes=45)

    obj = GDLTicketCartCache(
        vhost=vhost,
        domain=vdomain,          # <-- NEW: persist domain
        account=account,
        risk=stake,
        returns=returns,
        events=depth,
        expires_at=selected_expires_at,
        selected_expires_at=selected_expires_at,
        selected=True,
        ticket_data=ticketData,
    )
    obj.save()
    return obj

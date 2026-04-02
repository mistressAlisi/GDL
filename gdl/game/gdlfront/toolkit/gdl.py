from datetime import timedelta

from django.utils.timezone import now

from game.gdlcore.engine import GDLEngine
from game.gdlfront.models import GDLTicketCartCache
from toolkit.encoders import encode_json_for_html


def gdl_get_tickets_caller(vhost,vdomain,request,account,sports,teams,gdl_settings,**kwargs):
    gdlengine = GDLEngine(vhost, vdomain, sports, teams, gdl_settings)

    GDLTicketCartCache.objects.filter(vhost=vhost, domain=vdomain, account=account, selected=False,
                                      expires_at__lte=now()).delete()
    GDLTicketCartCache.objects.filter(vhost=vhost, domain=vdomain, account=account, selected=True,
                                      selected_expires_at__lte=now()).delete()
    res = gdlengine.get_gdl_tickets(count=gdl_settings["count"]),
    # print(type(res))
    # print(res)

    tickets = []
    for r in res[0]:
        # print("-*****-")
        # print(r)
        #
        # print("-*****-")
        ticketData = {
            # "id":random.randint(1000,10000),
            "matches": r["odds"],
            "mlen": len(r["odds"]),
            "type": r["odds_types"],
            "sports": r["odds_sports"],
            "returns": float(r["total_returns"]),
            "stake": int(gdl_settings["stake"]),
            "match_data": ",".join(r["odds_muuids"]),
            "types": ",".join(r["odds_types"]),
            "lines": ",".join(r["odds_lines"]),
            "status": "C"

        }
        ticket_full_data = {
            "ticketData": ticketData,
            "payload": {"matches": r["odds_muuids"], "types": r["odds_types"], "stake": int(request.POST["stake"]),"lines": r["odds_lines"],
                        "returns": float(r["total_returns"])}
        }
        if "ticket_selected" in kwargs:
            selected = True
            selected_expires_at = now()+timedelta(minutes=45)
        else:
            selected = False
            selected_expires_at = now() + timedelta(minutes=30)
        ticketCacheObj = GDLTicketCartCache(vhost=vhost, domain=vdomain, account=account, risk=gdl_settings["stake"],
                                            returns=ticketData["returns"], events=gdl_settings["depth"],
                                            expires_at=now() + timedelta(minutes=10),
                                            selected_expires_at=selected_expires_at,selected=selected,
                                            ticket_data=ticket_full_data)
        ticketCacheObj.save()
        compressed_data = encode_json_for_html(
            {"matches": r["odds_muuids"], "types": r["odds_types"], "stake": ticketData["stake"],
             "returns": ticketData["returns"]})
        ticketData["payload"] = compressed_data
        ticketData["uuid"] = ticketCacheObj.uuid
        tickets.append(ticketData)

    return tickets
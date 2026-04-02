import requests
import random
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from applications.sportslottonet import library
from sportslottovip.library.datamap import SPORTS
from django.shortcuts import render


from django.http import JsonResponse


def how_to_play(request):
    context = {}
    return render(request, 'sportslottovip/how_to_play/index.html', context)


def about_us(request):
    context = {}
    return render(request, 'sportslottovip/about_us/index.html', context)


def terms_conditions(request):
    context = {}
    return render(request, 'sportslottovip/terms_conditions/index.html', context)


def faq(request):
    context = {}
    return render(request, 'sportslottovip/faq/index.html', context)

def glossary(request):
    context = {}
    return render(request, 'sportslottovip/glossary/index.html', context)

def responsible_gaming(request):
    context = {}
    return render(request, 'sportslottovip/responsible_gaming/index.html', context)
def privacy(request):
    context = {}
    return render(request, 'sportslottovip/privacy/index.html', context)
def differences(request):
    context = {}
    return render(request, 'sportslottovip/differences/index.html', context)
def what_is_sportslotto(request):
    context = {}
    return render(request, 'sportslottovip/what_is_sportslotto/index.html', context)
def how_to_win(request):
    context = {}
    return render(request, 'sportslottovip/how_to_win/index.html', context)
def consolation_payout_table(request):
    context = {}
    return render(request, 'sportslottovip/consolation_payout_table/index.html', context)


def refer_a_friend(request):
    context = {}
    return render(request, 'sportslottovip/refer_a_friend/index.html', context)
def register(request):
    context = {}
    return render(request, 'sportslottovip/register/index.html', context)

def login_widget(request):
    theme = request.GET.get('theme', 'dark')
    url = f'https://play.sportslotto.vip/widgets/account/login/?theme={theme}'
    try:
        r = requests.get(url)   # <-- use requests.get
        r.raise_for_status()
        return HttpResponse(r.text)
    except requests.RequestException as e:
        return HttpResponse(f"<p>Error loading login widget: {e}</p>")
def login_widget_proxy(request):
    theme = request.GET.get('theme', 'dark')
    url = f"https://play.sportslotto.vip/widgets/account/login/?theme={theme}"
    r = requests.get(url)
    return HttpResponse(r.text)





def build_hero_rows(blocked_sizes=None, blocked_uuids=None, blocked_logos=None, grey_sizes=None):
    """
    Pick 8 unique teams (4 top, 4 bottom).
    Use abbreviation as fallback only for blocked/grey logos.

    grey_sizes: list of logo sizes that are known to be dull/grey
    """
    blocked_sizes = blocked_sizes or []
    blocked_uuids = blocked_uuids or []
    blocked_logos = blocked_logos or []
    grey_sizes = grey_sizes or []

    sport = random.choice(list(SPORTS.keys()))
    teams = SPORTS[sport]["teams"]

    # Filter valid teams
    valid_teams = [
        t for t in teams
        if t.card_logo
           and t.card_logo.size not in blocked_sizes
           and t.uuid not in blocked_uuids
    ]

    if len(valid_teams) < 8:
        raise ValueError(f"Not enough valid teams for sport {sport}")

    random.shuffle(valid_teams)

    def team_data(t):
        # Treat grey logos as "blocked"
        is_grey = t.card_logo.size in grey_sizes or t.card_logo.url in blocked_logos
        logo_url = None if is_grey else t.card_logo.url
        return {
            "name": t.name,
            "abbr": "".join([word[0] for word in t.name.split()]).upper(),
            "color": t.team_colour_primary,
            "logo": logo_url
        }

    top_teams_data = [team_data(t) for t in valid_teams[:4]]
    bottom_teams_data = [team_data(t) for t in valid_teams[4:8]]

    result = {"sport": sport, "top": top_teams_data, "bottom": bottom_teams_data}
    return result


def build_bg_balls(count=20):
    """
    Generate properties for flowing background balls
    """
    bg_balls = []
    for _ in range(count):
        bg_balls.append({
            "left": f"{random.randint(0,90)}%",
            "delay": f"{random.uniform(0,5):.2f}s",
            "size": f"{random.randint(20,40)}px",
            "color": "rgba(255,255,255,0.1)",
        })
    return bg_balls

def index(request):
    """
    Render the hero section with initial hero balls and background balls
    """
    # vhost, vdomain, apperance, context = default_dashboard_context(request, "player")
    context = {}
    context.update({
        "hero_rows": build_hero_rows(),
        "bg_balls": build_bg_balls(),
    })
    # print("Context: ", context)
    return render(request, "sportslottovip/home/index.html", context)

def hero_rows_json(request):
    """
    Return new hero rows as JSON for JS redraw
    """
    return JsonResponse(build_hero_rows())

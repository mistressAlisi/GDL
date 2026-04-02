from .american_football import APISportsAmericanFootballAsync
from .baseball import APISportsBaseballAsync
from .basketball import APISportsBasketballAsync
from .football import APISportsFootballAsync
from .hockey import APISportsHockeyAsync

APISPORTS_DAEMONS = {
    "APISportsAMFd":APISportsAmericanFootballAsync,
    "APISportsBased":APISportsBaseballAsync,
    "APISportsBasketd":APISportsBasketballAsync,
    "APISportsFootballd":APISportsFootballAsync,
    "APISportsHockeyd":APISportsHockeyAsync
}

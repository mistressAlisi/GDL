from django.db.models import OuterRef, Exists

from teams.models import TeamSport, Team

# NFL Teams → Official Colors
nfl_teams = {
    "ARI": "#A71930", "ATL": "#A5ACAF", "BAL": "#241773", "BUF": "#00338D",
    "CAR": "#0085CA", "CHI": "#0B162A", "CIN": "#FB4F14", "CLE": "#311D00",
    "DAL": "#003594", "DEN": "#FB4F14", "DET": "#0076B6", "GB": "#203731",
    "HOU": "#03202F", "IND": "#002C5F", "JAX": "#006778", "KC": "#E31837",
    "LAC": "#002A5C", "LAR": "#003594", "MIA": "#008E97", "MIN": "#4F2683",
    "NE": "#002244", "NO": "#D3BC8D", "NYG": "#0B2265", "NYJ": "#125740",
    "PHI": "#004C54", "PIT": "#FFB612", "SF": "#AA0000", "SEA": "#69BE28",
    "TB": "#D50A0A", "TEN": "#4B92DB", "WAS": "#773141",
}

# NBA Teams → Official Colors (example)
nba_teams = {
    "ATL": "#E13A3E", "BOS": "#007A33", "BRK": "#000000", "CHA": "#1D1160",
    "CHI": "#CE1141", "CLE": "#860038", "DAL": "#00538C", "DEN": "#0E2240",
    "DET": "#C8102E", "GSW": "#1D428A", "HOU": "#CE1141", "IND": "#002D62",
    "LAC": "#C8102E", "LAL": "#552583", "MEM": "#5D76A9", "MIA": "#98002E",
    "MIL": "#00471B", "MIN": "#0C2340", "NO": "#85714D", "NYK": "#F58426",
    "OKC": "#007AC1", "ORL": "#0077C0", "PHI": "#006BB6", "PHX": "#E56020",
    "POR": "#E03A3E", "SAC": "#5A2D81", "SAS": "#C4CED4", "TOR": "#CE1141",
    "UTA": "#002B5C", "WAS": "#002B5C",
}
mlb_minor_teams = {
    f"MiLB{i}": f"#{"%06x" % (i*123456 % 0xFFFFFF)}" for i in range(1, 31)
}

wnba_teams = {
    "MIN": "#0C2340", "NY": "#F58426", "LA": "#552583", "SEA": "#69BE28",
    "PHO": "#E56020", "IND": "#002D62", "ATL": "#E13A3E", "CHI": "#CE1141",
    "CON": "#007A33", "DAL": "#00538C", "LV": "#B4975A", "WAS": "#002B5C",
    "MIA": "#98002E", "HOU": "#CE1141", "SAC": "#5A2D81", "BOS": "#007A33"
}
# NHL and MLB similar dictionaries
nhl_teams = {
    "BOS": "#FFB81C", "BUF": "#003087", "CGY": "#C8102E", "CAR": "#007A33",
    "CHI": "#CF0A2C", "COL": "#6F263D", "CBJ": "#002654", "DAL": "#006847",
    "DET": "#CE1126", "EDM": "#041E42", "FLA": "#041E42", "LA": "#111111",
    "MIN": "#154734", "MTL": "#AF1E2D", "NSH": "#FFB81C", "NJ": "#CE1126",
    "NYI": "#00539B", "NYR": "#0038A8", "OTT": "#E31937", "PHI": "#000000",
    "PIT": "#FCB514", "SEA": "#00B2A9", "STL": "#002F87", "TBL": "#002868",
    "TOR": "#00205B", "VAN": "#00205B", "VGK": "#B4975A", "WSH": "#FC0202",
}
mlb_teams = {
    "ARI": "#A71930", "ATL": "#13274F", "BAL": "#241773", "BOS": "#BD3039",
    "CHC": "#0E3386", "CWS": "#27251F", "CIN": "#C6011F", "CLE": "#311D00",
    "COL": "#33006F", "DET": "#0076B6", "HOU": "#002D62", "KC": "#E31837",
    "LAA": "#BA0021", "LAD": "#005A9C", "MIA": "#00A3E0", "MIL": "#12284B",
    "MIN": "#002B5C", "NYM": "#002D72", "NYY": "#1C2841", "OAK": "#003831",
    "PHI": "#E81828", "PIT": "#FDB827", "SD": "#2C2A29", "SEA": "#005C5C",
    "SF": "#FD5A1E", "STL": "#0C2340", "TB": "#092C5C", "TEX": "#003278",
    "TOR": "#134A8E", "WAS": "#AB0003",
}
fifa_teams = {
    "BRA": "#FFCC00", "ARG": "#75AADB", "FRA": "#0055A4", "GER": "#000000",
    "ESP": "#AA151B", "ENG": "#FFFFFF", "ITA": "#0A6EB4", "NED": "#FF6100",
    "POR": "#006C35", "BEL": "#ED2939", "CRO": "#F40000", "URU": "#75AADB",
    "COL": "#FFD700", "SUI": "#FF0000", "DEN": "#C60C30", "SWE": "#FFCD00",
    "MEX": "#006847", "JPN": "#BC002D", "KOR": "#003478", "AUS": "#FFCC33",
    "USA": "#B22234", "CAN": "#FF0000", "NGA": "#008751", "CMR": "#007A33",
    "ARG_F": "#75AADB", "BRA_F": "#FFCC00", "ENG_F": "#FFFFFF", "FRA_F": "#0055A4",
    "GER_F": "#000000", "NED_F": "#FF6100", "ITA_F": "#0A6EB4", "ESP_F": "#AA151B",
}
fifa_w_teams = {
    "USA": "#B22234",   # United States
    "BRA": "#009C3B",   # Brazil
    "GER": "#000000",   # Germany
    "FRA": "#0055A4",   # France
    "ENG": "#FFFFFF",   # England
    "JPN": "#BC002D",   # Japan
    "CAN": "#FF0000",   # Canada
    "SWE": "#FFCC00",   # Sweden
    "NOR": "#EF2B2D",   # Norway
    "NED": "#FF6600",   # Netherlands
    "AUS": "#FFCD00",   # Australia
    "CHN": "#DE2910",   # China
    "ESP": "#AA151B",   # Spain
    "ITA": "#008C45",   # Italy
    "DEN": "#C60C30",   # Denmark
    "COL": "#FFD700",   # Colombia
    "NZL": "#000000",   # New Zealand
    "KOR": "#003478",   # South Korea
    "ARG": "#75AADB",   # Argentina
    "MEX": "#00933B",   # Mexico
    "THA": "#0B4C8C",   # Thailand
    "NGA": "#008751",   # Nigeria
    "RSA": "#007749",   # South Africa
    "IRL": "#009B48",   # Ireland
    "PHI": "#0038A8",   # Philippines
    "CHL": "#D52B1E",   # Chile
}
nwsl_teams = {
    "ANGC": "#010101",  # Angel City FC black / pink Sol Rosa accent
    "BAY": "#051C2C",   # Bay FC dark blue
    "CHIR": "#000080",  # Chicago Red Stars navy
    "HOU": "#03202F",   # Houston Dash navy
    "KC": "#E03A3E",    # Kansas City Current red
    "ORL": "#0077C0",   # Orlando Pride purple/blue
    "PORT": "#E03A3E",  # Portland Thorns red
    "SEA": "#00B2A9",   # OL Reign teal
    "WAS": "#773141",   # Washington Spirit maroon/violet
    "RSL": "#002B5C",   # Utah Royals navy (historic)
    "NC": "#007A33",    # North Carolina Courage green (primary)
}
epl_teams = {
    "ARS": "#EF0107", "AVL": "#95BFE5", "BHA": "#0057B8", "BUR": "#6C1D45",
    "CHE": "#034694", "CRY": "#1B458F", "EVE": "#003399", "FUL": "#DA291C",
    "LIV": "#C8102E", "LEI": "#003090", "LEED": "#FFCD00", "MCI": "#6CABDD",
    "MUN": "#DA291C", "NEW": "#241F20", "NFO": "#DD0000", "SOU": "#D71920",
    "TOT": "#132257", "WHU": "#7A263A", "WOL": "#FDB913", "BOU": "#DA291C",
    "BRE": "#009739", "BHA": "#0057B8", "NCL": "#241F20", "SHE": "#EE2737",
    "STK": "#E03A3E", "WAT": "#FBE122", "WBA": "#1F5C99", "WLV": "#FDB913",
    "NOR": "#EF3340", "CAR": "#0085CA"
}
laliga_teams = {
    "RMA": "#FEBE10", "FCB": "#004D98", "ATM": "#D50A0A", "SEV": "#F20000",
    "VAL": "#E06A1D", "VIL": "#FDB813", "SOC": "#0085CA", "ATH": "#003366",
    "BET": "#2C2A29", "CEL": "#0085CA", "ESP": "#FF0000", "LEV": "#00A3E0",
    "GET": "#0052A5", "EIB": "#E31B23", "OSAS": "#005CA9", "ALM": "#D71920",
    "CAD": "#005CA9", "MAL": "#FFCD00", "GRN": "#006400", "CAV": "#FF0000",
    "RAY": "#E03A3E", "HUE": "#ED1C24", "LEG": "#004E98", "RCD": "#004D98",
    "SDH": "#1B458F", "VALF": "#E06A1D", "SEVF": "#F20000", "ATM_F": "#D50A0A",
    "FCB_F": "#004D98", "RMA_F": "#FEBE10"
}
ncaaf_teams = {
    "ALA": "#9E1B32", "CLEM": "#F66733", "FSU": "#782F40", "MICH": "#00274C",
    "OSU": "#BB0000", "ND": "#0C2340", "TX": "#BF0A30", "OU": "#841617",
    "UCLA": "#2774AE", "USC": "#990000", "LSU": "#461D7C", "BAMA": "#9E1B32",
    "Oregon": "#154733", "Georgia": "#BA0C2F", "Florida": "#FA4616",
    "Penn": "#011F5B", "TexasTech": "#CC0000", "Miami": "#F47321",
    "Wisconsin": "#C5050C", "Washington": "#4B2E83", "Iowa": "#000000",
    "MichiganState": "#18453B", "Nebraska": "#E41B17", "Tennessee": "#FF8200",
    "OklahomaState": "#FF6F00", "UCF": "#000000", "Cincinnati": "#E00122",
    "BoiseState": "#ED8B00", "Utah": "#CC0000", "Minnesota": "#7A0019"
}

af_subq = TeamSport.objects.filter(
            team=OuterRef("pk")
        ).filter(
            sport__group__slug="AF"
        )
bab_subq = TeamSport.objects.filter(
            team=OuterRef("pk")
        ).filter(
            sport__group__slug="BK"
        )
hock_subq = TeamSport.objects.filter(
            team=OuterRef("pk")
        ).filter(
            sport__group__slug="IH"
        )
bas_subq = TeamSport.objects.filter(
            team=OuterRef("pk")
        ).filter(
            sport__group__slug="BB"
        )
soc_subq = TeamSport.objects.filter(
            team=OuterRef("pk")
        ).filter(
            sport__group__slug="SC"
        )
teams_with_logos = Team.objects.filter(card_logo__isnull=False)
SPORTS = {
    "nfl": {
        "icon": "icon-football",
        "teams": list(teams_with_logos.annotate(nfl_exists=Exists(af_subq)).filter(nfl_exists=True).all())
    },
    "nba": {
        "icon": "icon-basketball",
        "teams": list(teams_with_logos.annotate(nfl_exists=Exists(bab_subq)).filter(nfl_exists=True).all())
    },
    "wnba": {
        "icon": "icon-basketball",
        "teams": list(teams_with_logos.annotate(nfl_exists=Exists(bab_subq)).filter(nfl_exists=True).all())
    },
    "nhl": {
        "icon": "icon-hockey",
        "teams": list(teams_with_logos.annotate(nfl_exists=Exists(hock_subq)).filter(nfl_exists=True).all())
    },
    "mlb": {
        "icon": "icon-baseball",
        "teams": list(teams_with_logos.annotate(nfl_exists=Exists(bas_subq)).filter(nfl_exists=True).all())
    },
    "fifa": {
        "icon": "icon-soccer",
        "teams": list(teams_with_logos.annotate(nfl_exists=Exists(soc_subq)).filter(nfl_exists=True).all())
    },
}
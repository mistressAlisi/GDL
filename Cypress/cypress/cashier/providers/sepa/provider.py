"""
ionBlock Payment Provider Configuration
Cryptocurrency payment gateway supporting deposits and withdrawals
"""

PAYMENT_PROVIDER_INFO = {
    "name": "sepa",
    "description": "Direct Euro Currency XFER via Banks",
    "is_fiat": True,
    "is_crypto": False,
    "icon_class": "fa-solid fa-cube",
    "ordering_key": 3,
    "deposits": False,
    "dep_min": 0.001,  # Minimum deposit in crypto
    "dep_max": 100,    # Maximum deposit in crypto
    "dep_fees": 0,     # No additional fees (ionBlock handles conversion)
    "withdrawals": True,
    "wdl_min": 0.001,  # Minimum withdrawal in crypto
    "wdl_max": 50,     # Maximum withdrawal in crypto
    "wdl_fees": 0      # No additional fees
}

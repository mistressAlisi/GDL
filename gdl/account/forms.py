from django.forms import ModelForm, HiddenInput, TextInput
from django.forms import ModelForm, HiddenInput, TextInput

from .models import Account


class AccountForm(ModelForm):
    # id = CharField(widget=HiddenInput())
    # name = CharField(label="Agent/User Name", help_text="Must be unique!")
    # first_name = CharField(label="First Name", help_text="Optional",required=False)
    # last_name = CharField(label="Last Name", help_text="Optional",required=False)
    # email = EmailField(label="Agent Email Address",help_text="Required to create the new account")
    # password = CharField(widget=PasswordInput(), label="Password",help_text="Set the Agent's new Password",required=False)
    # password2 = CharField(widget=PasswordInput(), label="Password Confirmation", help_text="Confirm the Agent's new Password",required=False)
    # is_active = BooleanField(label="Agent Active",help_text="Global Enable/Disable flag",initial=True)
    class Meta:
        model = Account
        fields = ["uuid","acctnum","holder","email1","email2","account_level","low_balance_alert","min_wager","wager_limit","settle",
                 "must_change_pw","use_rolling_balance",
                  "can_use_sportsbook","can_place_wagers","can_place_phone_wagers","active","frozen","settle"]
        widgets = {
            # "available": HiddenInput(),
            # "current":HiddenInput(),
            # "at_risk": HiddenInput(),
            # "free_play": HiddenInput(),
            "uuid":HiddenInput(),
            "settle": TextInput(),
            "holder": TextInput(),
            "must_change_pw":HiddenInput(),
        }



class AccountEditForm(ModelForm):
    # id = CharField(widget=HiddenInput())
    # name = CharField(label="Agent/User Name", help_text="Must be unique!")
    # first_name = CharField(label="First Name", help_text="Optional",required=False)
    # last_name = CharField(label="Last Name", help_text="Optional",required=False)
    # email = EmailField(label="Agent Email Address",help_text="Required to create the new account")
    # password = CharField(widget=PasswordInput(), label="Password",help_text="Set the Agent's new Password",required=False)
    # password2 = CharField(widget=PasswordInput(), label="Password Confirmation", help_text="Confirm the Agent's new Password",required=False)
    # is_active = BooleanField(label="Agent Active",help_text="Global Enable/Disable flag",initial=True)
    class Meta:
        model = Account
        fields = ["uuid","acctnum","holder","email1","email2","low_balance_alert","min_wager","wager_limit","settle","mobile",
                  "use_rolling_balance"]
        widgets = {
            # "available": HiddenInput(),
            # "current": HiddenInput(),
            # "at_risk": HiddenInput(),
            # "free_play": HiddenInput(),
            "acctnum": HiddenInput(),
            "uuid":HiddenInput(),
            "mobile": TextInput(),
            "holder": TextInput(),

        }
class AccountSelfEditForm(ModelForm):
    # id = CharField(widget=HiddenInput())
    # name = CharField(label="Agent/User Name", help_text="Must be unique!")
    # first_name = CharField(label="First Name", help_text="Optional",required=False)
    # last_name = CharField(label="Last Name", help_text="Optional",required=False)
    # email = EmailField(label="Agent Email Address",help_text="Required to create the new account")
    # password = CharField(widget=PasswordInput(), label="Password",help_text="Set the Agent's new Password",required=False)
    # password2 = CharField(widget=PasswordInput(), label="Password Confirmation", help_text="Confirm the Agent's new Password",required=False)
    # is_active = BooleanField(label="Agent Active",help_text="Global Enable/Disable flag",initial=True)
    class Meta:
        model = Account
        fields = ["uuid","acctname","holder","email1","email2","mobile","locale","system_theme","timezone","pronouns"]
        widgets = {
            "acctnum": HiddenInput(),
            "uuid":HiddenInput(),
            "mobile": TextInput(),
            "holder": TextInput(),
            "acctname": TextInput(),

        }




class TimeZoneForm(ModelForm):
    class Meta:
        model = Account
        fields = ["uuid","timezone","locale"]
        widgets = {
            "uuid":HiddenInput(),
        }
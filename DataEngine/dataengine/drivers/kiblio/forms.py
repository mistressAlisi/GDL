from django.forms import ModelForm, TextInput, HiddenInput, Form, BooleanField

from parameters.models import AgentParameters
from providers.theodds.models.base_models import MatchOddsAPISettings, OddsRegion


class TheOddsForm(ModelForm):
    class Meta:
        model = MatchOddsAPISettings
        fields = ["uuid","api_key_str","update_frequency","requests_remaining"]
        widgets = {
            "requests_remaining": TextInput({"disabled":True}),
            "uuid":HiddenInput()

        }


class OddsRegionForm(ModelForm):
    class Meta:
        model = OddsRegion
        fields = ["uuid","key","name","active"]
        widgets = {
            "uuid":HiddenInput()
        }


class AgentParametersForm(ModelForm):
    class Meta:
        model = AgentParameters
        fields = ["uuid","ping_offline_threshold","new_account_free_play","max_open_bet_limit","low_balance_alert","enable_phone_bets"]
        widgets = {
            "uuid":HiddenInput()
        }

class OddsExecutionForm(Form):
    sync_get_sports = BooleanField(label="Sync Sports/Leagues",help_text="Synchronise all The Odds regions and get all sports and leagues entries.",initial=False,required=False)
    sync_get_h2h = BooleanField(label="Sync Head to Head Lines",help_text="Synchronise and Summarise all Head to head odds for all events.",initial=False,required=False)
    sync_get_totals = BooleanField(label="Sync Total Score Lines",help_text="Synchronise all Total lines for all events.",initial=False,required=False)
    sync_get_scores = BooleanField(label="Sync Scores",help_text="Synchronise all Scores",initial=False,required=False)

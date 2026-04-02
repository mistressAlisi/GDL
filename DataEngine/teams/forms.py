from django import forms
from django.forms import HiddenInput, TextInput, ModelChoiceField, CharField

# from providers.apisports.models import Team as APITeam
# from providers.theodds.models import Team as OddsTeam
from teams.models import Team, AccountTeamFavourite


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = "__all__"
        widgets = {
            "uuid":HiddenInput(),
            "name":TextInput(),

        }


class AccountTeamFavouriteForm(forms.ModelForm):
    class Meta:
        model = AccountTeamFavourite
        fields = "__all__"
        widgets = {
            "uuid":HiddenInput(),
            "account":HiddenInput(),
        }


class TeamMapEditForm(forms.Form):
    tuuid = CharField(widget=HiddenInput())
    # apisports_team = ModelChoiceField(label="API Sports Team:",queryset=APITeam.objects.all(),required=True,to_field_name="uuid")
    # theodds_team = ModelChoiceField(label="The Odds Team:",queryset=OddsTeam.objects.all(),required=True,to_field_name="uuid")

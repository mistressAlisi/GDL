from django import forms
from django.forms import HiddenInput, TextInput, Select, CheckboxInput, NumberInput

from matches.models import Match


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = "__all__"
        widgets = {
            "uuid":HiddenInput(),
            "name":TextInput(),
            "apiid": TextInput({"readonly": "readonly", "help_text": "For Reference ONLY, do NOT modify."}),
            "id": TextInput({"readonly": "readonly","help_text":"For Reference ONLY, do NOT modify."}),
            "final_score": TextInput({"readonly": "readonly"}),
            "scoring_data": TextInput({"readonly": "readonly"}),
            "winner": Select({"disabled": True}),
            "draw":CheckboxInput({"disabled": True}),
            "status_short":TextInput(),
            "status_long": TextInput(),
            "stage":TextInput(),
            "week": NumberInput(),
            "city":TextInput(),
            "venue":TextInput(),
            "status_timer":TextInput({"readonly": "readonly"}),
            "commence_time":TextInput({"readonly": "readonly"})
        }

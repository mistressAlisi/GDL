from django.forms import HiddenInput, ModelForm, TextInput

from sports.models import Group, Sport


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = "__all__"
        widgets = {
            "uuid": HiddenInput()
        }


class SportForm(ModelForm):
    class Meta:
        model = Sport
        fields = "__all__"
        widgets = {
            "uuid": HiddenInput(),
            "key":TextInput(),
            "title":TextInput(),
            "description":TextInput(),
        }
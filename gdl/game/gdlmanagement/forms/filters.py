from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django.forms import ModelForm, HiddenInput

from game.gdlgdlcore.models import GDLCoreSportGroupFilters
from game.gdlfront.models import GDLFilterSettingsGroup


class GDLCoreSportFilterForm(ModelForm):
    class Meta:
        model = GDLCoreSportGroupFilters
        fields = ['uuid','vhost','domain','group_filter','sport_filter']
        widgets = {
            "uuid": HiddenInput(),
            "domain":HiddenInput(),
            "vhost": HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Div(
                Div(Field("group_filter"), css_class="col row"),
                css_class="row"
            ),

            Div(
                Div(Field("sport_filter"), css_class="col row"),
                css_class="row"
            ),
            Field("uuid"),
            Field("vhost"),
            Field("domain"),
            HTML('<button type="submit" class="btn btn-primary w-100 pt-2 pb-2">Set Filters</button>')
        )


class GDLFilterSettingsForm(ModelForm):
    class Meta:
        model = GDLFilterSettingsGroup
        fields = ['uuid','vhost','domain','name','group_filter','sport_filter']
        widgets = {
            "uuid": HiddenInput(),
            "domain":HiddenInput(),
            "vhost": HiddenInput(),
            "name":HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Div(
                Div(Field("group_filter"), css_class="col row"),
                css_class="row"
            ),

            Div(
                Div(Field("sport_filter"), css_class="col row"),
                css_class="row"
            ),
            Field("uuid"),
            Field("vhost"),
            Field("domain"),
            Field("name"),
            HTML('<button type="submit" class="btn btn-primary w-100 pt-2 pb-2">Set Filter Settings</button>')
        )

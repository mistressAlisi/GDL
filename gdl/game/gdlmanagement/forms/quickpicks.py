from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django.forms import ModelForm, HiddenInput, TextInput, NumberInput

from game.gdlgdlcore.models import GDLTypeSettingsEntry


class GDLTypeSettingsEntryForm(ModelForm):
    class Meta:
        model = GDLTypeSettingsEntry
        fields = ['uuid','vhost','domain','name','icon','class_name','group_filter','sport_filter','order_by','active']
        widgets = {
            "uuid": HiddenInput(),
            "domain":HiddenInput(),
            "vhost": HiddenInput(),
            "name":TextInput(),
            "icon":TextInput(),
            "class_name":TextInput(),
            "order_by":NumberInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'row'

        self.helper.layout = Layout(
            Div(
                Div(Field("name"), css_class="col row"),
                Div(Field("icon"), css_class="col row"),
                Div(Field("class_name"), css_class="col row"),

                Div(
                    Div(Field("group_filter"), css_class="col row"),
                    css_class="row"
                ),
                Div(
                    Div(Field("sport_filter"), css_class="col row"),
                    css_class="row"
                ),
                Div(
                    Div(Field("order_by"), css_class="col row"),
                    Div(Field("active"), css_class="col row"),
                    css_class="row"
                ),
                Field("uuid"),
                Field("vhost"),
                Field("domain"),
                HTML(
                    '<div class="card-footer"><div class="d-flex justify-content-end"><div class="p-2"><input type="reset" class="btn btn-primary" value="Reset Form"/></div><div class="p-2"><input type="submit" class="btn btn-success" value="Save Changes"/></div></div></div>')
            )

        )

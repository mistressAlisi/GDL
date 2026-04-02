from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django.forms import Form, IntegerField, HiddenInput, ChoiceField
from django.forms.models import ModelForm
from django.utils.translation import gettext_lazy as _
from django import forms

from cashier.models import AccountLossesLimits

BUTTON_SET_LIMITS_STR = _("Set Limits")






class AccountLossesLimitsForm(ModelForm):
    class Meta:
        model = AccountLossesLimits
        fields = ['uuid','vhost','account','daily_limit',
                  'weekly_limit','monthly_limit',
                  'active'
                  ]
        widgets = {
            "uuid": HiddenInput(),
            "vhost": HiddenInput(),
            "account": HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Div(
                Div(Field("daily_limit"), css_class="col row"),

                css_class="row"
            ),

            Div(
                Div(Field("weekly_limit"), css_class="col row"),

                css_class="row"
            ),

            Div(
                Div(Field("monthly_limit"), css_class="col row"),

                css_class="row"
            ),
            Div(
                Div(Field("active"), css_class="col row"),
                css_class="row"
            ),
            Field("uuid"),
            Field("vhost"),
            Field("account"),
            HTML("""<button type="submit" class="btn btn-primary w-100 pt-2 pb-2">{set_limit_str}</button>""".format(set_limit_str=BUTTON_SET_LIMITS_STR))
        )

class SepaWithdrawForm(forms.Form):
    legalname = forms.CharField(
        label=_("Full Legal Name on Bank Account"),
        max_length=255
    )
    iban = forms.CharField(
        label=_("IBAN Number"),
        max_length=34
    )
    amount = forms.DecimalField(
        label=_("Withdraw Amount"),
        min_value=1,
        max_value=1000,
        decimal_places=2
    )
    acct_passwd = forms.CharField(
        label=_("Account Password"),
        widget=forms.PasswordInput
    )

    def clean_iban(self):
        iban = self.cleaned_data["iban"].replace(" ", "").upper()
        if len(iban) < 15:
            raise forms.ValidationError(_("Invalid IBAN format."))
        return iban
from django.forms import ModelForm, HiddenInput, TextInput

from .models import ApperanceParameters, AccountParameters, LedgerParameters


class ApperanceForm(ModelForm):
    class Meta:
        model = ApperanceParameters
        fields = ["site_name", "site_domain", "site_icon", "site_font_awesome","site_tagline","site_currency","uuid","vhost","show_featured","show_favourites","show_all_sports","show_events_today",
                  "show_scores","landing_page", "menu_entries",]
        widgets = {
            "uuid": HiddenInput(),
            "site_name": TextInput(),
            "site_font_awesome": TextInput(),
            "site_domain": TextInput(),
            "site_tagline": TextInput(),
            "site_currency": TextInput(),
            "vhost": HiddenInput()
        }


class AccountForm(ModelForm):
    class Meta:
        model = AccountParameters
        fields = ["enable_new_acct_free_play","initial_credit","new_account_free_play","min_wager","max_wager","account_perf_warning_threshold","account_perf_alarm_threshold","uuid"]
        widgets = {
            "uuid": HiddenInput(),

        }



class LedgersForm(ModelForm):
    class Meta:
        model = LedgerParameters
        fields = "__all__"
        widgets = {
            "uuid": HiddenInput(),

        }


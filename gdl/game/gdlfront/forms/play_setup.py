from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field
from django.forms import Form, CharField, ChoiceField, RadioSelect, HiddenInput
from django.forms.fields import IntegerField
from django.forms.widgets import NumberInput
from django.utils.translation import gettext_lazy as _

GENERATE_TICKETS_STR = _("Generate Tickets!")
GET_TICKETS_STR = _("Get Tickets!")
FILTERS_STR = _("Filters")
VIEW_CART_STR = _("View Cart")

class SetupGDL_BasicForm1(Form):
    bet_amnt = IntegerField(label=_("Bet Amount:"),help_text=_("Amount to risk per placed ticket"),required=True,initial=1,min_value=1,max_value=1000)
    num_games = IntegerField(label=_("Ticket Legs:"), help_text=_("How many games/events to include per ticket"), required=True,initial=5,min_value=1,max_value=20)
    win_amnt = IntegerField(label=_("Win Amount:"), help_text=_("How much would you like to win"), required=True,initial=2500,min_value=100,max_value=100000)
    num_tickets = IntegerField(label=_("Ticket Count:"), help_text=_("How many ticket options would you like?"), required=True,initial=25,min_value=5,max_value=50)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Div(
                Div(FloatingField("bet_amnt"), css_class="col"),
                css_class="row"
            ),
            Div(
                Div(FloatingField("num_games"), css_class="col"),
                css_class="row"
            ),
            Div(
                Div(FloatingField("win_amnt"), css_class="col"),
                css_class="row"
            ),
            Div(
            Div(FloatingField("num_tickets"), css_class="col"),
            css_class="row"
            ),
            HTML("""<button type="submit" class="btn btn-primary w-90 p-2 m-2">{generate}</button>""".format(generate=GENERATE_TICKETS_STR)),
        )



class SetupGDL_FullForm(Form):
    stake = IntegerField(label=_("Risk:"),required=True,initial=1,min_value=1,max_value=1000)
    depth = IntegerField(label=_("Events:"), required=True,initial=5,min_value=1,max_value=20)
    min_payout = IntegerField(label=_("Win:"), required=True,initial=2500,min_value=10,max_value=100000)
    count = IntegerField(required=True,initial=15,widget=HiddenInput)
    event_cutoff = ChoiceField(
        choices=((36, _("36 Hours")),(24, _("24 Hours")),(12, _("12 Hours")),(6,_("6 Hours")),(3,_("3 Hours")),),
        label=_("Time Frame:"),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stake"].widget.attrs["max_value"] = 5
        self.helper = FormHelper()
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Div(
                Div(Field("stake"), css_class="col row"),
                Div(Field("depth"), css_class="col row"),
                css_class="row"
            ),

            Div(
                Div(Field("min_payout"), css_class="col row"),
                Div(Field("event_cutoff"), css_class="col row"),
                css_class="row"
            ),

            Field("count"),
            HTML("""<button type="submit" class="btn btn-primary w-100 pt-2 mt-4 pb-2">{get_tickets}</button>""".format(get_tickets=GET_TICKETS_STR)),
        )

class SetupGDL_FilteredForm(Form):
    stake = IntegerField(label=_("Risk:"),required=True,initial=1,min_value=1,max_value=1000,widget=NumberInput(attrs={"data-bs-toggle":"tooltip","data-bs-title":_("How much to risk per ticket? 1 up to 1,000."),"data-bs-placement":"bottom"}))
    depth = IntegerField(label=_("Events:"), required=True,initial=5,min_value=1,max_value=20,widget=NumberInput(attrs={"data-bs-toggle":"tooltip","data-bs-title":_("How many events to include in your ticket? 1 to 20."),"data-bs-placement":"bottom"}))
    min_payout = IntegerField(label=_("Win:"), required=True,initial=2500,min_value=10,max_value=100000,widget=NumberInput(attrs={"data-bs-toggle":"tooltip","data-bs-title":_("Enter the desired win amount! Up to 100,000!"),"data-bs-placement":"bottom"}))
    count = IntegerField(required=True,initial=15,widget=HiddenInput)
    event_cutoff = CharField(initial=36,widget=HiddenInput,required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stake"].widget.attrs["max_value"] = 5
        self.helper = FormHelper()
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Div(
                Div(Field("stake"), css_class="col row"),
                Div(Field("depth"), css_class="col row"),
                css_class="row"
            ),

            Div(
                Div(Field("min_payout"), css_class="col row"),
                # Div(HTML(
                #     '<button type="button" id="quick_pick_btn" class="btn btn-primary mt-4"><span class="d-none d-lg-inline"><i class="fa-duotone fa-solid fa-stars pe-1"></i></span>Quick Picks</button>'),
                #     css_class="col-3 pt-3"),
                Div(HTML("""<button type="button" id="custom_switch_btn" class="btn btn-success mt-4"><span class="d-none d-lg-inline"><i class="fa-duotone fa-solid fa-magnifying-glass pe-1"></i></span>{filters}</button>""".format(filters=FILTERS_STR)), css_class="col-12 col-md-3 pt-3"),
                css_class="row"
            ),
            # Field('event_cutoff'),
            Field("count"),
            Div(
                Div(HTML("""<button type="submit" class="btn btn-primary w-100 pt-2 pb-2 mt-4">{get_tickets}</button>""".format(get_tickets=GET_TICKETS_STR)), css_class="col row"),
                Div(HTML("""<button type="button" id="gdl_buy_now_alt" class="btn btn-primary w-100 pt-2 pb-2 mt-4">{cart}</button>""".format(cart=VIEW_CART_STR)), css_class="col row"),
                css_class="row"
            ),
        )




class SetupGDL_AdvInlineForm(Form):
    stake = IntegerField(label=_("Risk:"),required=True,initial=1,min_value=1,max_value=1000,widget=NumberInput(attrs={"data-bs-toggle":"tooltip","data-bs-title":_("How much to risk per ticket? $1 up to $1,000."),"data-bs-placement":"bottom"}))
    depth = IntegerField(label=_("Events:"), required=True,initial=5,min_value=1,max_value=20,widget=NumberInput(attrs={"data-bs-toggle":"tooltip","data-bs-title":_("How many events to include in your ticket? 1 to 20."),"data-bs-placement":"bottom"}))
    min_payout = IntegerField(label=_("Win:"), required=True,initial=2500,min_value=10,max_value=100000,widget=NumberInput(attrs={"data-bs-toggle":"tooltip","data-bs-title":_("Enter the desired win amount! Up to $100,000!"),"data-bs-placement":"bottom"}))
    count = IntegerField(required=True,initial=15,widget=HiddenInput)
    event_cutoff = ChoiceField(
        choices=((36, _("36 Hours")),(24, _("24 Hours")),(12, _("12 Hours")),(6,_("6 Hours")),(3,_("3 Hours")),),
        label="Time Frame:",
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["stake"].widget.attrs["max_value"] = 5
        self.helper = FormHelper()
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Div(
                Div(Field("stake"), css_class="col row"),
                Div(Field("depth"), css_class="col row"),
                Div(Field("min_payout"), css_class="col row"),
                Div(Field("event_cutoff"), css_class="col row"),

                css_class="row"
            ),
            Field("count")
        )

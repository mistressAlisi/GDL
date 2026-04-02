from django.urls import path
# from frontend.mycashier import views
urlpatterns = [
    path('health_check', views.health_check),
    path("balance", views.my_balance, name="my_balance"),
    path("deposit",views.landing_dep, name="deposit_landing"),
    path("deposit/modal",views.deposit_modal, name="deposit_modal"),
    path("deposit/start/<str:provider>", views.deposit_start, name="deposit_start"),
    path("promos",views.my_promos, name="my_promos"),
    path("promos/historic",views.my_past_promos,name="my_past_promos"),

    path("withdraw", views.landing_withd, name="withdrawal_landing"),
    path("withdraw/start/<str:provider>", views.withdrawal_start, name="withdrawal_start"),
    path("withdraw/validate", views.withdrawal_validate, name="withdrawal_validate"),

    path("limits/applications",views.application_limits, name="application_limits"),
    path("limits/applications/modal/<uuid:auuid>",views.application_limit_form,name="application_limit_form"),
    path("limits/losses", views.losses_limits, name="losses_limits"),
    path("limits/losses/modal/", views.losses_limit_form, name="losses_limit_form"),
    path("lockout/", views.account_lockout, name="losses_limits"),
    # OLD STUFF:
    path("buy_tokens", views.buy_tokens, name="buy_tokens"),
    path("completed", views.completed_transactions, name="completed_transactions"),
    path("pending", views.pending_transactions, name="pending_transactions"),
    path("exchange", views.exchange_tokens_step1, name="cashier_exchange"),
    path("exchange/step2", views.exchange_tokens_step2, name="cashier_exchange_step2"),
    path("exchange/step3", views.exchange_tokens_step3, name="cashier_exchange_step3"),
    path("exchange/approve/<str:confirm_key>", views.exchange_tokens_confirm, name="exchange_tokens_confirm"),
    path("exchange/resend/<uuid:tuuid>", views.exchange_tokens_resend, name="exchange_tokens_confirm"),
    path("landing", views.landing_dep, name="cashier_landing"),
    path("claim-bonus/", views.claim_bonus, name="claim_bonus"),
    path("read-message/", views.mark_message_read, name="read_message"),
    path('ionblock/status/<int:channel_id>', views.ionblock_status, name='ionblock_status'),
    path("sepa-transfer", views.sepa_request_page, name="sepa_request_page"),
]
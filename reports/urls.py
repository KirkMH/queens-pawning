from django.urls import path
from . import views


urlpatterns = [
    path('expenses/<str:type>/report',
         views.expense_report, name='expense_report'),

    path('pawns/nonrenewal',
         views.nonrenewal_report, name='nonrenewal_report'),
    path('pawns/<int:pk>/hold/<int:status>',
         views.set_onhold, name='set_onhold'),
    path('pawn/new', views.new_pawn_tickets, name='new_pawn_report'),

    path('daily-cash-position',
         views.daily_cash_position, name='daily_cash_position'),
    path('daily-cash-position/<int:pk>/receipts/add',
         views.ReceiptCreateView.as_view(), name='add_receipt'),
    path('daily-cash-position/<int:pk>/disbursement/add',
         views.DisbursementCreateView.as_view(), name='add_disbursement'),
    path('daily-cash-position/<int:pk>/cib-breakdown',
         views.update_cib_brakedown, name='update_cib_brakedown'),
    path('receipt/<int:pk>/delete',
         views.delete_receipt, name='delete_receipt'),
    path('disbursement/<int:pk>/delete',
         views.delete_disbursement, name='delete_disbursement'),

    path('cash-count', views.cash_count, name='cash_count'),
    # pk -> CashCount.pk
    path('cash-count/<int:pk>/add',
         views.OtherCashCountCreateView.as_view(), name='add_cash_count'),
    # pk -> OtherCashCount.pk
    path('other-cash-count/<int:pk>/remove',
         views.remove_other_cash_count, name='remove_other_cash_count'),

    path('auction/branch', views.auction_report, name='auction_report'),
    path('auction/branch/go', views.auction_now, name='auction_now'),

    path('income-statement', views.income_statement, name='income_statement'),
]

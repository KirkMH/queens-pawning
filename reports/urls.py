from django.urls import path
from . import views


urlpatterns = [
    path('expenses/<str:type>/report',
         views.expense_report, name='expense_report'),

    path('pawns/nonrenewal',
         views.nonrenewal_report, name='nonrenewal_report'),
    path('pawns/<int:pk>/hold/<int:status>',
         views.set_onhold, name='set_onhold'),

    path('daily-cash-position',
         views.daily_cash_position, name='daily_cash_position'),
    path('daily-cash-position/<int:pk>/receipts/add',
         views.ReceiptCreateView.as_view(), name='add_receipt'),
    path('daily-cash-position/<int:pk>/disbursement/add',
         views.DisbursementCreateView.as_view(), name='add_disbursement'),
    path('daily-cash-position/<int:pk>/cib-breakdown',
         views.update_cib_brakedown, name='update_cib_brakedown'),

    path('cash-count', views.cash_count, name='cash_count'),
    path('cash-count/<int:pk>/add',
         views.OtherCashCountCreateView.as_view(), name='add_cash_count'),
]

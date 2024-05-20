from django.urls import path
from . import views


urlpatterns = [
    path('expenses/<str:type>/report',
         views.expense_report, name='expense_report'),
    path('pawns/nonrenewal',
         views.nonrenewal_report, name='nonrenewal_report'),

    path('daily-cash-position',
         views.daily_cash_position, name='daily_cash_position'),
    path('daily-cash-position/<int:pk>/receipts/add',
         views.ReceiptCreateView.as_view(), name='add_receipt'),
    path('daily-cash-position/<int:pk>/disbursement/add',
         views.DisbursementCreateView.as_view(), name='add_disbursement'),

]

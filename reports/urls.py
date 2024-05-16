from django.urls import path
from . import views


urlpatterns = [
    path('expenses/<str:type>/report',
         views.expense_report, name='expense_report'),
    path('pawns/nonrenewal',
         views.nonrenewal_report, name='nonrenewal_report'),
]

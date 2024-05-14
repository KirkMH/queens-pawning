from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('dt', views.ExpenseDTListView.as_view(), name='expense_dtlist'),
]

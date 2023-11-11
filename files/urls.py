from django.urls import path
from . import views


urlpatterns = [
    path('client', views.client_list, name='client_list'),
    path('client/dt', views.ClientDTListView.as_view(), name='client_dtlist'),
    path('client/new', views.ClientCreateView.as_view(), name='new_client'),
    path('client/<int:pk>/edit',
         views.ClientUpdateView.as_view(), name='edit_client'),


    path('expense/category', views.expense_category_list,
         name='expense_category_list'),
    path('expense/category/dt', views.ExpenseCategoryDTListView.as_view(),
         name='expense_category_dtlist'),
    path('expense/category/new', views.ExpenseCategoryCreateView.as_view(),
         name='new_expense_category'),
    path('expense/category/<int:pk>/edit',
         views.ExpenseCategoryUpdateView.as_view(), name='edit_expense_category'),
]

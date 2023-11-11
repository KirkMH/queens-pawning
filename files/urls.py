from django.urls import path
from . import views


urlpatterns = [
    path('clients', views.client_list, name='client_list'),
    path('clients/dt', views.ClientDTListView.as_view(), name='client_dtlist'),
    path('clients/new', views.ClientCreateView.as_view(), name='new_client'),
    path('clients/<int:pk>/edit',
         views.ClientUpdateView.as_view(), name='edit_client'),


    path('expenses/categories', views.expense_category_list,
         name='expense_category_list'),
    path('expenses/categories/dt', views.ExpenseCategoryDTListView.as_view(),
         name='expense_category_dtlist'),
    path('expenses/categories/new', views.ExpenseCategoryCreateView.as_view(),
         name='new_expense_category'),
    path('expenses/categories/<int:pk>/edit',
         views.ExpenseCategoryUpdateView.as_view(), name='edit_expense_category'),
]

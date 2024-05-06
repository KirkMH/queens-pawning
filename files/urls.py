from django.urls import path
from . import views


urlpatterns = [
    path('clients', views.client_list, name='client_list'),
    path('clients/dt', views.ClientDTListView.as_view(), name='client_dtlist'),
    path('clients/new', views.ClientCreateView.as_view(), name='new_client'),
    path('clients/<int:pk>/edit',
         views.ClientUpdateView.as_view(), name='edit_client'),
    path('clients/<int:pk>/detail',
         views.ClientDetailView.as_view(), name='client_detail'),

    path('expenses/categories', views.expense_category_list,
         name='expense_category_list'),
    path('expenses/categories/dt', views.ExpenseCategoryDTListView.as_view(),
         name='expense_category_dtlist'),
    path('expenses/categories/new', views.ExpenseCategoryCreateView.as_view(),
         name='new_expense_category'),
    path('expenses/categories/<int:pk>/edit',
         views.ExpenseCategoryUpdateView.as_view(), name='edit_expense_category'),

    path('branches', views.branch_list,
         name='branch_list'),
    path('branches/dt', views.BranchDTListView.as_view(),
         name='branch_dtlist'),
    path('branches/new', views.BranchCreateView.as_view(),
         name='new_branch'),
    path('branches/<int:pk>/edit',
         views.BranchUpdateView.as_view(), name='edit_branch'),

    path('other-fees', views.other_fees,
         name='other_fees'),
    path('term-duration', views.term_duration,
         name='term_duration'),
    # type is either 'int' (interest rate) or 'adv' (advance interest rate)
    path('interest-rates/<str:type>', views.interest_rate,
         name='interest_rates'),
]

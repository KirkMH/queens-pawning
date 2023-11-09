from django.urls import path
from . import views


urlpatterns = [
    path('client', views.client_list, name='client_list'),
    path('client/dt', views.ClientDTListView.as_view(), name='client_dtlist'),
    path('client/new', views.ClientCreateView.as_view(), name='new_client'),
    path('client/<int:pk>/edit',
         views.ClientUpdateView.as_view(), name='edit_client'),
]

from django.urls import path
from . import views


urlpatterns = [
    path('expenses/itemized', views.itemized_expenses, name='itemized_expenses'),
]

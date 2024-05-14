from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import *


@login_required
def expense_list(request):
    return render(request, 'expense/expense_list.html')


@method_decorator(login_required, name='dispatch')
class ExpenseDTListView(ServerSideDatatableView):
    queryset = Expense.objects.all()
    columns = ['pk', 'branch', 'category', 'description',
               'amount', 'date', 'encoded_by', 'encoded_on']

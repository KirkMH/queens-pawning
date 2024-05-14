from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import *
from .forms import *


@login_required
def expense_list(request):
    return render(request, 'expense/expense_list.html')


@method_decorator(login_required, name='dispatch')
class ExpenseDTListView(ServerSideDatatableView):
    queryset = Expense.objects.all()
    columns = ['pk', 'branch__name', 'category__category', 'description',
               'amount', 'date', 'encoded_by__user__first_name', 'encoded_by__user__last_name', 'encoded_on']


@method_decorator(login_required, name='dispatch')
class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense/expense_form.html'

    def post(self, request, *args, **kwargs):
        form = ExpenseForm(request.POST)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.encoded_by = Employee.objects.get(user=request.user)
            saved.save()
            messages.success(request, f"New expense was created successfully.")
            if "another" in request.POST:
                return redirect('new_expense')
            else:
                return redirect('expense_list')

        else:
            return render(request, 'expense/expense_form.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ExpenseUpdateView(SuccessMessageMixin, UpdateView):
    model = Expense
    context_object_name = 'expense'
    form_class = ExpenseForm
    template_name = "expense/expense_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('expense_list')
    success_message = "The expense information was updated successfully."

    def post(self, request, *args, **kwargs):
        object = self.get_object()
        if "delete" in request.POST:
            object.delete()
            messages.success(request, f"Expense was deleted successfully.")
            return redirect('expense_list')
        else:
            return super().post(request, *args, **kwargs)

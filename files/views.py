from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from decimal import Decimal

from .models import *
from .forms import *


###############################################################################################
#                Client Maintenance
###############################################################################################

def client_list(request):
    return render(request, 'files/client_list.html')


class ClientDTListView(ServerSideDatatableView):
    queryset = Client.objects.all()
    columns = ['pk', 'title', 'last_name', 'first_name', 'middle_name', 'address',
               'id_presented', 'id_number', 'contact_num', 'date_registered', 'status']


class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'files/client_form.html'

    def post(self, request, *args, **kwargs):
        form = ClientForm(request.POST)
        if form.is_valid():
            saved = form.save()
            saved.save()
            messages.success(request, f"{saved} was created successfully.")
            if "another" in request.POST:
                return redirect('new_client')
            else:
                return redirect('client_list')

        else:
            return render(request, 'files/client_form.html', {'form': form})


class ClientUpdateView(SuccessMessageMixin, UpdateView):
    model = Client
    context_object_name = 'client'
    form_class = ClientForm
    template_name = "files/client_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('client_list')
    success_message = "The client's record was updated successfully."


class ClientDetailView(DetailView):
    model = Client
    template_name = "files/client_detail.html"
    context_object_name = 'client'


###############################################################################################
#                Expense Category Maintenance
###############################################################################################

def expense_category_list(request):
    return render(request, 'files/expense_category_list.html')


class ExpenseCategoryDTListView(ServerSideDatatableView):
    queryset = ExpenseCategory.objects.all()
    columns = ['pk', 'category', 'status']


class ExpenseCategoryCreateView(CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = 'files/expense_category_form.html'

    def post(self, request, *args, **kwargs):
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            saved = form.save()
            saved.save()
            messages.success(request, f"{saved} was created successfully.")
            if "another" in request.POST:
                return redirect('new_expense_category')
            else:
                return redirect('expense_category_list')

        else:
            return render(request, 'files/expense_category_form.html', {'form': form})


class ExpenseCategoryUpdateView(SuccessMessageMixin, UpdateView):
    model = ExpenseCategory
    context_object_name = 'category'
    form_class = ExpenseCategoryForm
    template_name = "files/expense_category_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('expense_category_list')
    success_message = "The expense category was updated successfully."


###############################################################################################
#                Branch Maintenance
###############################################################################################

def branch_list(request):
    return render(request, 'files/branch_list.html')


class BranchDTListView(ServerSideDatatableView):
    queryset = Branch.objects.all()
    columns = ['pk', 'name', 'address', 'vat_info',
               'contact_num', 'days_open', 'status']


class BranchCreateView(CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'files/branch_form.html'

    def post(self, request, *args, **kwargs):
        form = BranchForm(request.POST)
        if form.is_valid():
            saved = form.save()
            saved.save()
            messages.success(request, f"{saved} was created successfully.")
            if "another" in request.POST:
                return redirect('new_branch')
            else:
                return redirect('branch_list')

        else:
            return render(request, 'files/branch_form.html', {'form': form})


class BranchUpdateView(SuccessMessageMixin, UpdateView):
    model = Branch
    context_object_name = 'branch'
    form_class = BranchForm
    template_name = "files/branch_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('branch_list')
    success_message = "The branch information was updated successfully."


###############################################################################################
#                Other Fees
###############################################################################################

def other_fees(request):
    other_fees = OtherFees.get_instance()
    # check if post
    if request.method == 'POST':
        # get the form data
        fee_type = request.POST.get('fee_type')
        value = request.POST.get('fee_value')

        # check if the values are valid
        if value:
            # update the values
            if fee_type == 'service_fee':
                other_fees.service_fee = Decimal(value)
            else:
                other_fees.advance_interest_rate = int(value)
            other_fees.save()

            # return to other fees page with success message
            messages.success(request, "Other fees were updated successfully.")

    context = {
        'service_fee': other_fees.service_fee,
        'advance_interest': other_fees.advance_interest_rate
    }
    return render(request, 'files/other_fees.html', context)

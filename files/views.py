from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from decimal import Decimal

from .models import *
from .forms import *
from access_hub.models import Employee


###############################################################################################
#                Client Maintenance
###############################################################################################
@login_required
def client_list(request):
    return render(request, 'files/client_list.html')


@method_decorator(login_required, name='dispatch')
class ClientDTListView(ServerSideDatatableView):
    queryset = Client.objects.all()
    columns = ['pk', 'title', 'last_name', 'first_name', 'middle_name', 'address',
               'id_presented', 'id_number', 'contact_num', 'date_registered', 'status']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(branch=Employee.objects.get(user=self.request.user).branch)


@method_decorator(login_required, name='dispatch')
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'files/client_form.html'

    def post(self, request, *args, **kwargs):
        form = ClientForm(request.POST)
        if form.is_valid():
            saved = form.save()
            saved.branch = Employee.objects.get(user=request.user).branch
            saved.save()
            messages.success(request, f"{saved} was created successfully.")
            if "another" in request.POST:
                return redirect('new_client')
            else:
                return redirect('client_list')

        else:
            return render(request, 'files/client_form.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ClientUpdateView(SuccessMessageMixin, UpdateView):
    model = Client
    context_object_name = 'client'
    form_class = ClientForm
    template_name = "files/client_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('client_list')
    success_message = "The client's record was updated successfully."


@method_decorator(login_required, name='dispatch')
class ClientDetailView(DetailView):
    model = Client
    template_name = "files/client_detail.html"
    context_object_name = 'client'


###############################################################################################
#                Expense Category Maintenance
###############################################################################################

@login_required
def expense_category_list(request):
    return render(request, 'files/expense_category_list.html')


@method_decorator(login_required, name='dispatch')
class ExpenseCategoryDTListView(ServerSideDatatableView):
    queryset = ExpenseCategory.objects.all()
    columns = ['pk', 'category', 'status']


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
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

@login_required
def branch_list(request):
    return render(request, 'files/branch_list.html')


@method_decorator(login_required, name='dispatch')
class BranchDTListView(ServerSideDatatableView):
    queryset = Branch.objects.all()
    columns = ['pk', 'name', 'address', 'vat_info',
               'contact_num', 'days_open', 'status']


@method_decorator(login_required, name='dispatch')
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


@method_decorator(login_required, name='dispatch')
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

@login_required
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


###############################################################################################
#                Term Duration
###############################################################################################

@login_required
def term_duration(request):
    term_duration = TermDuration.get_instance()
    # check if post
    if request.method == 'POST':
        # get the form data
        type = request.POST.get('type')
        value = request.POST.get('value')

        # check if the values are valid
        if value:
            # update the values
            if type == 'maturity':
                term_duration.maturity = int(value)
            else:
                term_duration.expiration = int(value)
            term_duration.save()

            messages.success(
                request, "Term duration was updated successfully.")

    context = {
        'maturity': term_duration.maturity,
        'expiration': term_duration.expiration
    }
    return render(request, 'files/term_duration.html', context)


###############################################################################################
#                Interest Rates
###############################################################################################

@login_required
def interest_rate(request):
    # check if post
    if request.method == 'POST':
        # get the form data
        min_days = request.POST.getlist('min_days[]')
        rate = request.POST.getlist('rate[]')
        approval_required = request.POST.getlist('approval_required[]')

        if len(min_days) > 0 and (len(min_days) == len(rate) == len(approval_required)):
            print(min_days, rate, approval_required)
            # clear contents of InterestRate model
            InterestRate.objects.all().delete()

            # insert each element
            for i in range(len(min_days)):
                InterestRate.objects.create(
                    min_day=int(min_days[i]),
                    interest_rate=int(rate[i]),
                    approval_required=(approval_required[i] == '1')
                )

            messages.success(
                request, "Interest rates was updated successfully.")

    rates = InterestRate.objects.all()
    context = {
        'interest_rates': rates
    }
    return render(request, 'files/interest_rate.html', context)

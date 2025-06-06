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
from pawn.models import Pawn


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
               'id_link__type', 'id_number', 'contact_num', 'date_registered', 'status', 'branch__name']

    def get_queryset(self):
        qs = super().get_queryset()
        branch = Employee.objects.get(user=self.request.user).branch
        print(f"branch: {branch}")
        if branch:
            qs = qs.filter(branch=branch)
        return qs


@method_decorator(login_required, name='dispatch')
class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'files/client_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the logged-in user to the form
        return kwargs


    def post(self, request, *args, **kwargs):
        form = ClientForm(request.POST, user=request.user)
        if form.is_valid():
            saved = form.save()
            saved.branch = Employee.objects.get(user=request.user).branch
            saved.save()
            messages.success(request, f"{saved} was created successfully.")
            return redirect('client_detail', pk=saved.pk)

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
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the logged-in user to the form
        return kwargs


@method_decorator(login_required, name='dispatch')
class ClientDetailView(DetailView):
    model = Client
    template_name = "files/client_detail.html"
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = Client.objects.get(pk=self.kwargs['pk'])
        context["pawns"] = Pawn.objects.filter(client=client)
        return context


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
        print(f"Fee Type: {fee_type} | Value: {value}")

        # check if the values are valid
        if value:
            # update the values
            if fee_type == 'service_fee':
                other_fees.service_fee = Decimal(value)
            elif fee_type == 'penalty_rate':
                other_fees.penalty_rate = int(value)
            other_fees.save()
            print(f"Other Fees: {other_fees}")

            # return to other fees page with success message
            messages.success(request, "Other fees were updated successfully.")

    context = {
        'service_fee': other_fees.service_fee,
        'penalty_rate': other_fees.penalty_rate
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
def interest_rate(request, type):
    obj = InterestRate if type == 'int' else AdvanceInterestRate
    description = "Interest rate" if type == 'int' else "Advance interest rate"

    # check if post
    if request.method == 'POST':
        # get the form data
        min_days = request.POST.getlist('min_days[]')
        rate = request.POST.getlist('rate[]')

        if len(min_days) > 0 and (len(min_days) == len(rate)):
            print(min_days, rate)
            # clear contents of the model
            obj.objects.all().delete()

            # insert each element
            for i in range(len(min_days)):
                obj.objects.create(
                    min_day=int(min_days[i]),
                    interest_rate=int(rate[i])
                )

            messages.success(
                request, f"{description} was updated successfully.")

    rates = obj.objects.all()
    context = {
        'description': description,
        'interest_rates': rates
    }
    return render(request, 'files/interest_rate.html', context)

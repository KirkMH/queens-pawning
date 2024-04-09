from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from access_hub.models import Employee
from files.models import OtherFees
from .models import *
from .forms import *


###############################################################################################
#                Pawn Transactions
###############################################################################################

@login_required
def pawn_list(request):
    return render(request, 'pawn/pawn_list.html')


@method_decorator(login_required, name='dispatch')
class PawnDTListView(ServerSideDatatableView):
    queryset = Pawn.objects.all()
    columns = ['pk', 'date', 'client', 'quantity', 'carat', 'color', 'item_description', 'description', 'grams',
               'principal', 'service_charge', 'advance_interest', 'net_proceeds', 'status',
               'client__title', 'client__last_name', 'client__first_name', 'client__middle_name']

    def get_queryset(self):
        cur_employee = Employee.objects.filter(user=self.request.user).first()
        if cur_employee:
            branch = cur_employee.branch
            clients = Client.objects.filter(branch=branch)
            return super().get_queryset().filter(client__in=clients)
        else:
            return super().get_queryset()


@method_decorator(login_required, name='dispatch')
class PawnCreateView(CreateView):
    model = Pawn
    template_name = 'pawn/pawn_form.html'
    form_class = PawnForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['otherFees'] = OtherFees.get_instance()
        return context

    def get_form_kwargs(self):
        kwargs = super(PawnCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        form = PawnForm(request.POST, request=request)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.branch = Employee.objects.get(user=request.user).branch
            saved.save()
            messages.success(
                request, f"New pawn ticket for {saved.client} was created successfully.")
            if "another" in request.POST:
                return redirect('new_pawn')
            else:
                return redirect('pawn_detail', pk=saved.pk)

        else:
            return render(request, 'pawn/pawn_form.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class PawnUpdateView(SuccessMessageMixin, UpdateView):
    model = Pawn
    context_object_name = 'pawn'
    form_class = PawnForm
    template_name = "pawn/pawn_form.html"
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('pawn_list')
    success_message = "The Pawn's record was updated successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['otherFees'] = OtherFees.get_instance()
        return context


@method_decorator(login_required, name='dispatch')
class PawnDetailView(DetailView):
    model = Pawn
    template_name = "pawn/pawn_detail.html"
    context_object_name = 'pawn'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['otherFees'] = OtherFees.get_instance()
        return context


@login_required
def pawn_payment(request, pk):
    pawn = Pawn.objects.get(pk=pk)
    print('processing payment for ', pawn)
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('amtToPay'):
            amount_to_pay = float(request.POST.get('amtToPay'))
            pawn.pay(amount_to_pay, Employee.objects.get(user=request.user))
            messages.success(
                request, f"Payment of ₱ {'{:,.2f}'.format(amount_to_pay)} for {pawn.client} was recorded successfully.")
            return redirect('pawn_detail', pk=pk)
        else:
            messages.error(request, "Please fill-in all required fields.")

    return render(request, 'pawn/pawn_detail.html', {'pawn': pawn})


@login_required
def inventory_list(request):
    return render(request, 'pawn/pawn_items.html')


@method_decorator(login_required, name='dispatch')
class PawnedItemsDTListView(ServerSideDatatableView):
    queryset = Pawn.inventory.all()
    columns = ['pk', 'date', 'description', 'principal',
               'client__title', 'client__last_name', 'client__first_name', 'client__middle_name',
               'quantity', 'carat', 'color', 'item_description', 'grams',]

    def get_queryset(self):
        if Employee.objects.filter(user=self.request.user).count() > 0 and Employee.objects.get(user=self.request.user).branch:
            return super().get_queryset().filter(branch=Employee.objects.get(user=self.request.user).branch)
        else:
            return super().get_queryset()


@login_required
def request_discount(request, pk):
    ''' 
    The cashier requests for a discount for the pawn ticket.
    pk -> pawn.pk
    '''
    success = True
    error = None
    try:
        pawn = Pawn.objects.get(pk=pk)
        amount = request.GET['amount']
        interest_due = request.GET['interest_due']
        discount = DiscountRequests.objects.create(
            pawn=pawn, interest_due=interest_due, amount=amount,
            requested_by=Employee.objects.get(user=request.user))
        print(discount)
    except Exception as e:
        print(e)
        success = False
        error = str(e)
    return JsonResponse({'success': success, 'error': error})


@login_required
def cancel_request_discount(request, pk):
    ''' 
    The cashier cancels the discount request. 
    pk -> pawn.pk
    '''
    success = True
    error = None
    try:
        discount = DiscountRequests.objects.get(pawn=Pawn.objects.get(pk=pk))
        discount.cancel()
    except Exception as e:
        print(e)
        success = False
        error = str(e)
    return JsonResponse({'success': success, 'error': error})


@login_required
def request_discount_status(request, pk):
    ''' 
    The frontend repeatedly requests for the status of the discount request until either approved or cancelled. 
    pk -> pawn.pk
    '''
    discount = DiscountRequests.objects.get(pawn=Pawn.objects.get(pk=pk))
    return JsonResponse({'status': discount.status})


@login_required
def approve_discount(request, pk):
    ''' 
    The manager approves the discount request. 
    pk -> discount.pk
    '''
    success = True
    error = None
    try:
        discount = DiscountRequests.objects.get(pk=pk)
        discount.approve(Employee.objects.get(user=request.user))
    except Exception as e:
        print(e)
        success = False
        error = str(e)
    return JsonResponse({'success': success, 'error': error})


@login_required
def reject_discount(request, pk):
    ''' 
    The manager rejects the discount request. 
    pk -> discount.pk
    '''
    success = True
    error = None
    try:
        discount = DiscountRequests.objects.get(pk=pk)
        discount.reject(Employee.objects.get(user=request.user))
    except Exception as e:
        print(e)
        success = False
        error = str(e)
    return JsonResponse({'success': success, 'error': error})


@login_required
def discount_requests(request):
    return render(request, 'pawn/discount_list.html')


@method_decorator(login_required, name='dispatch')
class DiscountRequestsDTListView(ServerSideDatatableView):
    queryset = DiscountRequests.objects.all()
    columns = ['pk', 'date', 'pawn__pk', 'amount', 'status',
               'requested_by__user__last_name', 'requested_by__user__first_name',
               'pawn__principal', 'interest_due']

    def get_queryset(self):
        if Employee.objects.filter(user=self.request.user).count() > 0 and Employee.objects.get(user=self.request.user).branch:
            return super().get_queryset().filter(pawn__branch=Employee.objects.get(user=self.request.user).branch)
        else:
            return super().get_queryset()

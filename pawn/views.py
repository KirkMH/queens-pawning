from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from datetime import datetime

from access_hub.models import Employee
from files.models import OtherFees
from .models import *
from .forms import *


###############################################################################################
#                Pawn Transactions
###############################################################################################

@login_required
def pawn_list(request):
    selected_filter = request.GET.get('filter') or 'All'
    # capitalize first letter
    selected_filter = selected_filter[0].upper() + selected_filter[1:]
    context = {'selected_filter': selected_filter}
    return render(request, 'pawn/pawn_list.html', context)


@method_decorator(login_required, name='dispatch')
class PawnDTListView(ServerSideDatatableView):
    queryset = Pawn.objects.all()
    columns = ['pk', 'date_granted', 'client__contact_num', 'quantity', 'carat', 'color', 'item_description', 'description', 'grams',
               'principal', 'service_charge', 'advance_interest', 'net_proceeds', 'status',
               'client__title', 'client__last_name', 'client__first_name', 'client__middle_name', 'transaction_type', 'branch__name',
               'date_encoded', 'pawn_ticket_number']

    def get_queryset(self):
        print(f'GET: {self.request.GET}')
        qs = super().get_queryset()
        filter = self.request.GET.get('filter') or 'Active'
        if filter == 'active':
            qs = qs.filter(status='ACTIVE')
        elif filter == 'renewed':
            qs = qs.filter(status='RENEWED')
        elif filter == 'redeemed':
            qs = qs.filter(status='REDEEMED')
        elif filter == 'auctioned':
            qs = qs.filter(status='AUCTIONED')

        branch = Employee.objects.get(user=self.request.user).branch
        print(f"branch: {branch}")
        if branch:
            clients = Client.objects.filter(branch=branch)
            return qs.filter(client__in=clients)
        else:
            return qs


@method_decorator(login_required, name='dispatch')
class PawnCreateView(CreateView):
    model = Pawn
    template_name = 'pawn/pawn_form.html'
    form_class = PawnForm

    def get_context_data(self, **kwargs):
        print(f"self.request.GET: {self.request.GET}")
        client_pk = self.request.GET.get('client', None)
        if client_pk:
            client = Client.objects.get(pk=client_pk)
            self.initial['client'] = client
            print(f'client: {client}')
        context = super().get_context_data(**kwargs)
        # context['otherFees'] = OtherFees.get_instance()
        # print(f'context: {context}')
        return context

    def get_form_kwargs(self):
        kwargs = super(PawnCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def post(self, request, *args, **kwargs):
        form = PawnForm(request.POST, request=request)
        if form.is_valid():
            employee = Employee.objects.get(user=request.user)
            pawn = form.save(commit=False)
            pawn.promised_renewal_date = None
            pawn.advance_interest = 0
            pawn.branch = employee.branch
            print(f'employee: {employee}')
            print(f'employee.branch: {employee.branch}')
            pawn.save()
            pawn.update_renew_redeem_date()
            pawn.update_payment(
                employee, pawn.service_charge, pawn.advance_interest)
            pawn.update_cash_position_new_ticket(
                employee, 'New pawn ticket')
            messages.success(
                request, f"New pawn ticket for {pawn.client} was created successfully.")
            return redirect('pawn_detail', pk=pawn.pk)

        else:
            # form['otherFees'] = OtherFees.get_instance()
            return render(request, 'pawn/pawn_form.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class PawnUpdateView(SuccessMessageMixin, UpdateView):
    model = Pawn
    context_object_name = 'pawn'
    form_class = PawnForm
    template_name = "pawn/pawn_form.html"
    pk_url_kwarg = 'pk'
    success_message = "The Pawn's record was updated successfully."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['otherFees'] = OtherFees.get_instance()
        return context
    
    def get_success_url(self):
        pawn = self.get_object()
        employee = Employee.objects.get(user=self.request.user)
        pawn.update_cash_position_new_ticket(
            employee, 'Updated pawn ticket', False)
        return reverse_lazy('pawn_detail', kwargs={'pk': self.kwargs['pk']})


@method_decorator(login_required, name='dispatch')
class PawnDetailView(DetailView):
    model = Pawn
    template_name = "pawn/pawn_detail.html"
    context_object_name = 'pawn'

    def get_context_data(self, **kwargs):
        today = timezone.now().date()
        self.get_object().update_renew_redeem_date(today)
        print('renew_redeem_date: ', self.get_object().renew_redeem_date)
        context = super().get_context_data(**kwargs)
        context['pawn'] = self.get_object()
        context['otherFees'] = OtherFees.get_instance()
        return context


@login_required
def delete_pawn(request, pk):
    pawn = Pawn.objects.get(pk=pk)

    # update the mother ticket, if exists
    mother = pawn.renewed_from()
    print(f'mother: {type(mother)}')
    if mother:
        # delete payment from mother ticket
        payment = Payment.objects.filter(pawn=mother.pk).first()
        payment.delete()
        # reset the status of the mother ticket
        mother.reset_status()

    # delete from receipts of cash position
    pawn.receipts.all().delete()
    # delete from disbursements of cash position
    pawn.disbursements.all().delete()
    # delete this pawn
    pawn.delete()

    messages.success(
        request, f"Pawn ticket for {pawn.client} was successfully deleted.")
    return redirect('pawn_detail', pk=mother.pk)


@login_required
def void_pawn(request, pk):
    pawn = Pawn.objects.get(pk=pk)

    # delete payment from mother ticket
    payment = Payment.objects.filter(pawn=pawn.pk).first()
    payment.delete()

    # reset the status of the ticket
    pawn.reset_status()
    # delete from receipts of cash position
    pawn.receipts.all().delete()
    # delete from disbursements of cash position
    pawn.disbursements.all().delete()

    messages.success(
        request, f"The transaction for this pawn ticket was successfully voided.")
    return redirect('pawn_detail', pk=pawn.pk)


@login_required
def update_renew_redeem_date(request, pk):
    error = None
    status = 'success'
    print("updating...")
    if request.method == 'POST':
        print(request.POST)
        renew_redeem_post = request.POST.get('renew_redeem_date')
        print(f'renew_redeem_post: {renew_redeem_post}')
        try:
            if renew_redeem_post:
                # convert renew_redeem_post to a date
                renew_redeem_date = datetime.strptime(
                    renew_redeem_post, '%Y-%m-%d').date()
                pawn = Pawn.objects.get(pk=pk)
                if renew_redeem_date < pawn.date_granted:
                    status = 'error'
                    error = 'Date should not be less than the grant date.'
                else:
                    pawn.update_renew_redeem_date(renew_redeem_date)
                print(f'Interest: {pawn.getInterest()}')
                print(f'Advance Interest: {pawn.getAdvanceInterest()}')
                print(f'Penalty: {pawn.getPenalty()}')
                print(f'Interest + Penalty: {pawn.getInterestPlusPenalty()}')
        except Exception as e:
            print(e)
            error = str(e)
            status = 'error'

    return JsonResponse({'status': status, 'error': error})


@login_required
def pawn_payment(request, pk):
    pawn = Pawn.objects.get(pk=pk)
    print('processing payment for ', pawn)
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('amtToPay'):
            pawn.pay(request.POST, Employee.objects.get(user=request.user))
            messages.success(
                request, f"Pawn ticket was successfully {pawn.status.lower()}.")
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
    columns = ['pk', 'date_granted', 'description', 'principal',
               'client__title', 'client__last_name', 'client__first_name', 'client__middle_name',
               'quantity', 'carat', 'color', 'item_description', 'grams', 'branch__name']

    def get_queryset(self):
        branch = Employee.objects.get(user=self.request.user).branch
        if branch:
            return super().get_queryset().filter(branch=branch)
        else:
            return super().get_queryset()


@login_required
def redeem_pawn(request, pk):
    context = {
        'pawn': Pawn.objects.get(pk=pk)
    }
    return render(request, 'pawn/pawn_redeem.html', context)


@login_required
def renew_pawn(request, pk):
    context = {
        'pawn': Pawn.objects.get(pk=pk)
    }
    return render(request, 'pawn/pawn_renew.html', context)


@login_required
def print_inventory_list(request):
    queryset = Pawn.inventory.all()
    selected_branch = 'All Branches'
    try:
        branch = Employee.objects.get(user=request.user).branch

        if branch:
            queryset = queryset.filter(branch=branch)
            selected_branch = f"{branch.name} Branch"
    except:
        pass

    context = {
        'list': queryset,
        'selected_branch': selected_branch
    }
    return render(request, 'pawn/pawn_items_print.html', context)


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


@login_required
def calculate_advance_interest(request):
    '''
    Calculate the advance interest of the pawn ticket.
    '''
    success = True
    error = None
    advance_interest = 0
    advance_interest_rate = 0
    # try:
    #     print(f'Calculating advance interest for {request.GET}')
    #     date_granted = datetime.strptime(
    #         request.GET['date_granted'], '%Y-%m-%d').date()
    #     promised_date = datetime.strptime(
    #         request.GET['promised_date'], '%Y-%m-%d').date()
    #     principal = float(request.GET['principal'])
    #     advance_interest_rate = Pawn.advanceInterestRate(
    #         promised_date, date_granted)
    #     advance_interest = principal * (advance_interest_rate / 100)
    # except Exception as e:
    #     print(e)
    #     success = False
    #     error = str(e)
    return JsonResponse({
        'success': success,
        'error': error,
        'advance_interest_rate': advance_interest_rate,
        'advance_interest': advance_interest
    })

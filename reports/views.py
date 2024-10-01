from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from django.http import Http404
from django.views.generic import CreateView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from urllib.parse import urlencode
from decimal import Decimal

from files.models import Branch
from expense.models import Expense
from pawn.models import Pawn, Payment
from access_hub.models import Employee
from .models import DailyCashPosition, AddReceipts, LessDisbursements
from .forms import *


def get_month_name(month, year):
    month_names = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]
    return f"{month_names[month - 1]} {year}"


@login_required
def expense_report(request, type):
    sel_branch = request.GET.get('branch')
    sel_month = request.GET.get('month')
    expenses = None
    expense_list = None
    selected_branch = None
    selected_month = None

    if sel_branch and sel_month:
        sel_branch = int(sel_branch)
        if sel_branch > -1:
            selected_branch = Branch.objects.get(
                pk=sel_branch).name + ' Branch'
            expense_list = Expense.objects.filter(
                branch=sel_branch
            )
        else:
            expense_list = Expense.objects.all()
            selected_branch = 'All Branches'

        sel_month_parts = sel_month.split('-')
        print(f"sel_month_parts: {sel_month_parts}")
        year = int(sel_month_parts[0])
        month = int(sel_month_parts[1])
        selected_month = get_month_name(month, year).upper()
        expense_list = expense_list.filter(
            date__year=year,
            date__month=month
        ).order_by('category__category').order_by('date')
        # create an array of dict of expenses, grouped by category
        expenses = []
        for expense in expense_list:
            if not expenses:
                expenses.append({
                    'category': expense.category.category,
                    'expenses': [expense]
                })
            else:
                found = False
                for exp in expenses:
                    if exp['category'] == expense.category.category:
                        exp['expenses'].append(expense)
                        found = True
                        break
                if not found:
                    expenses.append({
                        'category': expense.category.category,
                        'expenses': [expense]
                    })
    # calculate total per category
    grand_total = 0
    if expenses:
        for exp in expenses:
            total = 0
            for expense in exp['expenses']:
                total += expense.amount
            exp['total'] = total
            grand_total += total
    context = {
        'branches': Branch.objects.all(),
        'expenses': expenses,
        'grand_total': grand_total,
        'sel_branch': sel_branch,
        'sel_month': sel_month,
        'selected_branch': selected_branch,
        'selected_month': selected_month,
        'type': type
    }
    return render(request, 'reports/expense_report.html', context=context)


@login_required
def nonrenewal_report(request):
    sel_branch = url_branch = request.GET.get('branch', None)

    report = None
    grand_total = 0

    if sel_branch:
        report = Pawn.expired.filter(status='ACTIVE')
        sel_branch = int(sel_branch)
        if sel_branch == -1:
            sel_branch = 'All Branches'
        else:
            branch = Branch.objects.get(pk=sel_branch)
            report = report.filter(branch=branch)
            sel_branch = branch.name

        grand_total = report.aggregate(Sum('principal'))['principal__sum']

    context = {
        "branches": Branch.objects.all(),
        "sel_branch": sel_branch,
        "url_branch": url_branch,
        "report": report,
        "grand_total": grand_total
    }

    return render(request, 'reports/non_renewal.html', context)


@login_required
def set_onhold(request, pk, status):
    url_branch = request.GET.get('branch', None)
    pawn = Pawn.objects.get(pk=pk)
    pawn.on_hold = (status > 0)
    pawn.save()

    if pawn.on_hold:
        messages.success(
            request, f"PTN {pawn.pk:05d} is now ON HOLD.")
    else:
        messages.success(
            request, f"Disabled ON HOLD status of PTN {pawn.pk:06d}.")

    base_url = reverse('nonrenewal_report')
    query_string = urlencode({'branch': url_branch})
    url = '{}?{}'.format(base_url, query_string)

    return redirect(url)


@login_required
def daily_cash_position(request):
    employee = Employee.objects.get(user=request.user)
    branch_employee = employee.branch

    date = request.GET.get('date')
    branch = request.GET.get('branch')
    print(f"branch: {branch}")
    is_today = True
    if not date:
        date = timezone.now().date()
    else:
        date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        if date != timezone.now().date():
            is_today = False

    if branch:
        branch = int(branch)
        if branch > -1:
            branch = Branch.objects.get(pk=branch)
        else:
            branch = None
    else:
        branch = branch_employee

    print(f"branch: {branch}")

    daily_cash_position = None
    receipts = None
    disbursements = None
    last = None
    if branch:
        daily_cash_position = DailyCashPosition.objects.filter(
            branch=branch,
            date=date
        )
        if daily_cash_position.count() == 0:
            daily_cash_position = DailyCashPosition.objects.create(
                branch=branch,
                date=date
            )
            daily_cash_position.prepared_by = employee
            daily_cash_position.save()
        else:
            first_position = daily_cash_position.order_by('-id')[0]
            # delete the rest of the positions if they exist
            daily_cash_position.exclude(id=first_position.id).delete()
            daily_cash_position = first_position

        receipts = daily_cash_position.receipts.all()
        disbursements = daily_cash_position.disbursements.all()
        last = daily_cash_position.fill_in_from_yesterday()
    context = {
        'cash_position': daily_cash_position,
        'receipts': receipts,
        'disbursements': disbursements,
        'last': last,
        'sel_date': date,
        'selected_branch': branch,
        'is_today': is_today,
        'branches': Branch.objects.all(),
    }
    return render(request, 'reports/daily_cash_position.html', context)


@method_decorator(login_required, name='dispatch')
class ReceiptCreateView(CreateView):
    model = AddReceipts
    template_name = 'reports/daily_cash_position_form.html'
    form_class = ReceiptForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Receipt'
        return context

    def post(self, request, *args, **kwargs):
        form = ReceiptForm(request.POST)
        if form.is_valid():
            pk = kwargs.get('pk')
            daily_cash_position = DailyCashPosition.objects.get(pk=pk)
            receipt = form.save(commit=False)
            receipt.daily_cash_position = daily_cash_position
            receipt.save()
            messages.success(
                request, f"New receipt was added successfully.")
            if "another" in request.POST:
                return redirect('add_receipt', pk=pk)
            else:
                return redirect('daily_cash_position')


@method_decorator(login_required, name='dispatch')
class DisbursementCreateView(CreateView):
    model = LessDisbursements
    template_name = 'reports/daily_cash_position_form.html'
    form_class = DisbursementForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Disbursement'
        return context

    def post(self, request, *args, **kwargs):
        form = DisbursementForm(request.POST)
        if form.is_valid():
            pk = kwargs.get('pk')
            daily_cash_position = DailyCashPosition.objects.get(pk=pk)
            disbursement = form.save(commit=False)
            disbursement.daily_cash_position = daily_cash_position
            disbursement.save()
            messages.success(
                request, f"New disbursement was added successfully.")
            if "another" in request.POST:
                return redirect('add_disbursement', pk=pk)
            else:
                return redirect('daily_cash_position')


@login_required
def update_cib_brakedown(request, pk):
    if request.method == 'POST':
        print(f"POST: {request.POST}")
        deposits = request.POST.get('deposits_today') or '0'
        withdrawals = request.POST.get('withdrawals_today') or '0'
        daily_cash_position = DailyCashPosition.objects.get(pk=pk)
        daily_cash_position.deposits = float(deposits)
        daily_cash_position.withdrawals = float(withdrawals)
        daily_cash_position.save()
        messages.success(
            request, f"CIB breakdown was updated successfully.")
    return redirect('daily_cash_position')


@login_required
def cash_count(request):
    date = request.GET.get('date')
    is_today = False
    is_updated = False
    if not date:
        date = timezone.now().date()
        is_today = True
    else:
        date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
        print(f"Date: {date}")
        print(f'Today: {timezone.now().date()}')
        if date == timezone.now().date():
            is_today = True
    employee = Employee.objects.get(user=request.user)
    branch = employee.branch
    if not branch:
        raise Http404("This feature is only available to branches.")
    print(f"Branch: {branch}")
    print(f"Date: {date}")
    cash_count, _ = CashCount.objects.get_or_create(
        branch=branch,
        date=date,
        prepared_by=employee
    )

    if request.method == 'POST':
        cash_count.one_thousands = int(
            request.POST.get('one_thousands') or '0')
        cash_count.five_hundreds = int(
            request.POST.get('five_hundreds') or '0')
        cash_count.two_hundreds = int(request.POST.get('two_hundreds') or '0')
        cash_count.one_hundreds = int(request.POST.get('one_hundreds') or '0')
        cash_count.fifties = int(request.POST.get('fifties') or '0')
        cash_count.twenties = int(request.POST.get('twenties') or '0')
        cash_count.tens = int(request.POST.get('tens') or '0')
        cash_count.fives = int(request.POST.get('fives') or '0')
        cash_count.coins = int(request.POST.get('coins') or '0')
        cash_count.coins_total = Decimal(
            request.POST.get('coins_total') or '0')
        cash_count.save()
        is_updated = True

    context = {
        'cash_count': cash_count,
        'sel_date': date,
        'selected_branch': branch.name + ' Branch',
        'is_today': is_today,
        'is_updated': is_updated
    }
    return render(request, 'reports/cash_count.html', context)


@method_decorator(login_required, name='dispatch')
class OtherCashCountCreateView(CreateView):
    model = OtherCashCount
    template_name = 'reports/cash_count_form.html'
    form_class = OtherCashCountForm

    def post(self, request, *args, **kwargs):
        form = OtherCashCountForm(request.POST)
        if form.is_valid():
            pk = kwargs.get('pk')
            cash_count = CashCount.objects.get(pk=pk)
            other = form.save(commit=False)
            other.cash_count = cash_count
            other.save()
            messages.success(
                request, f"New item on cash count was added successfully.")
            if "another" in request.POST:
                return redirect('add_cash_count', pk=pk)
            else:
                return redirect('cash_count')


def generate_auction_report(employee: Employee):
    branch = employee.branch
    report = Pawn.expired.filter(on_hold=False)

    if not branch:
        branch = 'All Branches'
        report = report.all()
    else:
        report = report.filter(branch=branch)
        branch = branch.name + ' Branch'

    return report, branch


@login_required
def auction_report(request):
    employee = Employee.objects.get(user=request.user)
    report, branch = generate_auction_report(employee)

    principal_total = report.aggregate(Sum('principal'))['principal__sum']
    interest_total = sum([pawn.getAuctionInterest() for pawn in report])
    grand_total = principal_total + interest_total

    context = {
        'report': report,
        'branch': branch,
        'type': type,
        'principal_total': principal_total,
        'interest_total': interest_total,
        'grand_total': grand_total
    }

    if branch == 'All Branches':
        return render(request, 'reports/auction_overall.html', context)
    else:
        return render(request, 'reports/auction_branch.html', context)


@login_required
def add_to_auction(request, pk):
    employee = Employee.objects.get(user=request.user)
    report, branch = generate_auction_report(employee)
    for pawn in report:
        if pawn.pk == pk:
            pawn.status = Pawn.AUCTIONED
            pawn.status_updated_on = timezone.now()
            pawn.save()


@login_required
def delete_receipt(request, pk):
    receipt = AddReceipts.objects.get(pk=pk)
    receipt.delete()
    messages.success(
        request, f"Receipt was deleted successfully.")
    return redirect('daily_cash_position')


@login_required
def delete_disbursement(request, pk):
    disbursement = LessDisbursements.objects.get(pk=pk)
    disbursement.delete()
    messages.success(
        request, f"Disbursement was deleted successfully.")
    return redirect('daily_cash_position')


@login_required
def new_pawn_tickets(request):
    sel_branch = request.GET.get('branch', None)
    sel_month = request.GET.get('month', None)

    pawns = None
    branch = None
    selected_month = None
    selected_branch = None
    pawn_list = Pawn.objects.all()

    if selected_branch or sel_month:
        pawn_list = pawn_list.filter(status='ACTIVE')
    if sel_branch:
        sel_branch = int(sel_branch)
        if sel_branch >= 0:
            branch = get_object_or_404(Branch, pk=sel_branch)
            pawn_list = pawn_list.filter(branch=branch)
            selected_branch = f"{branch} Branch"
        else:
            selected_branch = "All Branches"
    if sel_month:
        parts = sel_month.split("-")
        year = int(parts[0])
        month = int(parts[1])
        selected_month = get_month_name(month, year).upper()
        pawn_list = pawn_list.filter(
            date__year=year,
            date__month=month
        )

    if pawn_list.count() > 0:
        pawns = []
        for pawn in pawn_list:
            if not hasattr(pawn, 'pawn_renewed_to'):
                pawns.append(pawn)

    context = {
        'pawns': pawns,
        'branch': branch,
        'branches': Branch.objects.all(),
        'selected_month': selected_month,
        'selected_branch': selected_branch,
        'sel_branch': sel_branch,
        'sel_month': sel_month,
    }

    return render(request, 'reports/new_pawn_tickets.html', context)


@login_required
def income_statement(request):
    # make sure that the logged employee is from a branch ====================
    employee = Employee.objects.get(user=request.user)
    branch = employee.branch
    if not branch:
        raise Http404("This feature is only available to branches.")

    # determine the report month ============================================
    selected_month = None
    interest = 0
    adv_interest = 0
    service_charge = 0
    total_expenses = 0
    expense_summary = None
    sel_month = request.GET.get('month', None)
    year = timezone.now().year
    month = timezone.now().month
    if sel_month:
        parts = sel_month.split("-")
        year = int(parts[0])
        month = int(parts[1])
        selected_month = get_month_name(month, year).upper()

        # for the income ========================================================
        payment_list = Payment.objects.filter(
            date__year=year,
            date__month=month,
            pawn__branch=branch
        )

        # sum interests (together with advance interest) and service charge
        for payment in payment_list:
            print(f"PTN: {payment.pawn.getPTN}")
            print(f"Interest: {payment.paid_interest}")
            print(f"Advance Interest: {payment.advance_interest}")
            print(f"Service Fee: {payment.service_fee}")
            print(
                f"Total: {payment.paid_interest + payment.advance_interest + payment.service_fee}\n")
            interest += payment.paid_interest
            adv_interest += payment.advance_interest
            service_charge += payment.service_fee

        # for the expenses =======================================================
        expenses = Expense.objects.filter(
            date__year=year,
            date__month=month,
            branch=branch
        )

        # Annotate total amount per category
        expense_summary = expenses.values('category__category').annotate(
            total_amount=Sum('amount')
        ).order_by('category__category')
        print(f"expense_summary:\n{expense_summary}")

        total_expenses = expenses.aggregate(
            grand_total=Sum('amount'))['grand_total'] or 0

    income = service_charge + interest + adv_interest

    context = {
        'branch': f"{branch} Branch",
        'sel_month': sel_month,
        'selected_month': selected_month,
        'interest': interest,
        'adv_interest': adv_interest,
        'service_charge': service_charge,
        'income': income,
        'expense_summary': expense_summary,
        'total_expenses': total_expenses,
        'net_income': income - total_expenses
    }

    return render(request, 'reports/income_statement.html', context)

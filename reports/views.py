from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Sum
from django.http import Http404
from django.views.generic import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from decimal import Decimal

from files.models import Branch
from expense.models import Expense
from pawn.models import Pawn
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


def nonrenewal_report(request):
    sel_branch = request.GET.get('branch', None)
    sel_type = request.GET.get('type', None)

    report = None
    grand_total = 0

    if sel_branch and sel_type:
        report = Pawn.star  # assumes star
        sel_branch = int(sel_branch)
        if sel_type == 'orig':  # orig
            report = Pawn.orig
        if sel_branch == -1:
            sel_branch = 'All Branches'
            report = report.all()
        else:
            branch = Branch.objects.get(pk=sel_branch)
            report = report.filter(branch=branch)
            sel_branch = branch.name

        grand_total = report.aggregate(Sum('principal'))['principal__sum']

    context = {
        "branches": Branch.objects.all(),
        "sel_branch": sel_branch,
        "sel_type": sel_type.upper(),
        "report": report,
        "grand_total": grand_total
    }

    return render(request, 'reports/non_renewal.html', context)


def daily_cash_position(request):
    date = request.GET.get('date')
    is_today = False
    if not date:
        date = timezone.now().date()
        is_today = True
    else:
        date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
    employee = Employee.objects.get(user=request.user)
    branch = employee.branch
    if not branch:
        raise Http404("This feature is only available to branches.")
    print(f"Branch: {branch}")
    print(f"Date: {date}")
    daily_cash_position, _ = DailyCashPosition.objects.get_or_create(
        branch=branch,
        date=date,
        prepared_by=employee
    )
    receipts = daily_cash_position.receipts.all()
    disbursements = daily_cash_position.disbursements.all()
    last = DailyCashPosition.objects.all().order_by('date').last()
    context = {
        'cash_position': daily_cash_position,
        'receipts': receipts,
        'disbursements': disbursements,
        'last': last,
        'sel_date': date,
        'selected_branch': branch.name + ' Branch',
        'is_today': is_today
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


def cash_count(request):
    date = request.GET.get('date')
    is_today = False
    if not date:
        date = timezone.now().date()
        is_today = True
    else:
        date = timezone.datetime.strptime(date, '%Y-%m-%d').date()
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

    context = {
        'cash_count': cash_count,
        'sel_date': date,
        'selected_branch': branch.name + ' Branch',
        'is_today': is_today
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

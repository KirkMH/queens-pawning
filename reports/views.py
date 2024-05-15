from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from files.models import Branch
from expense.models import Expense


def get_month_name(month, year):
    month_names = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]
    return f"{month_names[month - 1]} {year}"


@login_required
def itemized_expenses(request):
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
    for exp in expenses:
        total = 0
        for expense in exp['expenses']:
            total += expense.amount
        exp['total'] = total
    print(f"expenses: {expenses}")
    context = {
        'branches': Branch.objects.all(),
        'expenses': expenses,
        'sel_branch': sel_branch,
        'sel_month': sel_month,
        'selected_branch': selected_branch,
        'selected_month': selected_month
    }
    return render(request, 'reports/itemized_expenses.html', context=context)

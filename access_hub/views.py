from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from files.models import Client
from pawn.models import Pawn
from .models import Employee

from datetime import date


@login_required
def dashboard(request):
    employee = Employee.objects.get(user=request.user)
    clients = Client.objects.filter(
        date_registered=date.today())
    transactions = Pawn.objects.filter(
        date=date.today())
    matured = Pawn.matured.all()
    expired = Pawn.expired.all()
    print(f"branch: {request.user.employee.branch}")
    if employee.branch:
        clients = clients.filter(branch=employee.branch)
        transactions = transactions.filter(branch=employee.branch)
        matured = matured.filter(branch=employee.branch)
        expired = expired.filter(branch=employee.branch)
    context = {
        'greeting': 'Hello, there!',
        'newClientCountToday': clients.count(),
        'transactionsCountToday': transactions.count(),
        'maturedToday': matured.count(),
        'expiredToday': expired.count(),
    }
    return render(request, 'dashboard.html', context)

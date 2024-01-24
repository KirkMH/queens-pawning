from django.shortcuts import render

from files.models import Client
from pawn.models import Pawn

from datetime import date


def dashboard(request):
    newClientCountToday = Client.objects.filter(
        date_registered=date.today()).count()
    transactionsCountToday = Pawn.objects.filter(
        date__date=date.today()).count()
    context = {
        'greeting': 'Hello, there!',
        'newClientCountToday': newClientCountToday,
        'transactionsCountToday': transactionsCountToday
    }
    return render(request, 'dashboard.html', context)

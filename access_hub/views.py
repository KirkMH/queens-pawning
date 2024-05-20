from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from files.models import Client
from pawn.models import Pawn

from datetime import date


@login_required
def dashboard(request):
    newClientCountToday = Client.objects.filter(
        date_registered=date.today()).count()
    transactionsCountToday = Pawn.objects.filter(
        date__date=date.today()).count()
    context = {
        'greeting': 'Hello, there!',
        'newClientCountToday': newClientCountToday,
        'transactionsCountToday': transactionsCountToday,
        'maturedToday': Pawn.matured.count(),
        'expiredToday': Pawn.expired.count(),
    }
    return render(request, 'dashboard.html', context)

from django.shortcuts import render


def dashboard(request):
    context = {
        'greeting': 'Hello, there!',
    }
    return render(request, 'dashboard.html', context)

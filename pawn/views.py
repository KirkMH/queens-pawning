from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
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
    return render(request, 'pawn/pawn_list.html')


@method_decorator(login_required, name='dispatch')
class PawnDTListView(ServerSideDatatableView):
    queryset = Pawn.objects.all()
    columns = ['pk', 'date', 'client', 'description', 'principal',
               'service_charge', 'advance_interest', 'net_proceeds', 'status',
               'client__title', 'client__last_name', 'client__first_name', 'client__middle_name']

    def get_queryset(self):
        if Employee.objects.filter(user=self.request.user).count() > 0 and Employee.objects.get(user=self.request.user).branch:
            return super().get_queryset().filter(branch=Employee.objects.get(user=self.request.user).branch)
        else:
            return super().get_queryset()


@method_decorator(login_required, name='dispatch')
class PawnCreateView(CreateView):
    model = Pawn
    form_class = PawnForm
    template_name = 'pawn/pawn_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['otherFees'] = OtherFees.get_instance()
        return context

    def post(self, request, *args, **kwargs):
        form = PawnForm(request.POST)
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

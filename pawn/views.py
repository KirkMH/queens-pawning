from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django_serverside_datatable.views import ServerSideDatatableView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from decimal import Decimal

from files.models import OtherFees
from .models import *
from .forms import *


###############################################################################################
#                Pawn Transactions
###############################################################################################

def pawn_list(request):
    return render(request, 'pawn/pawn_list.html')


class PawnDTListView(ServerSideDatatableView):
    queryset = Pawn.objects.all()
    columns = ['pk', 'date', 'client', 'description', 'principal',
               'service_charge', 'advance_interest', 'net_proceeds', 'status']
    foreign_fields = {'client': 'client__first_name'}


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
            saved = form.save(commit=True)
            messages.success(
                request, f"New pawn ticket for {saved.client} was created successfully.")
            if "another" in request.POST:
                return redirect('new_pawn')
            else:
                return redirect('pawn_list')

        else:
            return render(request, 'pawn/pawn_form.html', {'form': form})


# class PawnUpdateView(SuccessMessageMixin, UpdateView):
#     model = Pawn
#     context_object_name = 'Pawn'
#     form_class = PawnForm
#     template_name = "pawn/pawn_form.html"
#     pk_url_kwarg = 'pk'
#     success_url = reverse_lazy('pawn_list')
#     success_message = "The Pawn's record was updated successfully."


# class PawnDetailView(DetailView):
#     model = Pawn
#     template_name = "files/pawn_detail.html"
#     context_object_name = 'Pawn'

from collections.abc import Mapping
from typing import Any
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import *
from files.models import OtherFees


############################
#       PAWN
############################
class PawnForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Pawn
        exclude = ('status', 'on_hold', 'status_updated_on',
                   'branch', 'renewed_to', 'additional_principal', 'renew_redeem_date')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PawnForm, self).__init__(*args, **kwargs)

        self.fields['date_granted'].initial = timezone.now().date()
        self.fields['promised_renewal_date'].initial = timezone.now().date()
        self.fields['service_charge'].initial = OtherFees.get_instance().service_fee
        print(
            f'service charge via forms: {OtherFees.get_instance().service_fee}')
        self.fields['client'].queryset = Client.objects.filter(status='ACTIVE')
        self.fields['date_granted'].required = True
        if self.request:
            branch = Employee.objects.get(user=self.request.user).branch
            if branch:
                self.fields['client'].queryset = self.fields['client'].queryset.filter(
                    branch=Employee.objects.get(user=self.request.user).branch)

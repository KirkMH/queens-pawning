from collections.abc import Mapping
from typing import Any
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from .models import *
from files.models import OtherFees


############################
#       PAWN
############################
class PawnForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Pawn
        exclude = ('status', 'date', 'status_updated_on',
                   'branch', 'renewed_to')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PawnForm, self).__init__(*args, **kwargs)

        self.fields['client'].queryset = Client.objects.filter(status='ACTIVE')
        if self.request:
            self.fields['client'].queryset = self.fields['client'].queryset.filter(
                branch=Employee.objects.get(user=self.request.user).branch)
        # self.fields['service_charge'].widget.attrs['disabled'] = True
        # self.fields['advance_interest'].widget.attrs['disabled'] = True
        # self.fields['net_proceeds'].widget.attrs['disabled'] = True
        # self.fields['service_charge'].widget.attrs['required'] = False
        # self.fields['advance_interest'].widget.attrs['required'] = False
        # self.fields['net_proceeds'].widget.attrs['required'] = False


class PawnPaymentForm(forms.Form):
    # I need 3 number fields: amount, tendered, and discount
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    tendered = forms.DecimalField(
        max_digits=10, decimal_places=2, required=True)
    discount = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False, initial=0)

    # to check if valid, tendere should be greater than or equal to amount - discount
    def clean(self) -> Mapping[str, Any]:
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount') or 0
        tendered = cleaned_data.get('tendered') or 0
        discount = cleaned_data.get('discount') or 0
        if tendered < amount - discount:
            self.add_error('tendered', _(
                'Tendered amount should be greater than or equal to the total amount less the discount.'))
        return cleaned_data

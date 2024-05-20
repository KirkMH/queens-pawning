from django import forms
from django.utils.translation import gettext_lazy as _

from .models import *


class ReceiptForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = AddReceipts
        exclude = ('daily_cash_position', )


class DisbursementForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = LessDisbursements
        exclude = ('daily_cash_position', )


class OtherCashCountForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = OtherCashCount
        exclude = ('cash_count', )

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import *


class ReceiptForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = AddReceipts
        exclude = ('daily_cash_position', )

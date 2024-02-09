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
        exclude = ('status', 'date', 'status_updated_on', 'branch', )

    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.fields['client'].queryset = Client.objects.filter(status='ACTIVE')
        # self.fields['service_charge'].widget.attrs['disabled'] = True
        # self.fields['advance_interest'].widget.attrs['disabled'] = True
        # self.fields['net_proceeds'].widget.attrs['disabled'] = True
        # self.fields['service_charge'].widget.attrs['required'] = False
        # self.fields['advance_interest'].widget.attrs['required'] = False
        # self.fields['net_proceeds'].widget.attrs['required'] = False

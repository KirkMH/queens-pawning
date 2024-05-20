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
        exclude = ('status', 'on_hold', 'status_updated_on',
                   'branch', 'renewed_to',)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(PawnForm, self).__init__(*args, **kwargs)

        self.fields['client'].queryset = Client.objects.filter(status='ACTIVE')
        if self.request:
            self.fields['client'].queryset = self.fields['client'].queryset.filter(
                branch=Employee.objects.get(user=self.request.user).branch)

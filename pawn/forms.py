from collections.abc import Mapping
from typing import Any
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from .models import *


############################
#       PAWN
############################
class PawnForm(forms.ModelForm):
    required_css_class = 'required'
    clients = forms.ModelChoiceField(queryset=Client.objects.all())

    class Meta:
        model = Pawn
        fields = '__all__'

    def __init__(self, *args, **kwards):
        super().__init__(*args, **kwards)
        self.fields['client'].queryset = Client.objects.filter(status='ACTIVE')

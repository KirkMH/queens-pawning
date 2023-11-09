from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *


############################
#       CLIENT
############################
class ClientForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Client
        fields = '__all__'

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


############################
#       EXPENSE CATEGORY
############################
class ExpenseCategoryForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = ExpenseCategory
        fields = '__all__'


############################
#       Branches
############################
class BranchForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Branch
        fields = '__all__'

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *


############################
#       CLIENT
############################
class ClientForm(forms.ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_link'].required = True
        self.fields['middle_name'].required = False

    class Meta:
        model = Client
        exclude = ('status', 'branch')


class AdminClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_link'].required = True

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
        exclude = ('status', )


############################
#       Branches
############################
class BranchForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Branch
        exclude = ('status', )

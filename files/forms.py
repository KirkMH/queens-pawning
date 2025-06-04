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
        exclude = ('status', )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract user from kwargs
        super().__init__(*args, **kwargs)

        self.fields['id_link'].required = True
        self.fields['middle_name'].required = False

        if user.employee.branch is not None:
            self.fields['branch'].initial = user.employee.branch
            self.fields['branch'].widget = forms.HiddenInput()
            self.fields['branch'].label = ""


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

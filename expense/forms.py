from django import forms

from .models import Expense


class ExpenseForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = Expense
        exclude = ['encoded_by', 'encoded_on']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

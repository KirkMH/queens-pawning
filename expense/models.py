from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from files.models import ExpenseCategory, Branch
from access_hub.models import Employee

from django.utils import timezone


class Expense(models.Model):
    branch = models.ForeignKey(
        Branch,
        related_name='expenses',
        on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        ExpenseCategory,
        related_name='expenses',
        on_delete=models.CASCADE
    )
    description = models.CharField(max_length=250)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    date = models.DateField(
        validators=[MaxValueValidator(timezone.now().date())])
    encoded_by = models.ForeignKey(
        Employee,
        related_name='expenses_encoded',
        on_delete=models.CASCADE
    )
    encoded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description

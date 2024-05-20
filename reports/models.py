from django.db import models

from files.models import Branch
from access_hub.models import Employee


class DailyCashPosition(models.Model):
    date = models.DateField()
    branch = models.ForeignKey(
        Branch,
        related_name='daily_cash_positions',
        on_delete=models.CASCADE
    )
    balance_coh = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    balance_cib = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    cash_in_bank = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    deposits = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    withdrawals = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    prepared_by = models.ForeignKey(
        Employee,
        related_name='daily_cash_positions',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.date} - {self.branch}'

    def get_total_balance(self):
        return self.balance_coh + self.balance_cib

    def get_subtotal(self):
        return self.cash_in_bank + self.deposits

    def get_cash_in_bank(self):
        return self.get_subtotal() - self.withdrawals

    def get_total_receipts(self):
        return sum([receipt.amount for receipt in self.receipts.all()])

    def get_total_disbursements(self):
        return sum([disbursement.amount for disbursement in self.disbursements.all()])

    def get_net_subtotal(self):
        return self.get_total_balance() + self.get_total_receipts()

    def get_net_total(self):
        return self.get_net_subtotal() - self.get_total_disbursements()


class AddReceipts(models.Model):
    daily_cash_position = models.ForeignKey(
        DailyCashPosition,
        related_name='receipts',
        on_delete=models.CASCADE
    )
    reference_number = models.CharField(max_length=20, blank=True, null=True)
    received_from = models.CharField(max_length=50, blank=True, null=True)
    particulars = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f'{self.particulars} - {self.amount}'


class LessDisbursements(models.Model):
    daily_cash_position = models.ForeignKey(
        DailyCashPosition,
        related_name='disbursements',
        on_delete=models.CASCADE
    )
    reference_number = models.CharField(max_length=20, blank=True, null=True)
    payee = models.CharField(max_length=50, blank=True, null=True)
    particulars = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f'{self.particulars} - {self.amount}'

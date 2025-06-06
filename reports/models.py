from django.db import models
from django.utils import timezone

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
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    def __str__(self):
        return f'{self.date} - {self.branch}: {self.get_net_total()}'

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
        return self.balance_coh + self.get_total_receipts()

    def get_net_total(self):
        return self.get_net_subtotal() - self.get_total_disbursements()

    def fill_in_from_yesterday(self):
        # get the last daily cash position before today
        positions = DailyCashPosition.objects.filter(
            branch=self.branch,
            date__lt=self.date
        ).order_by('-date')

        last_position = None
        if positions.exists():
            last_position = positions.first()
            self.balance_coh = last_position.get_net_total()
            self.balance_cib = last_position.get_cash_in_bank()
            self.cash_in_bank = last_position.get_cash_in_bank()
            self.save()
        return last_position


class AddReceipts(models.Model):
    daily_cash_position = models.ForeignKey(
        DailyCashPosition,
        related_name='receipts',
        on_delete=models.CASCADE
    )
    pawn = models.ForeignKey(
        "pawn.Pawn",
        related_name='receipts',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    reference_number = models.CharField(max_length=20, blank=True, null=True)
    received_from = models.CharField(max_length=50, blank=True, null=True)
    particulars = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    automated = models.BooleanField(default=False)

    def __str__(self):
        ref = ""
        if self.reference_number:
            ref = f"PTN {self.reference_number}: "
        return f'{ref}{self.particulars} - {self.amount}'

    class Meta:
        verbose_name_plural = 'Add Receipts'
        verbose_name = 'Add Receipt'


class LessDisbursements(models.Model):
    daily_cash_position = models.ForeignKey(
        DailyCashPosition,
        related_name='disbursements',
        on_delete=models.CASCADE
    )
    pawn = models.ForeignKey(
        "pawn.Pawn",
        related_name='disbursements',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    reference_number = models.CharField(max_length=20, blank=True, null=True)
    payee = models.CharField(max_length=50, blank=True, null=True)
    particulars = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    automated = models.BooleanField(default=False)

    def __str__(self):
        ref = ""
        if self.reference_number:
            ref = f"PTN {self.reference_number}: "
        return f'{ref}{self.particulars} - {self.amount}'

    class Meta:
        verbose_name_plural = 'Less Disbursements'
        verbose_name = 'Less Disbursement'


class CashCount(models.Model):
    date = models.DateField()
    branch = models.ForeignKey(
        Branch,
        related_name='cash_counts',
        on_delete=models.CASCADE
    )
    prepared_by = models.ForeignKey(
        Employee,
        related_name='cash_counts',
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    one_thousands = models.IntegerField(default=0)
    five_hundreds = models.IntegerField(default=0)
    two_hundreds = models.IntegerField(default=0)
    one_hundreds = models.IntegerField(default=0)
    fifties = models.IntegerField(default=0)
    twenties = models.IntegerField(default=0)
    tens = models.IntegerField(default=0)
    fives = models.IntegerField(default=0)
    coins = models.IntegerField(default=0)
    coins_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def total_one_thousands(self):
        return self.one_thousands * 1000

    def total_five_hundreds(self):
        return self.five_hundreds * 500

    def total_two_hundreds(self):
        return self.two_hundreds * 200

    def total_one_hundreds(self):
        return self.one_hundreds * 100

    def total_fifties(self):
        return self.fifties * 50

    def total_twenties(self):
        return self.twenties * 20

    def total_tens(self):
        return self.tens * 10

    def total_fives(self):
        return self.fives * 5

    def total_cash(self):
        return self.total_one_thousands() + self.total_five_hundreds() + self.total_two_hundreds() + self.total_one_hundreds() + self.total_fifties() + self.total_twenties() + self.total_tens() + self.total_fives() + self.coins_total

    def total_others(self):
        return sum([other.amount for other in self.other_cash_counts.all()])

    def grand_total(self):
        return self.total_cash() + self.total_others()

    def remarks(self):
        remark = ''
        position = DailyCashPosition.objects.filter(
            branch=self.branch,
            date=self.date
        ).first()

        if position:
            net_total = position.get_net_total()
            if net_total > self.grand_total():
                remark = 'Cash shortage'
            elif net_total < self.grand_total():
                remark = 'Cash over'
            else:
                remark = '---'
        else:
            remark = 'No Daily Cash Position'

        return remark

    def __str__(self):
        return f'{self.date}: {self.grand_total()}'


class OtherCashCount(models.Model):
    cash_count = models.ForeignKey(
        CashCount,
        related_name='other_cash_counts',
        on_delete=models.CASCADE
    )
    particulars = models.CharField(max_length=50)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f'{self.particulars} - {self.amount}'

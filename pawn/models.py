from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from datetime import datetime
from decimal import Decimal

from files.models import Client, Branch, InterestRate, TermDuration
from access_hub.models import Employee


class Inventory(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(status__in=['REDEEMED', 'AUCTIONED'])


class Pawn(models.Model):
    ACTIVE = 'ACTIVE'
    RENEWED = 'RENEWED'
    REDEEMED = 'REDEEMED'
    MATURED = 'MATURED'
    EXPIRED = 'EXPIRED'
    AUCTIONED = 'AUCTIONED'
    STATUS = [
        (ACTIVE, _('Active')),
        (RENEWED, _('Renewed')),
        (REDEEMED, _('Redeemed')),
        (MATURED, _('Matured')),
        (EXPIRED, _('Expired')),
        (AUCTIONED, _('Auctioned'))
    ]

    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=False, blank=False
    )
    description = models.TextField(
        _('Description'),
        null=False, blank=False
    )
    principal = models.DecimalField(
        _('Principal'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    service_charge = models.DecimalField(
        _('LESS: Service Charge'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    advance_interest = models.DecimalField(
        _('LESS: Advance Interest'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    net_proceeds = models.DecimalField(
        _('Net Proceeds'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS,
        default=ACTIVE,
        null=False, blank=False
    )
    status_updated_on = models.DateTimeField(null=True, blank=True)
    branch = models.ForeignKey(
        Branch,
        related_name='pawn_branch',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    objects = models.Manager()
    history = HistoricalRecords()
    Inventory = Inventory()

    def __str__(self):
        return f"{self.description} by {self.client}"

    def getElapseDays(self):
        return (datetime.now().date() - self.date.date()).days

    def getInterestRate(self):
        elapsed = self.getElapseDays()
        rate = InterestRate.rates.get_rate(elapsed)
        return rate if rate else 0

    def getInterest(self):
        return self.principal * Decimal(str((self.getInterestRate() / 100)))

    def hasPenalty(self):
        return self.getElapseDays() > TermDuration.get_instance().maturity

    def getPenalty(self):
        if self.hasPenalty():
            daysPenalty = self.getElapseDays() - TermDuration.get_instance().maturity
            return self.principal * (InterestRate.rates.get_max_rate() / 100) * (daysPenalty / 30)
        return 0

    def getTotalDue(self):
        return self.principal + self.getInterest() + self.getPenalty()

    def getMinimumPayment(self):
        return self.getInterest() + self.getPenalty()


class Payment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    pawn = models.ForeignKey(
        Pawn,
        on_delete=models.CASCADE,
        null=False, blank=False
    )
    amount_paid = models.DecimalField(
        _('Amount Paid'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    paid_for_principal = models.DecimalField(
        _('Paid for Principal'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    cashier = models.ForeignKey(
        Employee,
        related_name='payment_cashier',
        on_delete=models.CASCADE,
        null=False, blank=False
    )

    def __str__(self):
        return f"{self.pawn} - {self.amount_paid} by {self.cashier} on {self.date}"

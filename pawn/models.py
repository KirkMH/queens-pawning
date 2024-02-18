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
        return super().get_queryset().filter(status='ACTIVE')


class Pawn(models.Model):
    ACTIVE = 'ACTIVE'
    RENEWED = 'RENEWED'
    REDEEMED = 'REDEEMED'
    AUCTIONED = 'AUCTIONED'
    STATUS = [
        (ACTIVE, _('Active')),
        (RENEWED, _('Renewed')),
        (REDEEMED, _('Redeemed')),
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
    renewed_to = models.OneToOneField(
        'self',
        related_name='pawn_renewed_to',
        on_delete=models.CASCADE,
        null=True, blank=True
    )

    objects = models.Manager()
    history = HistoricalRecords()
    inventory = Inventory()

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

    def hasMatured(self):
        return self.getElapseDays() >= TermDuration.get_instance().maturity

    def hasExpired(self):
        return self.getElapseDays() > TermDuration.get_instance().expiration

    def hasPenalty(self):
        return self.getElapseDays() > TermDuration.get_instance().maturity

    def getStanding(self):
        if self.hasExpired():
            return 'EXPIRED'
        if self.hasMatured():
            return 'MATURED'
        return 'ACTIVE'

    def getPenalty(self):
        if self.hasPenalty():
            daysPenalty = Decimal(
                str(self.getElapseDays() - TermDuration.get_instance().maturity))
            return self.principal * (InterestRate.rates.get_max_rate() / 100) * (daysPenalty / 30)
        return 0

    def getTotalDue(self):
        return self.principal + self.getInterest() + self.getPenalty()

    def getMinimumPayment(self):
        return self.getInterest() + self.getPenalty()

    def pay(self, amount_paid, cashier):
        if amount_paid > self.getMinimumPayment():
            paid_for_principal = amount_paid - self.getMinimumPayment()

        if amount_paid == self.getTotalDue():
            self.status = 'REDEEMED'
        else:
            # create a new pawn ticket for the renewed pawn
            new_principal = self.principal - paid_for_principal
            new_pawn = Pawn()
            new_pawn.client = self.client
            new_pawn.description = self.description
            new_pawn.principal = new_principal
            new_pawn.service_charge = 0
            new_pawn.advance_interest = 0
            new_pawn.net_proceeds = 0
            new_pawn.branch = self.branch
            new_pawn.status = 'ACTIVE'
            new_pawn.save()

            self.status = 'RENEWED'
            new_pawn.renewed_to = new_pawn

        self.status_updated_on = datetime.now()
        self.save()

        payment = Payment()
        payment.amount_paid = amount_paid
        payment.pawn = self
        payment.cashier = cashier
        payment.paid_for_principal = paid_for_principal
        payment.save()


class Payment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    pawn = models.OneToOneField(
        Pawn,
        on_delete=models.CASCADE,
        related_name='payment_pawn',
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


class DiscountRequests(models.Model):
    STATUS = [
        ('PENDING', _('Pending')),
        ('APPROVED', _('Approved')),
        ('REJECTED', _('Rejected')),
        ('CANCELLED', _('Cancelled'))
    ]

    date = models.DateTimeField(auto_now_add=True)
    pawn = models.OneToOneField(
        Pawn,
        on_delete=models.CASCADE,
        related_name='discount_requested',
        null=False, blank=False
    )
    amount = models.DecimalField(
        _('Amount'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS,
        default='PENDING',
        null=False, blank=False
    )
    requested_by = models.ForeignKey(
        Employee,
        related_name='discount_requested_by',
        on_delete=models.CASCADE,
        null=False, blank=False
    )
    approved_by = models.ForeignKey(
        Employee,
        related_name='discount_approved_by',
        on_delete=models.CASCADE,
        null=True, blank=True,
        default=None
    )
    approved_on = models.DateTimeField(null=True, blank=True, default=None)

    def cancel(self):
        self.status = 'CANCELLED'
        self.save()

    def approve(self, employee):
        self.status = 'APPROVED'
        self.approved_by = employee
        self.approved_on = datetime.now()
        self.save()

    def reject(self, employee):
        self.status = 'REJECTED'
        self.approved_by = employee
        self.approved_on = datetime.now()
        self.save()

    def __str__(self):
        return f"{self.pawn} - {self.amount} on {self.date}"

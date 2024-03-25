from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from datetime import datetime
from decimal import Decimal

from files.models import Client, Branch, InterestRate, TermDuration, OtherFees
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
    CARAT = [
        ('10k', '10k'),
        ('12k', '12k'),
        ('18k', '18k'),
        ('21k', '21k'),
        ('24k', '24k')
    ]
    COLOR = [
        ('White Gold', _('White Gold')),
        ('Yellow Gold', _('Yellow Gold')),
        ('Rose Gold', _('Rose Gold')),
        ('Saudi Gold', _('Saudi Gold')),
        ('Japan Gold', _('Japan Gold')),
        ('Tri-Color', _('Tri-Color'))
    ]
    ITEM_DESCRIPTION = [
        ('Anklet', _('Anklet')),
        ('Bangle', _('Bangle')),
        ('Bracelet', _('Bracelet')),
        ('Stud Earrings', _('Stud Earrings')),
        ('Loop Earrings', _('Loop Earrings')),
        ('Clip Earrings', _('Clip Earrings')),
        ('Stud Earrings', _('Stud Earrings')),
        ('Dangling Earrings', _('Dangling Earrings')),
        ('Ring', _('Ring')),
        ('Wedding Ring', _('Wedding Ring')),
        ('Necklace', _('Necklace')),
        ('Pendant', _('Pendant'))
    ]

    date = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=False, blank=False
    )
    quantity = models.PositiveIntegerField(
        _('Quantity'),
        null=False, blank=False,
        default=1
    )
    carat = models.CharField(
        _('Carat'),
        max_length=10,
        choices=CARAT,
        null=False, blank=False
    )
    color = models.CharField(
        _('Color'),
        max_length=20,
        choices=COLOR,
        null=False, blank=False
    )
    item_description = models.CharField(
        _('Item Description'),
        max_length=20,
        choices=ITEM_DESCRIPTION,
        null=False, blank=False
    )
    description = models.TextField(
        _('Additional Description')
    )
    grams = models.DecimalField(
        _('Grams'),
        max_digits=5,
        decimal_places=2,
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
        return f"{self.complete_description} by {self.client}"

    @property
    def complete_description(self):
        unit = 'pcs' if self.quantity > 1 else 'pc'
        return f"{self.quantity}{unit} {self.carat} {self.color} {self.item_description} {self.description} {self.grams}g"

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

    def getRenewalServiceFee(self):
        return OtherFees.get_instance().service_fee

    def getRenewalAdvanceInterest(self):
        return OtherFees.get_instance().advance_interest_rate * self.principal

    def getMinimumPayment(self):
        otherFees = OtherFees.get_instance()
        service_charge = otherFees.service_fee
        adv_int = otherFees.advance_interest_rate * self.principal
        return self.getInterest() + self.getPenalty() + service_charge + adv_int

    def pay(self, amount_paid, cashier):
        discounted = 0
        dr = DiscountRequests.objects.filter(pawn=self)
        if dr:
            discounted = dr.first().getApprovedDiscount()

        if amount_paid == self.getTotalDue():
            paid_for_principal = self.principal
            self.status = 'REDEEMED'
        else:
            paid_for_principal = amount_paid - self.getMinimumPayment() + discounted
            new_principal = self.principal - paid_for_principal
            otherFees = OtherFees.get_instance()
            new_sf = otherFees.service_fee
            new_ai = otherFees.advance_interest_rate * new_principal
            # create a new pawn ticket for the renewed pawn
            new_pawn = Pawn()
            new_pawn.client = self.client
            new_pawn.quantity = self.quantity
            new_pawn.carat = self.carat
            new_pawn.color = self.color
            new_pawn.item_description = self.item_description
            new_pawn.description = self.description
            new_pawn.grams = self.grams
            new_pawn.principal = new_principal
            new_pawn.service_charge = new_sf
            new_pawn.advance_interest = new_ai
            new_pawn.net_proceeds = new_principal - new_sf - new_ai
            new_pawn.branch = self.branch
            new_pawn.status = 'ACTIVE'
            new_pawn.save()

            self.status = 'RENEWED'
            self.renewed_to = new_pawn

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

    def getApprovedDiscount(self):
        return self.amount if self.status == 'APPROVED' else 0

    def __str__(self):
        return f"{self.pawn} - {self.amount} on {self.date}"

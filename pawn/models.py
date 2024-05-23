from django.db import models
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from django.utils import timezone
from decimal import Decimal

from files.models import Client, Branch, InterestRate, AdvanceInterestRate, TermDuration, OtherFees
from access_hub.models import Employee
from reports.models import AddReceipts, DailyCashPosition, LessDisbursements


class Inventory(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='ACTIVE')


class Expired(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        expired_today = timezone.now().date(
        ) - timezone.timedelta(days=TermDuration.get_instance().expiration)
        return qs.filter(status='ACTIVE').filter(date__date__lte=expired_today)


class Matured(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        matured_today = timezone.now().date(
        ) - timezone.timedelta(days=TermDuration.get_instance().maturity)
        return qs.filter(status='ACTIVE').filter(date__date__lte=matured_today)


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
        ('24k', '24k'),
        ('Others', 'Others, specify in description')
    ]
    COLOR = [
        ('White Gold', _('White Gold')),
        ('Yellow Gold', _('Yellow Gold')),
        ('Rose Gold', _('Rose Gold')),
        ('Saudi Gold', _('Saudi Gold')),
        ('Japan Gold', _('Japan Gold')),
        ('Tri-Color', _('Tri-Color')),
        ('Others', 'Others, specify in description')
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
        ('Pendant', _('Pendant')),
        ('Others', 'Others, specify in description')
    ]
    TRANSACTION_TYPE = [
        ('NEW', _('New')),
        ('EXISTING', _('Existing'))
    ]

    date = models.DateTimeField(auto_now_add=True)
    # NEW = Advance Interest Rate; EXISTING = Interest Rate
    transaction_type = models.CharField(
        _('Transaction Type'),
        max_length=10,
        choices=TRANSACTION_TYPE,
        default='NEW',
    )
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
    appraised_value = models.DecimalField(
        _('Appraised Value'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    principal = models.DecimalField(
        _('Principal'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    additional_principal = models.DecimalField(
        _('Additional Principal'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False,
        default=0
    )
    promised_renewal_date = models.DateField(
        _('Promised Renewal Date'),
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
    on_hold = models.BooleanField(
        _('On Hold'),
        default=False
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
    matured = Matured()
    expired = Expired()

    def __str__(self):
        return f"{self.complete_description} by {self.client}"

    @property
    def complete_description(self):
        unit = 'pcs' if self.quantity > 1 else 'pc'
        description = f"{self.quantity}{unit}"
        if self.carat != 'Others':
            description += f" {self.carat}"
        if self.color != 'Others':
            description += f" {self.color}"
        if self.item_description != 'Others':
            description += f" {self.item_description}"
        if len(self.description) > 0:
            description += f" {self.description}"
        description += f" {self.grams}g"
        return description

    def getElapseDays(self):
        if self.transaction_type == 'NEW':
            return (timezone.now().date() - self.promised_renewal_date).days
        else:
            return (timezone.now().date() - self.date.date()).days

    def getInterestRate(self):
        elapsed = self.getElapseDays()
        rate = InterestRate.rates.get_rate(elapsed)
        return rate if rate else 0

    @staticmethod
    def advanceInterestRate(promise_date):
        elapsed = (promise_date - timezone.now().date()).days
        rate = AdvanceInterestRate.rates.get_rate(abs(elapsed))
        print(
            f"Promise Date: {promise_date}, Elapsed: {elapsed}, Rate: {rate}")
        return rate if rate else 0

    def getAdvanceInterestRate(self):
        return Pawn.advanceInterestRate(self.promised_renewal_date)

    def getInterest(self):
        interest = 0
        if self.transaction_type == 'EXISTING':
            interest = self.principal * \
                Decimal(str((self.getInterestRate() / 100)))
        return interest

    def getAdditionalInterest(self):
        ''' the additional interest is calculated when the pawn is renewed past the promised renewal date '''
        additional_interest = 0
        if self.transaction_type == 'NEW':
            interest = self.principal * \
                Decimal(
                    str((Pawn.advanceInterestRate(self.date.date()) / 100)))
            print(f"Interest: {interest}")
            print(f"Current Advance Interest: {self.advance_interest}")
            if interest > self.advance_interest:
                additional_interest = interest - self.advance_interest
        return additional_interest

    def getAdvanceInterest(self):
        return self.principal * Decimal(str((self.getAdvanceInterestRate() / 100)))

    def hasMatured(self):
        elapsed = (timezone.now().date() - self.date.date()).days
        return elapsed >= TermDuration.get_instance().maturity

    def get_maturity_date(self):
        return self.date.date() + timezone.timedelta(days=TermDuration.get_instance().maturity)

    def hasExpired(self):
        elapsed = (timezone.now().date() - self.date.date()).days
        return elapsed > TermDuration.get_instance().expiration

    def hasPenalty(self):
        elapsed = (timezone.now().date() - self.date.date()).days
        return elapsed > TermDuration.get_instance().maturity

    def getStanding(self):
        if self.hasExpired():
            return 'EXPIRED'
        if self.hasMatured():
            return 'MATURED'
        return 'ACTIVE'

    def getAuctionInterest(self):
        return self.principal * Decimal(4 * 0.04)

    def getPrincipalPlusAuctionInterest(self):
        return self.principal + self.getAuctionInterest()

    def getPenalty(self):
        if self.hasPenalty():
            daysPenalty = Decimal(
                str(self.getElapseDays() - TermDuration.get_instance().maturity))
            return self.principal * (InterestRate.rates.get_max_rate() / 100) * (daysPenalty / 30)
        return 0

    def getInterestPlusPenalty(self):
        return self.getInterest() + self.getPenalty()

    def getPrincipalPlusInterest(self):
        return self.principal + self.getInterest()

    def getTotalDue(self):
        return self.getPrincipalPlusInterest() + self.getPenalty() + self.getAdditionalInterest()

    def getRenewalServiceFee(self):
        return OtherFees.get_instance().service_fee

    def getMinimumPayment(self):
        otherFees = OtherFees.get_instance()
        service_charge = otherFees.service_fee
        adv_int = 0
        interest = 0
        if self.transaction_type == 'EXISTING':
            adv_int = self.getAdvanceInterest()
        else:
            interest = self.getInterest()
        return interest + self.getPenalty() + service_charge + adv_int

    def pay(self, post, cashier):
        amount_paid = Decimal(post.get('amtToPay'))
        otherFees = OtherFees.get_instance()
        paid_for_principal = Decimal(post.get('partial'))
        interest = self.getInterest()
        penalty = self.getPenalty()
        additional_principal = Decimal(post.get('additionalPrincipal', '0'))
        promised_date = None
        adv_interest_rate = 0
        adv_interest = 0
        if post.get('promised_renewal_date'):
            promised_date = timezone.datetime.strptime(
                post.get('promised_renewal_date'), '%Y-%m-%d').date()
            adv_interest_rate = Pawn.advanceInterestRate(promised_date)
            adv_interest = (self.principal - paid_for_principal +
                            additional_principal) * Decimal(adv_interest_rate / 100)
        service_fee = 0
        discounted = 0
        dr = DiscountRequests.objects.filter(pawn=self)

        if dr:
            discounted = dr.first().getApprovedDiscount()

        if amount_paid >= self.principal:
            self.status = 'REDEEMED'

        else:
            service_fee = otherFees.service_fee
            new_principal = self.principal - paid_for_principal + additional_principal
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
            new_pawn.appraised_value = self.appraised_value
            new_pawn.additional_principal = additional_principal
            new_pawn.promised_renewal_date = promised_date
            new_pawn.service_charge = service_fee
            new_pawn.advance_interest = adv_interest
            new_pawn.net_proceeds = new_principal - service_fee - adv_interest
            new_pawn.branch = self.branch
            new_pawn.status = 'ACTIVE'
            new_pawn.save()

            self.status = 'RENEWED'
            self.renewed_to = new_pawn

        self.status_updated_on = timezone.now()
        self.save()

        payment = Payment()
        payment.amount_paid = amount_paid
        payment.pawn = self
        payment.paid_interest = interest
        payment.penalty = penalty
        payment.service_fee = service_fee
        payment.advance_interest = adv_interest
        payment.cashier = cashier
        payment.paid_for_principal = paid_for_principal
        payment.discount_granted = discounted
        payment.save()

        # update daily cash position
        if self.status == 'RENEWED':
            self.update_cash_position_renew_ticket(
                cashier, 'Renewed pawn ticket', new_pawn
            )
        elif self.status == 'REDEEMED':
            self.update_receipts(
                cashier, 'Redeemed', amount_paid)

    def get_last_renewal_date(self):
        renewal = None
        if self.pawn_renewed_to:
            renewal = self.date
        return renewal

    def update_receipts(self, cashier, description, amount):
        cash_position, _ = DailyCashPosition.objects.get_or_create(
            branch=self.branch,
            date=timezone.now().date(),
            prepared_by=cashier
        )
        receipt, _ = AddReceipts.objects.get_or_create(
            daily_cash_position=cash_position,
            reference_number=self.pk
        )
        receipt.received_from = self.client.full_name
        receipt.particulars = description
        receipt.amount = amount
        receipt.automated = True
        receipt.save()
        return receipt

    def update_disbursements(self, cashier, description, amount):
        cash_position, _ = DailyCashPosition.objects.get_or_create(
            branch=self.branch,
            date=timezone.now().date(),
            prepared_by=cashier
        )
        disbursement, _ = LessDisbursements.objects.get_or_create(
            daily_cash_position=cash_position,
            reference_number=self.pk
        )
        disbursement.payee = self.client.full_name
        disbursement.particulars = description
        disbursement.amount = amount
        disbursement.automated = True
        disbursement.save()
        return disbursement

    def update_cash_position_new_ticket(self, cashier, description):
        receipt = None
        disbursement = None
        if self.transaction_type == 'NEW':
            receipt = self.update_receipts(
                cashier, description, self.advance_interest)
            d_amt = self.principal - self.service_charge
            disbursement = self.update_disbursements(
                cashier, description, d_amt)
        return (receipt, disbursement)

    def update_cash_position_renew_ticket(self, cashier, description, new_ticket):
        receipt = None
        disbursement = None
        total_interest = 0
        if self.transaction_type == 'NEW':
            total_interest = new_ticket.advance_interest
        else:
            total_interest = self.getInterest()

        r_amt = new_ticket.principal + total_interest
        receipt = self.update_receipts(
            cashier, description, r_amt)
        d_amt = new_ticket.principal - new_ticket.service_charge
        disbursement = self.update_disbursements(
            cashier, description, d_amt)
        return (receipt, disbursement)


class Payment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    pawn = models.OneToOneField(
        Pawn,
        on_delete=models.CASCADE,
        related_name='payment_pawn',
        null=False, blank=False
    )
    paid_interest = models.DecimalField(
        _('Paid Interest'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    penalty = models.DecimalField(
        _('Penalty'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    service_fee = models.DecimalField(
        _('Service Fee'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    advance_interest = models.DecimalField(
        _('Advance Interest'),
        max_digits=10,
        decimal_places=2,
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
    discount_granted = models.DecimalField(
        _('Discount Granted'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False,
        default=0
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
    interest_due = models.DecimalField(
        _('Interest Due'),
        max_digits=10,
        decimal_places=2,
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
        self.approved_on = timezone.now()
        self.save()

    def reject(self, employee):
        self.status = 'REJECTED'
        self.approved_by = employee
        self.approved_on = timezone.now()
        self.save()

    def getApprovedDiscount(self):
        return self.amount if self.status == 'APPROVED' else 0

    def __str__(self):
        return f"{self.pawn} - {self.amount} on {self.date}"

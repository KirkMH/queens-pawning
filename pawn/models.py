from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from simple_history.models import HistoricalRecords

from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal

from files.models import Client, Branch, InterestRate, AdvanceInterestRate, TermDuration, OtherFees
from access_hub.models import Employee
from reports.models import AddReceipts, DailyCashPosition, LessDisbursements


def to_date(value):
    if isinstance(value, datetime):
        return value.date()  # Convert datetime to date
    elif isinstance(value, date):
        return value  # It's already a date
    else:
        raise ValueError(
            "Input must be a datetime or date object. Received: '{}'".format(value))


def validate_date_granted(value):
    if value > timezone.now().date():
        raise ValidationError(_('Date granted cannot be in the future.'))


class Inventory(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='ACTIVE')


class Expired(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        expired_today = timezone.now().date(
        ) - timezone.timedelta(days=TermDuration.get_instance().expiration)
        return qs.filter(status='ACTIVE').filter(date_granted__lte=expired_today)


class Matured(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        matured_today = timezone.now().date(
        ) - timezone.timedelta(days=TermDuration.get_instance().maturity)
        return qs.filter(status='ACTIVE').filter(date_granted__lte=matured_today)


class Pawn(models.Model):
    ACTIVE = 'ACTIVE'
    RENEWED = 'RENEWED'
    REDEEMED = 'REDEEMED'
    AUCTIONED = 'AUCTIONED'
    CANCELLED = 'CANCELLED'
    STATUS = [
        (ACTIVE, _('Active')),
        (RENEWED, _('Renewed')),
        (REDEEMED, _('Redeemed')),
        (AUCTIONED, _('Auctioned')),
        (CANCELLED, _('Cancelled'))
    ]
    CARAT = [
        ('10k', '10k'),
        ('12k', '12k'),
        ('14k', '14k'),
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

    # NEW = Advance Interest Rate; EXISTING = Interest Rate
    transaction_type = models.CharField(
        _('Transaction Type'),
        max_length=10,
        choices=TRANSACTION_TYPE,
        default='NEW',
    )
    pawn_ticket_number = models.CharField(
        _('Pawn Ticket Number'),
        max_length=20,
        null=True, blank=True
    )
    date_encoded = models.DateField(_("Date encoded"), auto_now_add=True)
    date_granted = models.DateField(
        _("Date granted"),
        null=True, blank=True,
        validators=[validate_date_granted]
    )
    renew_redeem_date = models.DateField(
        _("Renew/Redeem Date"),
        null=True, blank=True
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
        null=True, blank=True
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
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    objects = models.Manager()
    history = HistoricalRecords()
    inventory = Inventory()
    matured = Matured()
    expired = Expired()

    def __str__(self):
        return f"{self.getPTN}: {self.client} - {self.complete_description}"

    @property
    def getPTN(self):
        if self.pawn_ticket_number:
            return f"{self.pawn_ticket_number}"
        else:
            return f"{self.id:06d}"

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

    @property
    def expiration_date(self):
        expiration_days = TermDuration.get_instance().expiration
        return self.date_granted + timezone.timedelta(days=expiration_days)

    def getElapseDays(self):
        self.update_renew_redeem_date()
        rrd = to_date(self.renew_redeem_date)
        

        # if self.transaction_type == 'NEW':
        #     return (rrd - to_date(self.promised_renewal_date)).days if self.promised_renewal_date else 0
        # else:
        return (rrd - to_date(self.date_granted)).days

    def getInterestRate(self):
        elapsed = self.getElapseDays()
        rate = InterestRate.rates.get_rate(elapsed)
        print(f"Elapsed: {elapsed}, Rate: {rate}")
        return rate if rate else 0

    @staticmethod
    def advanceInterestRate(promise_date, date_granted=None):
        elapsed = 0
        date_granted = timezone.now().date() if date_granted is None else date_granted
        if promise_date:
            elapsed = abs((promise_date - date_granted).days)
        rate = AdvanceInterestRate.rates.get_rate(abs(elapsed))
        print(
            f"Promise Date: {promise_date}, Elapsed: {elapsed}, Rate: {rate}")
        return rate if rate else 0

    def getAdvanceInterestRate(self):
        return Pawn.advanceInterestRate(self.promised_renewal_date, self.date_granted)

    def getInterest(self):
        # interest = 0
        # if self.transaction_type == 'EXISTING':
        interest = self.principal * \
            Decimal(str((self.getInterestRate() / 100)))
        # if self.transaction_type == 'NEW':  # and interest >= self.advance_interest:
        #     interest = 0
        return interest

    def getAdditionalInterest(self):
        ''' the additional interest is calculated when the pawn is renewed past the promised renewal date '''
        additional_interest = 0
        # if self.transaction_type == 'NEW':
        #     interest = self.principal * \
        #         Decimal(
        #             str((Pawn.advanceInterestRate(self.promised_renewal_date, self.date_granted) / 100)))
        #     print(f"Interest: {interest}")
        #     print(f"Current Advance Interest: {self.advance_interest}")
        #     if interest > self.advance_interest:
        #         additional_interest = interest - self.advance_interest
        return additional_interest

    def getAdvanceInterest(self):
        return 0 #self.principal * Decimal(str((self.getAdvanceInterestRate() / 100)))

    def hasMatured(self):
        elapsed = (timezone.now().date() - self.date_granted).days
        return elapsed >= TermDuration.get_instance().maturity

    def get_maturity_date(self):
        return self.date_granted + timezone.timedelta(days=TermDuration.get_instance().maturity)

    def hasExpired(self):
        elapsed = (timezone.now().date() - self.date_granted).days
        print(f"Elapsed: {elapsed}")
        return elapsed > TermDuration.get_instance().expiration

    def hasPenalty(self):
        elapsed = (to_date(self.renew_redeem_date) -
                   to_date(self.date_granted)).days
        return elapsed > TermDuration.get_instance().maturity

    def getStanding(self):
        if self.status == 'ACTIVE':
            if self.hasExpired():
                return 'EXPIRED'
            if self.hasMatured():
                return 'MATURED'
        return self.status

    def getAuctionInterest(self):
        return self.principal * Decimal(4 * 0.04)

    def getPrincipalPlusAuctionInterest(self):
        return self.principal + self.getAuctionInterest()

    def getPenalty(self):
        if self.hasPenalty():
            daysPenalty = self.getElapseDays()
            if self.transaction_type == 'EXISTING':
                daysPenalty = Decimal(
                    str(self.getElapseDays() - TermDuration.get_instance().maturity))
            print(f"Days Penalty: {daysPenalty}")
            other_fees = OtherFees.get_instance()
            deferred_fields = other_fees.get_deferred_fields()
            if 'penalty_rate' in deferred_fields:
                other_fees.refresh_from_db(fields=['penalty_rate'])
            penalty_rate = other_fees.penalty_rate
            penalty = abs(self.principal * Decimal(penalty_rate / 100)
                          * Decimal(daysPenalty / 30))

            print(f"Penalty Rate: {penalty_rate}")
            print(f"Penalty: {penalty}")

            return penalty
        return 0

    def getInterestPlusPenalty(self):
        interest = self.getInterest()
        penalty = self.getPenalty()
        addInt = self.getAdditionalInterest()
        print(
            f"Interest: {interest}, Penalty: {penalty}, Additional Interest: {addInt}")
        return interest + penalty + addInt

    def getPrincipalPlusInterest(self):
        return self.principal + self.getInterest()

    def getTotalDue(self):
        return self.getPrincipalPlusInterest() + self.getPenalty() + self.getAdditionalInterest()

    def getMinTotalDue(self):
        return self.getInterest() + self.getPenalty() + self.getAdditionalInterest()

    def getRenewalServiceFee(self):
        return OtherFees.get_instance().service_fee

    def getMinimumPayment(self):
        otherFees = OtherFees.get_instance()
        service_charge = otherFees.service_fee
        adv_int = 0
        interest = 0
        # if self.transaction_type == 'NEw':
        #     adv_int = self.getAdvanceInterest()
        # else:
        interest = self.getInterest()
        return interest + self.getPenalty() + service_charge + adv_int + self.getAdditionalInterest()

    def pay(self, post, cashier):
        new_ptn = post.get('new_ptn')
        amount_paid = Decimal(post.get('amtToPay'))
        otherFees = OtherFees.get_instance()
        paid_for_principal = Decimal(post.get('partial', '0'))
        interest = self.getInterest()
        penalty = self.getPenalty()
        additional_principal = Decimal(post.get('additionalPrincipal', '0'))
        promised_date = None
        adv_interest_rate = 0
        adv_interest = 0
        if post.get('promised_renewal_date'):
            promised_date = timezone.datetime.strptime(
                post.get('promised_renewal_date'), '%Y-%m-%d').date()
            adv_interest_rate = Pawn.advanceInterestRate(
                promised_date, self.date_granted)
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
            new_pawn.transaction_type = self.transaction_type
            new_pawn.date_granted = self.renew_redeem_date
            new_pawn.client = self.client
            new_pawn.pawn_ticket_number = new_ptn
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

        self.update_payment(
            cashier, service_fee, adv_interest, amount_paid, interest, penalty, paid_for_principal, discounted)

        # update daily cash position
        if self.status == 'RENEWED':
            self.update_cash_position_renew_ticket(
                cashier, 'Renewed pawn ticket', new_pawn, new_entry=False
            )
        elif self.status == 'REDEEMED':
            self.update_receipts(
                cashier, 'Redeemed', amount_paid, new_entry=True)

    def update_payment(self, cashier, service_fee, advance_interest, amount_paid=0, paid_interest=0, penalty=0, paid_for_principal=0, discount_granted=0):
        created = False
        payment = Payment.objects.filter(pawn=self).first()
        if (payment is None):
            payment, created = Payment.objects.get_or_create(
                pawn=self, cashier=cashier)

        payment.payment_date = self.renew_redeem_date
        payment.amount_paid = amount_paid
        payment.paid_interest = paid_interest
        payment.penalty = penalty
        payment.service_fee = service_fee
        payment.advance_interest = advance_interest
        payment.cashier = cashier
        payment.paid_for_principal = paid_for_principal
        payment.discount_granted = discount_granted
        payment.save()
        stat = 'created' if created else 'updated'
        print(f'payment record {stat}: {payment}')

    def get_last_renewal_date(self):
        renewal = None
        if self.pawn_renewed_to:
            renewal = self.date_granted
        return renewal

    def update_receipts(self, cashier, description, amount, new_entry=True, ticket=None):
        ticket = self if ticket is None else ticket
        receipt = None
        date = ticket.date_granted
        if description == "Redeemed" and self.renew_redeem_date is not None:
            date = self.renew_redeem_date
        print(f'new entry? {new_entry}')
        print(f'date: {date}')
        print(f'ticket: {ticket}')
        
        receipts = AddReceipts.objects.filter(
            pawn=ticket
        )
        if receipts.exists():
            receipts.delete()
        
        cash_position, created = DailyCashPosition.objects.get_or_create(
            branch=ticket.branch,
            date=date
        )
        print(f'cash position created? {created}')
        print(f'cash position: {cash_position}')
        receipt, created = AddReceipts.objects.get_or_create(
            daily_cash_position=cash_position,
            pawn=ticket
        )
        print(f'receipt created? {created}')
        print(f'receipt: {receipt}')
        if new_entry:
            cash_position.prepared_by = cashier
            cash_position.save()

        receipt.reference_number = ticket.getPTN
        receipt.received_from = ticket.client.full_name
        receipt.particulars = description
        receipt.amount = amount
        receipt.automated = True
        receipt.save()
        print(f'Receipt amount set to: {receipt.amount}')
        return receipt

    def update_disbursements(self, cashier, description, amount, new_entry=True, ticket=None):
        ticket = self if ticket is None else ticket
        disbursement = None
        date = ticket.date_granted
        disbursements = LessDisbursements.objects.filter(
            pawn=ticket
        )
        if disbursements.exists():
            disbursements.delete()
        cash_position, created = DailyCashPosition.objects.get_or_create(
            branch=self.branch,
            date=date
        )
        print(f'disbursement new entry? {new_entry}')
        print(f'date: {date}')
        print(f'ticket: {ticket}')
        print(f'cash position created? {created}')
        print(f'cash position: {cash_position}')
        disbursement, created = LessDisbursements.objects.get_or_create(
            daily_cash_position=cash_position,
            pawn=ticket
        )
        print(f'disbursement created? {created}')
        print(f'disbursement: {disbursement}')
        if new_entry:
            cash_position.prepared_by = cashier
            cash_position.save()

        disbursement.reference_number = ticket.getPTN
        disbursement.payee = ticket.client.full_name
        disbursement.particulars = description
        disbursement.amount = amount
        disbursement.automated = True
        disbursement.save()
        print(f'Disbursement amount set to: {disbursement.amount}')
        return disbursement

    def update_cash_position_new_ticket(self, cashier, description, new_entry=True):
        return self.update_cash_position_renew_ticket(cashier, description, self, new_entry)

    def update_cash_position_renew_ticket(self, cashier, description, new_ticket, new_entry=True):
        receipt = None
        disbursement = None
        total_interest = self.getInterest()

        # RECEIPT: new -- interest only; renew -- old principal + interest + penalty
        if self.renewed_to:
            r_amt = self.principal + total_interest + self.getPenalty()
        else:
            r_amt = self.service_charge # total_interest
        receipt = self.update_receipts(
            cashier, description, r_amt, new_entry, new_ticket)
        d_amt = new_ticket.principal - new_ticket.service_charge
        disbursement = self.update_disbursements(
            cashier, description, d_amt, new_entry, new_ticket)
        return (receipt, disbursement)

    def is_pawned_today(self):
        return self.date_granted == timezone.now().date()

    def is_encoded_today(self):
        return self.date_encoded == timezone.now().date()

    def renewed_from(self):
        mother = Pawn.objects.filter(
            renewed_to=self).first()
        print(f"Mother ticket: {mother}")
        return mother

    def is_pawn_edittable(self):
        return self.renewed_from is None and self.payment_pawn is None and (
            self.request.user.employee.branch is None or self.is_encoded_today()
        )

    def is_voidable(self):
        return self.status in ['REDEEMED', 'AUCTIONED']

    def update_renew_redeem_date(self, date=None):
        if self.status == 'ACTIVE':
            if date is not None:
                self.renew_redeem_date = date
            elif self.renew_redeem_date is None:
                self.renew_redeem_date = timezone.now()
            self.save()
            print(f'updated renew_redeem_date: {self.renew_redeem_date}')

    def auction(self):
        self.status = 'AUCTIONED'
        self.status_updated_on = timezone.now()
        self.save()

    def reset_status(self):
        self.renewed_to = None
        self.renew_redeem_date = None
        self.status = 'ACTIVE'
        self.status_updated_on = timezone.now()
        self.save()


class Payment(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateField(null=True, blank=True)
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
        default=0
    )
    penalty = models.DecimalField(
        _('Penalty'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    service_fee = models.DecimalField(
        _('Service Fee'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    advance_interest = models.DecimalField(
        _('Advance Interest'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    amount_paid = models.DecimalField(
        _('Amount Paid'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    paid_for_principal = models.DecimalField(
        _('Paid for Principal'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    discount_granted = models.DecimalField(
        _('Discount Granted'),
        max_digits=10,
        decimal_places=2,
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

    class Meta:
        ordering = ['-pawn__pk']


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

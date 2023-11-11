from django.db import models
from django.utils.translation import gettext_lazy as _


# will be used for the status of different models
ACTIVE = 'ACTIVE'
CANCELLED = 'CANCELLED'
STATUS = [
    (ACTIVE, _('Active')),
    (CANCELLED, _('Cancelled'))
]


class Client(models.Model):
    MR = 'MR'
    MS = 'MS'
    TITLES = [
        (MR, _(MR)),
        (MS, _(MS))
    ]
    title = models.CharField(
        _('Title'),
        max_length=2,
        choices=TITLES,
        default=MS,
        null=False, blank=False
    )
    last_name = models.CharField(
        _('Last Name'),
        max_length=20,
        null=False, blank=False
    )
    first_name = models.CharField(
        _('First Name'),
        max_length=20,
        null=False, blank=False
    )
    middle_name = models.CharField(
        _('Middle Name'),
        max_length=20
    )
    address = models.CharField(
        _('Address'),
        max_length=50,
        null=False, blank=False
    )
    id_presented = models.CharField(
        _('ID Presented'),
        max_length=20,
        null=False, blank=False
    )
    id_number = models.CharField(
        _('ID Number'),
        max_length=20,
        null=False, blank=False
    )
    contact_num = models.CharField(
        _('Contact Number'),
        max_length=20,
        null=False, blank=False
    )
    date_registered = models.DateField(
        _('Date Registered'),
        auto_now_add=True
    )
    status = models.CharField(
        _("Status"),
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )
    # NOTE: should the branch where the client was registered matter?

    def __str__(self):
        return self.full_name()

    @property
    def full_name(self):
        return f'{self.title} {self.last_name}, {self.first_name} {self.middle_name}'

    @property
    def id_info(self):
        return f'{self.id_presented}-{self.id_number}'

    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name']
        unique_together = ['last_name', 'first_name', 'middle_name']


class InterestRate(models.Model):
    interest_rate = models.PositiveSmallIntegerField(
        _('Interest Rate'),
        null=False, blank=False
    )
    min_day = models.PositiveSmallIntegerField(
        _('Minimum Days'),
        null=False, blank=False
    )
    max_day = models.PositiveSmallIntegerField(
        _('Maximum Days'),
        null=False, blank=False
    )
    approval_required = models.BooleanField(
        _('Approval required?'),
        default=False
    )

    def __str__(self):
        return f'{self.min_day} - {self.max_day} days: {self.interest_rate}%'

    class Meta:
        ordering = ['min_day']


class ServiceFee(models.Model):
    fee = models.DecimalField(
        _('Service Fee'),
        max_digits=6,
        decimal_places=2
    )
    effectivity = models.DateField(
        _('Effectivity Date')
    )

    def __str__(self):
        return str(self.fee)

    class Meta:
        ordering = ['-effectivity']


class AdvanceInterestRate(models.Model):
    rate = models.PositiveSmallIntegerField(
        _('Advance Interest Rate')
    )
    effectivity = models.DateField(
        _('Effectivity Date')
    )

    def __str__(self):
        return str(self.rate)

    class Meta:
        ordering = ['-effectivity']


class Maturity(models.Model):
    days = models.PositiveSmallIntegerField(
        _('Days to Maturity')
    )
    effectivity = models.DateField(
        _('Effectivity Date')
    )

    def __str__(self):
        return str(self.days)

    class Meta:
        ordering = ['-effectivity']


class Expiration(models.Model):
    days = models.PositiveSmallIntegerField(
        _('Days to Expiration')
    )
    effectivity = models.DateField(
        _('Effectivity Date')
    )

    def __str__(self):
        return str(self.days)

    class Meta:
        ordering = ['-effectivity']


class ExpenseCategory(models.Model):
    category = models.CharField(
        _('Category'),
        max_length=20,
        unique=True,
        null=False, blank=False
    )
    status = models.CharField(
        _("Status"),
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )

    def __str__(self):
        return self.category

    class Meta:
        ordering = ['category']


class Branch(models.Model):
    name = models.CharField(
        _('Branch Name'),
        max_length=30,
        unique=True,
        null=False, blank=False
    )
    address = models.CharField(
        _('Address'),
        max_length=50,
        null=False, blank=False
    )
    vat_info = models.CharField(
        _('VAT Information'),
        max_length=30,
        null=False, blank=False
    )
    contact_num = models.CharField(
        _('Contact Number'),
        max_length=20,
        null=False, blank=False
    )
    days_open = models.CharField(
        _('Days Open'),
        max_length=20
    )
    status = models.CharField(
        _("Status"),
        max_length=10,
        choices=STATUS,
        default=ACTIVE
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

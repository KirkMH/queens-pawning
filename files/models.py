from django.db import models
from django.utils.translation import gettext_lazy as _


# will be used for the status of different models
ACTIVE = 'ACTIVE'
CANCELLED = 'CANCELLED'
STATUS = [
    (ACTIVE, _('Active')),
    (CANCELLED, _('Cancelled'))
]

# list of valid


class ValidId(models.Model):
    type = models.CharField(
        _('ID Type'),
        max_length=50,
        null=False, blank=False
    )

    def __str__(self) -> str:
        return self.type

    class Meta:
        ordering = ['type']
        verbose_name = 'Valid ID'
        verbose_name_plural = 'Valid IDs'


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
    id_link = models.ForeignKey(
        ValidId,
        verbose_name=_('Presented ID'),
        on_delete=models.CASCADE,
        related_name='presenters',
        null=True, blank=True
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
    branch = models.ForeignKey(
        "Branch",
        on_delete=models.CASCADE,
        related_name='clients',
        null=True, blank=True
    )

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f'{self.title} {self.last_name}, {self.first_name} {self.middle_name}'

    @property
    def id_info(self):
        return f'{self.id_presented}-{self.id_number}'

    class Meta:
        ordering = ['last_name', 'first_name', 'middle_name']
        unique_together = ['last_name', 'first_name', 'middle_name']


class InterestRateManager(models.Manager):
    def get_rate(self, elapsed_days):
        # Get the interest rate for the given number of elapsed days
        try:
            rate = self.filter(min_day__lte=elapsed_days).order_by(
                '-interest_rate').first()
            return rate.interest_rate if rate else None
        except InterestRate.DoesNotExist:
            return None

    def get_max_rate(self):
        # Get the maximum interest rate
        try:
            rate = self.order_by('-interest_rate').first()
            return rate.interest_rate if rate else None
        except InterestRate.DoesNotExist:
            return None


class InterestRate(models.Model):
    interest_rate = models.PositiveSmallIntegerField(
        _('Interest Rate'),
        null=False, blank=False
    )
    min_day = models.PositiveSmallIntegerField(
        _('Minimum Days'),
        null=False, blank=False
    )

    objects = models.Manager()
    rates = InterestRateManager()

    def __str__(self):
        return f'From {self.min_day} days: {self.interest_rate}%'

    class Meta:
        ordering = ['min_day']


class OtherFees(models.Model):
    service_fee = models.DecimalField(
        _('Service Fee'),
        max_digits=6,
        decimal_places=2,
        default=0
    )
    advance_interest_rate = models.PositiveSmallIntegerField(
        _('Advance Interest Rate (in percent)'),
        default=0
    )

    @classmethod
    def get_instance(self):
        # Assuming only one instance exists
        instance, _ = self.objects.get_or_create(pk=1)
        return instance

    def __str__(self):
        return f'Service Fee: {self.service_fee} | Advance Interest Rate: {self.advance_interest_rate}%'


class TermDuration(models.Model):
    maturity = models.PositiveSmallIntegerField(
        _('Days before Maturity'),
        default=0
    )
    expiration = models.PositiveSmallIntegerField(
        _('Days before Expiration'),
        default=0
    )

    @classmethod
    def get_instance(self):
        # Assuming only one instance exists
        instance, _ = self.objects.get_or_create(pk=1)
        return instance

    def __str__(self):
        return f'Maturity: {self.maturity} days | Expiration: {self.expiration} days'


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
        verbose_name_plural = 'Expense categories'


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
        max_length=50
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
        verbose_name_plural = 'Branches'

from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from files.models import Client


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
    description = models.CharField(
        _('Description'),
        max_length=255,
        null=False, blank=False
    )
    principal = models.DecimalField(
        _('Principal'),
        max_digits=10,
        decimal_places=2,
        null=False, blank=False
    )
    service_charge = models.DecimalField(
        _('Service Charge'),
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
    status_updated_on = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()
    Inventory = Inventory()

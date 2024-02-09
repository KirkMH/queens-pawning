from django.contrib import admin

from .models import *


class PawnAdmin(admin.ModelAdmin):
    list_display = ('description', 'client', 'date',
                    'principal', 'net_proceeds', 'branch', 'status')


admin.site.register(Pawn, PawnAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('pawn', 'date', 'amount_paid',
                    'paid_for_principal', 'cashier')


admin.site.register(Payment, PaymentAdmin)

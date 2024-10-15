from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Employee
from pawn.models import Pawn
from reports.models import LessDisbursements, AddReceipts


admin.site.site_header = "Queen's Jewelry and Pawnshop"
admin.site.site_title = 'Administrator'
admin.site.index_title = 'System Administrator'


# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = "Employees"


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [EmployeeInline]
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (('Permissions'), {
         'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    class Media:
        js = ('js/employee-admin.js',)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# register Pawn in a tabular format


class PawnAdmin(admin.ModelAdmin):
    list_display = ('PTN', 'date_granted', 'client', 'complete_description',
                    'principal', 'net_proceeds', 'status', 'branch')  # display columns

    def PTN(self, pawn):
        return pawn.getPTN

    def complete_description(self, pawn):
        return pawn.complete_description


admin.site.register(Pawn, PawnAdmin)


class LessDisbursementsAdmin(admin.ModelAdmin):
    list_display = ('PTN', 'date_granted', 'client', 'complete_description',
                    'payee', 'particulars', 'amount')  # display columns

    def date_granted(self, less_disbursements):
        return less_disbursements.pawn.date_granted if less_disbursements.pawn else None

    def client(self, less_disbursements):
        return less_disbursements.pawn.client if less_disbursements.pawn else None

    def PTN(self, less_disbursements):
        return less_disbursements.pawn.getPTN if less_disbursements.pawn else f" Ref: {less_disbursements.reference_number}" if less_disbursements.reference_number else "(None)"

    def complete_description(self, less_disbursements):
        return less_disbursements.pawn.complete_description if less_disbursements.pawn else None


admin.site.register(LessDisbursements, LessDisbursementsAdmin)


class AddReceiptsAdmin(admin.ModelAdmin):
    list_display = ('PTN', 'date_granted', 'client', 'complete_description',
                    'received_from', 'particulars', 'amount')  # display columns

    def date_granted(self, add_receipts):
        return add_receipts.pawn.date_granted if add_receipts.pawn else None

    def client(self, add_receipts):
        return add_receipts.pawn.client if add_receipts.pawn else None

    def PTN(self, add_receipts):
        return add_receipts.pawn.getPTN if add_receipts.pawn else f" Ref: {add_receipts.reference_number}" if add_receipts.reference_number else "(None)"

    def complete_description(self, add_receipts):
        return add_receipts.pawn.complete_description if add_receipts.pawn else None


admin.site.register(AddReceipts, AddReceiptsAdmin)

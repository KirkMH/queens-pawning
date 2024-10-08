from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Employee
from pawn.models import Pawn


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

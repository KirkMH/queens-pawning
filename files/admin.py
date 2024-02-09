from django.contrib import admin
from django.contrib.auth.models import Group
from .models import *

admin.site.register(Client)
admin.site.register(ExpenseCategory)
admin.site.register(Branch)

# remove Group
admin.site.unregister(Group)

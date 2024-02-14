from django.contrib import admin
from django.contrib.auth.models import Group

from .models import *
from .forms import AdminClientForm

# make the id_link required


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = AdminClientForm


admin.site.register(Branch)
admin.site.register(ValidId)

# remove Group
admin.site.unregister(Group)

from django.db import models

from django.contrib.auth.models import User

from files.models import Branch


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(
        Branch, on_delete=models.CASCADE, related_name='employees')

    def __str__(self):
        return f"{self.user.username}'s Assigned Branch: {self.branch}"

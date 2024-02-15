from django.db import models

from django.contrib.auth.models import User

from files.models import Branch


USER_TYPES = (
    (1, 'Cashier'),
    (2, 'Staff'),
    (3, 'Expense Personnel'),
    (4, 'Administrator')
)


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='employees',
        null=True, blank=True
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPES, default=2)

    def __str__(self):
        return f"{self.user.username}'s Assigned Branch: {self.branch}"

# Generated by Django 4.0 on 2024-12-01 05:15

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0015_alter_expense_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='date',
            field=models.DateField(validators=[django.core.validators.MaxValueValidator(datetime.date(2024, 12, 1))]),
        ),
    ]

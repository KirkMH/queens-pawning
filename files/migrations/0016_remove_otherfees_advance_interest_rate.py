# Generated by Django 4.0 on 2024-05-07 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0015_advanceinterestrate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otherfees',
            name='advance_interest_rate',
        ),
    ]

# Generated by Django 4.0 on 2023-12-06 02:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0007_remove_interestrate_max_day'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interestrate',
            options={'ordering': ['approval_required', 'min_day']},
        ),
    ]

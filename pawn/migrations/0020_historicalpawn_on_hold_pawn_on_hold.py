# Generated by Django 4.0 on 2024-05-20 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pawn', '0019_payment_discount_granted'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpawn',
            name='on_hold',
            field=models.BooleanField(default=False, verbose_name='On Hold'),
        ),
        migrations.AddField(
            model_name='pawn',
            name='on_hold',
            field=models.BooleanField(default=False, verbose_name='On Hold'),
        ),
    ]
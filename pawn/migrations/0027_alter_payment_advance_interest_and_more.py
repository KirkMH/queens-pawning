# Generated by Django 4.0 on 2024-10-29 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pawn', '0026_alter_pawn_renewed_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='advance_interest',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Advance Interest'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Amount Paid'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='paid_for_principal',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Paid for Principal'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='paid_interest',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Paid Interest'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='penalty',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Penalty'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='service_fee',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Service Fee'),
        ),
    ]
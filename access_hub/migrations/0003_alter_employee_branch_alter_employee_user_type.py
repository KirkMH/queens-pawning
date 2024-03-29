# Generated by Django 4.0 on 2024-02-15 07:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0014_client_id_number'),
        ('access_hub', '0002_employee_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='branch',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='files.branch'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='user_type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Cashier'), (2, 'Staff'), (3, 'Expense Personnel'), (4, 'Administrator')], default=2),
        ),
    ]

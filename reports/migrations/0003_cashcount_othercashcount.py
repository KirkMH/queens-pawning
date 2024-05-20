# Generated by Django 4.0 on 2024-05-20 06:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('access_hub', '0003_alter_employee_branch_alter_employee_user_type'),
        ('files', '0016_remove_otherfees_advance_interest_rate'),
        ('reports', '0002_alter_dailycashposition_balance_cib_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('one_thousands', models.IntegerField(default=0)),
                ('five_hundreds', models.IntegerField(default=0)),
                ('two_hundreds', models.IntegerField(default=0)),
                ('one_hundreds', models.IntegerField(default=0)),
                ('fifties', models.IntegerField(default=0)),
                ('twenties', models.IntegerField(default=0)),
                ('tens', models.IntegerField(default=0)),
                ('fives', models.IntegerField(default=0)),
                ('coins', models.IntegerField(default=0)),
                ('coins_total', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_counts', to='files.branch')),
                ('prepared_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_counts', to='access_hub.employee')),
            ],
        ),
        migrations.CreateModel(
            name='OtherCashCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('particulars', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cash_count', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='other_cash_counts', to='reports.cashcount')),
            ],
        ),
    ]

# Generated by Django 4.0 on 2023-11-08 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdvanceInterestRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.PositiveSmallIntegerField(verbose_name='Advance Interest Rate')),
                ('effectivity', models.DateField(verbose_name='Effectivity Date')),
            ],
            options={
                'ordering': ['-effectivity'],
            },
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, verbose_name='Branch Name')),
                ('address', models.CharField(max_length=50, verbose_name='Address')),
                ('vat_info', models.CharField(max_length=30, verbose_name='VAT Information')),
                ('contact_num', models.CharField(max_length=20, verbose_name='Contact Number')),
                ('days_open', models.CharField(max_length=20, verbose_name='Days Open')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('CANCELLED', 'Cancelled')], default='ACTIVE', max_length=10, verbose_name='Status')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(choices=[('MR', 'MR'), ('MS', 'MS')], default='MS', max_length=2, verbose_name='Title')),
                ('last_name', models.CharField(max_length=20, verbose_name='Last Name')),
                ('first_name', models.CharField(max_length=20, verbose_name='First Name')),
                ('middle_name', models.CharField(max_length=20, verbose_name='Middle Name')),
                ('address', models.CharField(max_length=50, verbose_name='Address')),
                ('id_presented', models.CharField(max_length=20, verbose_name='ID Presented')),
                ('id_number', models.CharField(max_length=20, verbose_name='ID Number')),
                ('contact_num', models.CharField(max_length=20, verbose_name='Contact Number')),
                ('date_registered', models.DateField(auto_now_add=True, verbose_name='Date Registered')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('CANCELLED', 'Cancelled')], default='ACTIVE', max_length=10, verbose_name='Status')),
            ],
            options={
                'ordering': ['last_name', 'first_name', 'middle_name'],
            },
        ),
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=20, verbose_name='Category')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('CANCELLED', 'Cancelled')], default='ACTIVE', max_length=10, verbose_name='Status')),
            ],
            options={
                'ordering': ['category'],
            },
        ),
        migrations.CreateModel(
            name='Expiration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.PositiveSmallIntegerField(verbose_name='Days to Expiration')),
                ('effectivity', models.DateField(verbose_name='Effectivity Date')),
            ],
            options={
                'ordering': ['-effectivity'],
            },
        ),
        migrations.CreateModel(
            name='InterestRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interest_rate', models.PositiveSmallIntegerField(verbose_name='Interest Rate')),
                ('min_day', models.PositiveSmallIntegerField(verbose_name='Minimum Days')),
                ('max_day', models.PositiveSmallIntegerField(verbose_name='Maximum Days')),
                ('approval_required', models.BooleanField(default=False, verbose_name='Approval required?')),
            ],
            options={
                'ordering': ['min_day'],
            },
        ),
        migrations.CreateModel(
            name='Maturity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.PositiveSmallIntegerField(verbose_name='Days to Maturity')),
                ('effectivity', models.DateField(verbose_name='Effectivity Date')),
            ],
            options={
                'ordering': ['-effectivity'],
            },
        ),
        migrations.CreateModel(
            name='ServiceFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Service Fee')),
                ('effectivity', models.DateField(verbose_name='Effectivity Date')),
            ],
            options={
                'ordering': ['-effectivity'],
            },
        ),
    ]

# Generated by Django 4.0 on 2024-01-23 02:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0008_alter_interestrate_options'),
        ('pawn', '0004_alter_historicalpawn_status_updated_on_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpawn',
            name='advance_interest',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='LESS: Advance Interest'),
        ),
        migrations.AlterField(
            model_name='historicalpawn',
            name='service_charge',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='LESS: Service Charge'),
        ),
        migrations.AlterField(
            model_name='pawn',
            name='advance_interest',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='LESS: Advance Interest'),
        ),
        migrations.AlterField(
            model_name='pawn',
            name='service_charge',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='LESS: Service Charge'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount Paid')),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Balance')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='files.client')),
                ('pawn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pawn.pawn')),
            ],
        ),
    ]
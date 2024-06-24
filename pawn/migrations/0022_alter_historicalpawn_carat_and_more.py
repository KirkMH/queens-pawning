# Generated by Django 4.0 on 2024-06-21 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pawn', '0021_remove_historicalpawn_date_remove_pawn_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpawn',
            name='carat',
            field=models.CharField(choices=[('10k', '10k'), ('12k', '12k'), ('14k', '14k'), ('18k', '18k'), ('21k', '21k'), ('24k', '24k'), ('Others', 'Others, specify in description')], max_length=10, verbose_name='Carat'),
        ),
        migrations.AlterField(
            model_name='historicalpawn',
            name='promised_renewal_date',
            field=models.DateField(blank=True, null=True, verbose_name='Promised Renewal Date'),
        ),
        migrations.AlterField(
            model_name='pawn',
            name='carat',
            field=models.CharField(choices=[('10k', '10k'), ('12k', '12k'), ('14k', '14k'), ('18k', '18k'), ('21k', '21k'), ('24k', '24k'), ('Others', 'Others, specify in description')], max_length=10, verbose_name='Carat'),
        ),
        migrations.AlterField(
            model_name='pawn',
            name='promised_renewal_date',
            field=models.DateField(blank=True, null=True, verbose_name='Promised Renewal Date'),
        ),
    ]

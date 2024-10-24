# Generated by Django 4.0 on 2024-10-16 00:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pawn', '0025_alter_historicalpawn_date_granted_and_more'),
        ('reports', '0007_alter_cashcount_prepared_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='addreceipts',
            name='pawn',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='pawn.pawn'),
        ),
        migrations.AddField(
            model_name='lessdisbursements',
            name='pawn',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disbursements', to='pawn.pawn'),
        ),
    ]

# Generated by Django 4.0 on 2024-03-29 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pawn', '0015_payment_advance_interest_payment_paid_interest_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpawn',
            name='carat',
            field=models.CharField(choices=[('10k', '10k'), ('12k', '12k'), ('18k', '18k'), ('21k', '21k'), ('24k', '24k'), ('Others', 'Others, specify in description')], max_length=10, verbose_name='Carat'),
        ),
        migrations.AlterField(
            model_name='historicalpawn',
            name='color',
            field=models.CharField(choices=[('White Gold', 'White Gold'), ('Yellow Gold', 'Yellow Gold'), ('Rose Gold', 'Rose Gold'), ('Saudi Gold', 'Saudi Gold'), ('Japan Gold', 'Japan Gold'), ('Tri-Color', 'Tri-Color'), ('Others', 'Others, specify in description')], max_length=20, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='historicalpawn',
            name='item_description',
            field=models.CharField(choices=[('Anklet', 'Anklet'), ('Bangle', 'Bangle'), ('Bracelet', 'Bracelet'), ('Stud Earrings', 'Stud Earrings'), ('Loop Earrings', 'Loop Earrings'), ('Clip Earrings', 'Clip Earrings'), ('Stud Earrings', 'Stud Earrings'), ('Dangling Earrings', 'Dangling Earrings'), ('Ring', 'Ring'), ('Wedding Ring', 'Wedding Ring'), ('Necklace', 'Necklace'), ('Pendant', 'Pendant'), ('Others', 'Others, specify in description')], max_length=20, verbose_name='Item Description'),
        ),
        migrations.AlterField(
            model_name='pawn',
            name='carat',
            field=models.CharField(choices=[('10k', '10k'), ('12k', '12k'), ('18k', '18k'), ('21k', '21k'), ('24k', '24k'), ('Others', 'Others, specify in description')], max_length=10, verbose_name='Carat'),
        ),
        migrations.AlterField(
            model_name='pawn',
            name='color',
            field=models.CharField(choices=[('White Gold', 'White Gold'), ('Yellow Gold', 'Yellow Gold'), ('Rose Gold', 'Rose Gold'), ('Saudi Gold', 'Saudi Gold'), ('Japan Gold', 'Japan Gold'), ('Tri-Color', 'Tri-Color'), ('Others', 'Others, specify in description')], max_length=20, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='pawn',
            name='item_description',
            field=models.CharField(choices=[('Anklet', 'Anklet'), ('Bangle', 'Bangle'), ('Bracelet', 'Bracelet'), ('Stud Earrings', 'Stud Earrings'), ('Loop Earrings', 'Loop Earrings'), ('Clip Earrings', 'Clip Earrings'), ('Stud Earrings', 'Stud Earrings'), ('Dangling Earrings', 'Dangling Earrings'), ('Ring', 'Ring'), ('Wedding Ring', 'Wedding Ring'), ('Necklace', 'Necklace'), ('Pendant', 'Pendant'), ('Others', 'Others, specify in description')], max_length=20, verbose_name='Item Description'),
        ),
    ]
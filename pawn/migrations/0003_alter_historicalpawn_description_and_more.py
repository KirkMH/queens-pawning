# Generated by Django 4.0 on 2023-12-08 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pawn', '0002_alter_pawn_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalpawn',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='pawn',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
    ]
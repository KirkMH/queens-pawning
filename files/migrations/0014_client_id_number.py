# Generated by Django 4.0 on 2024-02-14 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0013_alter_validid_options_remove_client_id_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='id_number',
            field=models.CharField(default='', max_length=20, verbose_name='ID Number'),
            preserve_default=False,
        ),
    ]

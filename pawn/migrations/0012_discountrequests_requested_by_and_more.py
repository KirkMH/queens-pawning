# Generated by Django 4.0 on 2024-02-18 16:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('access_hub', '0003_alter_employee_branch_alter_employee_user_type'),
        ('pawn', '0011_discountrequests'),
    ]

    operations = [
        migrations.AddField(
            model_name='discountrequests',
            name='requested_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='discount_requested_by', to='access_hub.employee'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='discountrequests',
            name='approved_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discount_approved_by', to='access_hub.employee'),
        ),
        migrations.AlterField(
            model_name='discountrequests',
            name='approved_on',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='discountrequests',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected'), ('CANCELLED', 'Cancelled')], default='PENDING', max_length=20, verbose_name='Status'),
        ),
    ]
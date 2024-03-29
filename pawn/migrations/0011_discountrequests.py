# Generated by Django 4.0 on 2024-02-15 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('access_hub', '0003_alter_employee_branch_alter_employee_user_type'),
        ('pawn', '0010_historicalpawn_renewed_to_pawn_renewed_to_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscountRequests',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20, verbose_name='Status')),
                ('approved_on', models.DateTimeField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='discount_approved_by', to='access_hub.employee')),
                ('pawn', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='discount_requested', to='pawn.pawn')),
            ],
        ),
    ]

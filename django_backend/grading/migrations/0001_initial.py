# Generated by Django 3.0.6 on 2020-07-05 09:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Parcel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_parcel_code', models.CharField(max_length=15)),
                ('total_carats', models.DecimalField(decimal_places=3, max_digits=5)),
                ('total_pieces', models.IntegerField()),
                ('reference_price_per_carat', models.PositiveIntegerField()),
                ('gradia_parcel_code', models.CharField(max_length=15)),
            ],
            options={
                'verbose_name': 'Parcel- Check Inventory',
            },
        ),
        migrations.CreateModel(
            name='Split',
            fields=[
                ('original_parcel', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='grading.Parcel')),
                ('split_date', models.DateTimeField(auto_now_add=True)),
                ('split_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Split parcel into smaller parcels or individual stone',
            },
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=15)),
                ('intake_date', models.DateTimeField(auto_now_add=True)),
                ('release_date', models.DateTimeField(blank=True, null=True)),
                ('entity', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customers.Entity')),
                ('intake_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='signed_off_on_stone_intake', to=settings.AUTH_USER_MODEL)),
                ('release_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='signed_off_on_stone_release', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Customer Receipt',
            },
        ),
        migrations.AddField(
            model_name='parcel',
            name='receipt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='grading.Receipt'),
        ),
        migrations.CreateModel(
            name='Stone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence_number', models.IntegerField()),
                ('stone_id', models.CharField(max_length=15)),
                ('carats', models.DecimalField(decimal_places=3, max_digits=5)),
                ('color', models.CharField(max_length=1)),
                ('grader_1_color', models.CharField(blank=True, max_length=1)),
                ('grader_2_color', models.CharField(blank=True, max_length=1)),
                ('grader_3_color', models.CharField(blank=True, max_length=1)),
                ('clarity', models.CharField(max_length=4)),
                ('grader_1_clarity', models.CharField(blank=True, max_length=4)),
                ('grader_2_clarity', models.CharField(blank=True, max_length=4)),
                ('grader_3_clarity', models.CharField(blank=True, max_length=4)),
                ('fluo', models.CharField(max_length=4)),
                ('culet', models.CharField(max_length=2)),
                ('inclusion_remarks', models.TextField(blank=True)),
                ('grader_1_inclusion', models.TextField(blank=True)),
                ('grader_2_inclusion', models.TextField(blank=True)),
                ('grader_3_inclusion', models.TextField(blank=True)),
                ('rejection_remarks', models.TextField(blank=True)),
                ('data_entry_user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='entered_data_for_stone', to=settings.AUTH_USER_MODEL)),
                ('grader_1', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='grader_1_for_stone', to=settings.AUTH_USER_MODEL)),
                ('grader_2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='grader_2_for_stone', to=settings.AUTH_USER_MODEL)),
                ('grader_3', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='grader_3_for_stone', to=settings.AUTH_USER_MODEL)),
                ('split_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='grading.Split')),
            ],
            options={
                'verbose_name': 'Stone- Check Inventory',
            },
        ),
        migrations.AddField(
            model_name='parcel',
            name='split_from',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='grading.Split'),
        ),
    ]

# Generated by Django 3.0.6 on 2020-06-12 16:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grading', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stone',
            name='grader_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='grader_2_for_stone', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='stone',
            name='grader_3',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='grader_3_for_stone', to=settings.AUTH_USER_MODEL),
        ),
    ]

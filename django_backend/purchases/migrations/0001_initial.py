# Generated by Django 3.0.6 on 2020-11-27 16:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Seller",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("address", models.TextField()),
                ("remarks", models.TextField(blank=True)),
                ("phone", models.CharField(max_length=11)),
                ("email", models.CharField(max_length=255)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Receipt",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=15)),
                ("intake_date", models.DateTimeField(auto_now_add=True)),
                ("release_date", models.DateTimeField(blank=True, null=True)),
                (
                    "entity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchases.Seller",
                    ),
                ),
                (
                    "intake_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="signed_off_on_stone_purchase_intake",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "release_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="signed_off_on_stone_purchase_release",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Parcel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("customer_parcel_code", models.CharField(max_length=15)),
                ("total_carats", models.DecimalField(decimal_places=3, max_digits=5)),
                ("total_pieces", models.IntegerField()),
                ("reference_price_per_carat", models.PositiveIntegerField()),
                (
                    "rejected_carats",
                    models.DecimalField(
                        blank=True, decimal_places=3, max_digits=5, null=True
                    ),
                ),
                ("rejected_pieces", models.IntegerField(blank=True, null=True)),
                ("total_price_paid", models.IntegerField(blank=True, null=True)),
                (
                    "receipt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchases.Receipt",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="AuthorizedPersonnel",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("position", models.CharField(max_length=11)),
                ("name", models.CharField(max_length=255)),
                ("email", models.CharField(max_length=255)),
                ("mobile", models.CharField(max_length=11)),
                ("hkid", models.CharField(max_length=10)),
                ("remarks", models.TextField(blank=True)),
                (
                    "entity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="purchases.Seller",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]

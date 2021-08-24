import csv
import hashlib
import os
import itertools

# import StringIO
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.utils import IntegrityError
from django.urls import reverse
from django.utils.html import format_html

from stonegrading.mixins import (
    BasicGradingMixin,
    GIAGradingMixin,
    GIAGradingAdjustMixin,
    GWGradingMixin,
    GWGradingAdjustMixin,
    AutoGradeMixin,
    SarineGradingMixin,
)
from stonegrading.grades import (
    ColorGrades,
    CuletGrades,
    ClarityGrades,
    GeneralGrades,
    GirdleGrades,
    FluorescenceGrades,
    Inclusions,
)

from customers.models import Entity
from ownerships.models import ParcelTransfer, StoneTransfer

from .helpers import get_stone_fields


def generate_csv(filename, dir_name, field_names, queryset):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    file_path = dir_name + filename
    with open(file_path, "w") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(field_names)
        for stone in reversed(queryset.all()):
            values = []
            for field in field_names:
                value = getattr(stone, field)
                values.append(value)
            writer.writerow(values)

    return file_path


class StoneManager(models.Manager):
    def generate_id_csv(self, queryset):
        filename = "Gradia_id_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/download_ids/"
        field_names = ["internal_id"]

        return generate_csv(filename, dir_name, field_names, queryset)

    def generate_master_report_csv(self, queryset):
        filename = "Master_report_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/master_reports/"
        field_names = get_stone_fields(Stone)

        return generate_csv(filename, dir_name, field_names, queryset)

    def generate_to_goldway_csv(self, queryset):
        filename = "To_Goldway_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/to_goldway/"
        field_names = ["date_to_GW", "internal_id", "basic_carat"]

        return generate_csv(filename, dir_name, field_names, queryset)

    def generate_to_GIA_csv(self, queryset):
        filename = "To_GIA_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/to_GIA/"
        field_names = ["date_to_GIA", "external_id", "carat_weight", "color"]

        return generate_csv(filename, dir_name, field_names, queryset)

    def generate_basic_report_csv(self, queryset):
        filename = "Basic_Report" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/Basic_Report/"

        field_names = Stone.basic_grading_fields

        return generate_csv(filename, dir_name, field_names, queryset)

    def generate_triple_report_csv(self, queryset):
        filename = "Triple_Report" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/Triple_Report/"
        field_names = ["internal_id", "external_id", "carat_weight", "color", "clarity"]

        return generate_csv(filename, dir_name, field_names, queryset)


class Split(models.Model):
    original_parcel = models.OneToOneField("Parcel", on_delete=models.PROTECT, primary_key=True)

    split_by = models.ForeignKey(User, on_delete=models.PROTECT)
    split_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Split of {self.original_parcel}"

    def split_into_summary(self):
        summary = ""
        parcels = Parcel.objects.filter(split_from=self).count()
        if parcels:
            summary += f"{parcels} parcels"
        stones = Stone.objects.filter(split_from=self).count()
        if stones:
            summary += f"{stones} stones"
        if summary == "":
            raise
        return summary


class AbstractReceipt(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    code = models.CharField(max_length=15)
    intake_date = models.DateTimeField(auto_now_add=True)
    release_date = models.DateTimeField(null=True, blank=True)
    intake_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="signed_off_on_stone_intake")
    release_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="signed_off_on_stone_release", null=True, blank=True
    )

    admin_url = "admin:grading_receipt_change"
    close_url = "grading:close_receipt"

    def __str__(self):
        return "receipt " + self.code

    class Meta:
        abstract = True

    def closed_out(self):
        return self.release_by is not None and self.release_date is not None

    closed_out.boolean = True

    def get_receipt_with_html_link(self):
        link = reverse(self.admin_url, args=[self.id])
        return format_html(f'<a href="{link}">{self}</a>')

    get_receipt_with_html_link.short_description = "receipt"
    get_receipt_with_html_link.admin_order_field = "receipt"

    def get_action_html_link(self):
        # in the future might have to check user permissions here
        if not self.closed_out():
            link = reverse(self.close_url, args=[self.id])
            return format_html(f'<a href="{link}">Close Out</a>')
        return "-"

    get_action_html_link.short_description = "action"


class Receipt(AbstractReceipt):
    class Meta:
        verbose_name = "customer receipt"


class AbstractParcel(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT)
    customer_parcel_code = models.CharField(max_length=15)

    total_carats = models.DecimalField(max_digits=5, decimal_places=3)
    total_pieces = models.IntegerField()
    reference_price_per_carat = models.PositiveIntegerField()

    admin_url = "admin:grading_parcel_change"

    def __str__(self):
        return f"parcel {self.customer_parcel_code} ({self.total_carats}ct, {self.total_pieces}pcs, {self.receipt})"

    class Meta:
        abstract = True

    def get_receipt_with_html_link(self):
        return self.receipt.get_receipt_with_html_link()

    get_receipt_with_html_link.short_description = "receipt"
    get_receipt_with_html_link.admin_order_field = "receipt"

    def get_parcel_with_html_link(self):
        link = reverse(self.admin_url, args=[self.id])
        return format_html(f'<a href="{link}">{self}</a>')

    get_parcel_with_html_link.short_description = "parcel"
    get_parcel_with_html_link.admin_order_field = "id"


class Parcel(AbstractParcel):
    split_from = models.ForeignKey(Split, on_delete=models.PROTECT, blank=True, null=True)
    gradia_parcel_code = models.CharField(max_length=15)

    def __str__(self):
        return f"parcel {self.gradia_parcel_code} ({self.total_carats}ct, {self.total_pieces}pcs, {self.receipt})"

    def current_location(self):
        return ParcelTransfer.get_current_location(self)

    def finished_basic_grading(self):
        if Stone.objects.filter(split_from__parcel=self).count() == self.total_pieces:
            return True
        return False

    finished_basic_grading.boolean = True

    def most_recent_transfer(self):
        parcel = ParcelTransfer.most_recent_transfer(self)
        return f"{parcel.from_user} -> {parcel.to_user} (on {parcel.initiated_date:%D})"

    def get_action_html_link_for_user(self, user):
        # in the future might have to check user permissions here
        transfer = ParcelTransfer.most_recent_transfer(self)
        if transfer.fresh:
            if transfer.to_user == user:
                if transfer.in_transit():
                    return format_html(
                        f"<a href='{reverse('grading:confirm_received', args=[self.id])}'>Confirm Received</a>"
                    )
                else:
                    return format_html(
                        f"<a href='{reverse('grading:return_to_vault', args=[self.id])}'>Return to Vault</a>"
                    )
            if (
                transfer.in_transit()
                and transfer.to_user.username == "vault"
                and user.groups.filter(name="vault_manager").exists()
            ):
                return format_html(
                    f"<a href='{reverse('grading:confirm_received', args=[self.id])}'>Confirm Stones for Vault</a>"
                )
        return "-"

    get_action_html_link_for_user.short_description = "action"

    def split_into(self):
        # there is also a parcel.split, because split is one-to-one with parcel
        try:
            split = Split.objects.get(original_parcel=self)
        except self.DoesNotExist:
            return "not split"
        return split.split_into_summary()


class GoldwayVerification(models.Model):
    purchase_order = models.CharField(max_length=10, blank=True)
    invoice_number = models.CharField(max_length=10, blank=True)
    started = models.DateTimeField(auto_now_add=True)

    @property
    def code(self):
        pass

    def summary(self):
        return f"{self.stone_set.count()} stones"


class GiaVerification(models.Model):
    receipt_number = models.CharField(max_length=10, blank=True)
    invoice_number = models.CharField(max_length=10, blank=True)
    started = models.DateTimeField(auto_now_add=True)

    @property
    def code(self):
        pass

    def summary(self):
        return f"{self.stone_set.count()} stones"


#     def __str__(self):
#         return self.inclusion


class Stone(
    SarineGradingMixin,
    BasicGradingMixin,
    GIAGradingMixin,
    GIAGradingAdjustMixin,
    GWGradingMixin,
    GWGradingAdjustMixin,
    AutoGradeMixin,
):
    data_entry_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="entered_data_for_stone")
    split_from = models.ForeignKey(Split, on_delete=models.PROTECT)
    gia_verification = models.ForeignKey(GiaVerification, on_delete=models.PROTECT, blank=True, null=True)
    gw_verification = models.ForeignKey(GoldwayVerification, on_delete=models.PROTECT, blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)
    internal_id = models.IntegerField(unique=True)
    external_id = models.CharField(max_length=11, unique=True, blank=True, null=True)

    objects = StoneManager()

    def current_location(self):
        return StoneTransfer.get_current_location(self)

    def __generate_id(self):
        """
        Generates a hashed id of the stone.
        Format of string byte hashed:
        internal_id, basic_final_color, basic_final_clarity, sarine_cut,
        culet_size, gia_returned_date, gia_material_testing, gw_ai_code
        :return:
        """
        # This is still undergoing refactoring because of the whole Stone refactoring stuff
        payload = (
            f" {self.internal_id}, {self.basic_color_final}, {self.basic_clarity_final},"
            f" {self.sarine_cut_pre_polish_symmetry}, {self.culet_size}"
        )

        hashed = hashlib.blake2b(digest_size=4)
        hashed.update(payload.encode("utf-8"))
        return f"G{hashed.hexdigest()}"

    def generate_basic_external_id(self):
        """
        Returns a basic ID. i.e ID with -B append to it
        :return:
        """
        self.external_id = f"{self.__generate_id()}-B"
        try:
            self.save()
        except IntegrityError:
            # Set external_id to None
            self.external_id = None

            # Send an email to everyone
            raise IntegrityError("External Id Already Exists")

    def generate_triple_verified_external_id(self):
        """
        Returns an ID
        :return:
        """
        basic_hash_id = self.__generate_id()
        # This applies to triple verification. i.e It will not apply to basic
        if self.gw_verification is not None:
            payload = f", {self.gw_verification.code}, {self.gw_verification.started}"

            hashed = hashlib.blake2b(digest_size=3)
            hashed.update(payload.encode("utf-8"))
            hashed_value = f"G{hashed.hexdigest()}"

        self.external_id = self.__generate_id()
        try:
            self.save()
        except IntegrityError:
            # Send an email to everyone
            raise IntegrityError("External Id Already Exists")

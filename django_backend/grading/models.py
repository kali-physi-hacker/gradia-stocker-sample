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


"""
class A
C3 linear algorithm 
mro  ==> Method Resolution Order
"""

from stonegrading.mixins import (
    BasicGradingMixin,
    GIAGradingMixin,
    GIAGradingAdjustMixin,
    GWGradingAdjustMixin,
    GWGradingMixin,
    SarineGradingMixin,
    AutoGradeMixin,
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


def generate_csv(filename, dir_name, field_names, queryset, field_map):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    file_path = dir_name + filename

    with open(file_path, "w") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(field_names)
        for stone in reversed(queryset.all()):
            values = []
            for field in field_names:
                try:
                    value = getattr(stone, field)
                except:
                    # using the expected attribute
                    # field_map value contains attributes that exists

                    # there are some cases in which like gia code where both attributes and values don't exist but are needed
                    try:
                        attribute = stone.__dict__[field_map[field]]
                        value = attribute
                    except:
                        value = ""

                if "inclusion" in field and value != "":
                    value = ", ".join([instance.inclusion for instance in value.all()])
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

    def generate_basic_grading_template(self, request, queryset):
        filename = "Basic_Grading_Template_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/basic_grading_template/"
        field_names = [
            "internal_id",
            "basic_diamond_description",
            "basic_grader_1",
            "basic_grader_2",
            "basic_grader_3",
            "basic_carat",
            "basic_color_1",
            "basic_color_2",
            "basic_color_3",
            "basic_color_final",
            "basic_clarity_1",
            "basic_clarity_2",
            "basic_clarity_3",
            "basic_clarity_final",
            "basic_fluorescence_1",
            "basic_fluorescence_2",
            "basic_fluorescence_3",
            "basic_fluorescence_final",
            "basic_culet_1",
            "basic_culet_2",
            "basic_culet_3",
            "basic_culet_final",
            "basic_culet_characteristic_1",
            "basic_culet_characteristic_2",
            "basic_culet_characteristic_3",
            "basic_culet_characteristic_final",
            "basic_girdle_condition_1",
            "basic_girdle_condition_2",
            "basic_girdle_condition_3",
            "basic_girdle_condition_final",
            "basic_inclusions_1",
            "basic_inclusions_2",
            "basic_inclusions_3",
            "basic_inclusions_final",
            "basic_polish_1",
            "basic_polish_2",
            "basic_polish_3",
            "basic_polish_final",
            "girdle_min_grade",
            "basic_girdle_min_grade_final",
            "basic_remarks",
        ]

        return generate_csv(filename, dir_name, field_names, queryset, {})

    def generate_to_goldway_csv(self, request, queryset):
        filename = "To_Goldway_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/to_goldway/"
        field_names = [
            "date_from_gw",
            "internal_id",
            "nano_etch_inscription",
            "basic_carat",
        ]

        return generate_csv(
            filename, dir_name, field_names, queryset, field_map={"nano_etch_inscription": "external_id"}
        )

    def generate_adjust_goldway_csv(self, queryset):
        filename = "Adjust_Goldway" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/adjust_goldway/"
        field_names = [
            "internal_id",
            "nano_etch_inscription",
            "gw_adjust_grader_1",
            "gw_adjust_grader_2",
            "gw_adjust_grader_3",
            "basic_color_final",
            "gw_color",
            "gw_color_adjusted_1",
            "gw_color_adjusted_2",
            "gw_color_adjusted_3",
            "gw_color_adjusted_final",
            "basic_clarity_final",
            "gw_clarity",
            "gw_clarity_adjusted_1",
            "gw_clarity_adjusted_2",
            "gw_clarity_adjusted_3",
            "gw_clarity_adjusted_final",
            "basic_fluorescence_final",
            "gw_fluorescence",
            "gw_fluorescence_adjusted_1",
            "gw_fluorescence_adjusted_2",
            "gw_fluorescence_adjusted_3",
            "gw_fluorescence_adjusted_final",
            "gw_adjust_remarks",
        ]

        return generate_csv(filename, dir_name, field_names, queryset, {})

    def generate_to_GIA_csv(self, queryset):
        filename = "To_GIA_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/to_GIA/"
        field_names = [
            "date_from_gia",
            "nano_etch_inscription",
            "basic_carat",
            "basic_color_final",
        ]

        return generate_csv(
            filename, dir_name, field_names, queryset, field_map={"nano_etch_inscription": "external_id"}
        )

    def generate_adjust_GIA_csv(self, queryset):
        filename = "Adjust_GIA" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/adjust_gia/"
        field_names = [
            "gia_code",
            "nano_etch_inscription",
            "gia_adjust_grader_1",
            "gia_adjust_grader_2",
            "gia_adjust_grader_3",
            "gia_color_adjusted_final",
            "gia_color",
            "gia_color_adjusted_1",
            "gia_color_adjusted_2",
            "gia_color_adjusted_3",
            "gia_color_adjusted_final",
            "basic_polish_final",
            "gia_polish_adjusted_1",
            "gia_polish_adjusted_2",
            "gia_polish_adjusted_3",
            "gia_polish_adjusted_final",
            "basic_culet_final",
            "gia_culet_adjusted_1",
            "gia_culet_adjusted_2",
            "gia_culet_adjusted_3",
            "gia_culet_adjusted_final",
            "basic_culet_characteristic_final",
            "gia_culet_characteristic_1",
            "gia_culet_characteristic_2",
            "gia_culet_characteristic_3",
            "gia_culet_characteristic_final",
            "gia_adjust_remarks",
        ]

        return generate_csv(filename, dir_name, field_names, queryset, {})

    def generate_basic_report_csv(self, queryset):
        filename = "Basic_Report" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/Basic_Report/"

        field_names = [
            "internal_id",
            "diameter_min",
            "diameter_max",
            "height",
            "table_size",
            "crown_angle",
            "pavilion_angle",
            "star_length",
            "lower_half",
            "girdle_thickness_number",
            "girdle_min_number",
            "girdle_max_number",
            "culet_size",
            "crown_height",
            "pavilion_depth",
            "total_depth",
            "table_size_rounded",
            "crown_angle_rounded",
            "pavilion_angle_rounded",
            "star_length_rounded",
            "lower_half_rounded",
            "girdle_thickness_rounded",
            "girdle_min_grade",
            "girdle_max_grade",
            "culet_size_description",
            "crown_height_rounded",
            "pavilion_depth_rounded",
            "total_depth_rounded",
            "sarine_cut_pre_polish_symmetry",
            "sarine_symmetry",
            "roundness",
            "roundness_grade",
            "table_size_dev",
            "table_size_dev_grade",
            "crown_angle_dev",
            "crown_angle_dev_grade",
            "pavilion_angle_dev",
            "pavilion_angle_dev_grade",
            "star_length_dev",
            "star_length_dev_grade",
            "lower_half_dev",
            "lower_half_dev_grade",
            "girdle_thick_dev",
            "girdle_thick_dev_grade",
            "crown_height_dev",
            "crown_height_dev_grade",
            "pavilion_depth_dev",
            "pavilion_depth_dev_grade",
            "misalignment",
            "misalignment_grade",
            "table_edge_var",
            "table_edge_var_grade",
            "table_off_center",
            "table_off_center_grade",
            "culet_off_center",
            "culet_off_center_grade",
            "table_off_culet",
            "table_off_culet_grade",
            "star_angle",
            "star_angle_grade",
            "upper_half_angle",
            "upper_half_angle_grade",
            "lower_half_angle",
            "lower_half_angle_grade",
        ]

        return generate_csv(filename, dir_name, field_names, queryset, {})

    def generate_triple_report_csv(self, queryset):
        filename = "Triple_Report" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/Triple_Report/"

        field_names = [
            "internal_id",
            "goldway_code",
            "gia_code",
            "basic_carat_final",
            "gw_color_adjusted_final",
            "gw_clarity_adjusted_final",
            "gw_fluorescence_adjusted_final",
            "gia_culet_characteristic_final",
            "gia_culet_adjusted_final",
            "basic_inclusions_final",
            "basic_inclusions_final",
            "gia_polish_adjusted_final",
            "diameter_min",
            "diameter_max",
            "height",
            "table_size",
            "crown_angle",
            "pavilion_angle",
            "star_length",
            "lower_half",
            "girdle_thickness_number",
            "girdle_min_number",
            "girdle_max_number",
            "crown_height",
            "pavilion_depth",
            "total_depth",
            "sarine_cut_pre_polish_symmetry",
            "sarine_symmetry",
            "blockchain_address",
            "basic_remarks",
            "gw_remarks",
            "gw_adjust_remarks",
            "gia_remarks",
            "post_gia_remarks",
        ]

        return generate_csv(filename, dir_name, field_names, queryset, {})


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
        User,
        on_delete=models.PROTECT,
        related_name="signed_off_on_stone_release",
        null=True,
        blank=True,
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
    purchase_order = models.CharField(max_length=15, blank=True)
    invoice_number = models.CharField(max_length=15, blank=True)
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
    GWGradingMixin,
    GWGradingAdjustMixin,
    GIAGradingMixin,
    GIAGradingAdjustMixin,
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

    @property
    def customer_receipt_number(self):
        return self.split_from.original_parcel.receipt.code

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

        hashed = hashlib.blake2b(digest_size=3)
        hashed.update(payload.encode("utf-8"))
        return f"G{hashed.hexdigest()}-{self.internal_id}"

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

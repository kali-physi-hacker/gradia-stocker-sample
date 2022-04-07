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
    CuletCharacteristics,
)

from customers.models import Entity
from ownerships.models import ParcelTransfer, StoneTransfer

from .helpers import get_stone_fields


def generate_csv(filename, dir_name, field_names, queryset, field_map):
    is_lab_export = False

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    file_path = dir_name + filename

    if "gradia_ID" in field_map:  # if gradia_ID found it means we're doing an export to lab
        omit_plus_or_minus_fields = (
            "gia_color_adjusted_final",
            "gw_clarity_adjusted_final",
            "gw_fluorescence_adjusted_final",
            "basic_polish_final",
        )
        is_lab_export = True

    with open(file_path, "w") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(field_names)
        if len(field_map) > 1:
            for field in field_map:
                index = field_names.index(field)
                field_names[index] = field_map[field]
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

                if value is None:
                    value = ""

                if is_lab_export and field in omit_plus_or_minus_fields:
                    value = value.strip("+").strip("-")

                if is_lab_export and field == "gia_culet_characteristic_final":
                    export_value = CuletCharacteristics.LAB_EXPORT_MAP.get(value)
                    value = export_value if export_value is not None else value

                if is_lab_export and field == "height":
                    value = "%.2f" % round(float(value), 2) if value != "" else value

                if "inclusion" in field and value != "":
                    value = ", ".join([instance.inclusion for instance in value.all()])

                if "verification" in field and value != "" and value is not None:
                    value = value.code

                if "split_from" in field and value != "":
                    value = value.original_parcel.gradia_parcel_code

                values.append(value)
            writer.writerow(values)

    return file_path


class StoneManager(models.Manager):
    def generate_external_id_csv(self, queryset):
        filename = "Gradia_id_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/download_ids/"
        field_names = ["external_id"]

        return generate_csv(filename, dir_name, field_names, queryset, {})

    def generate_master_report_csv(self, queryset):
        filename = "Master_report_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/master_reports/"
        field_names = get_stone_fields(Stone)
        return generate_csv(filename, dir_name, field_names, queryset, {})

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

    def generate_goldway_grading_template(self, request, queryset):
        filename = "Goldway_Grading_Template_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "csv_downloads/goldway_grading_template/"
        field_names = [
            "date_from_gw",
            "internal_id",
            "goldway_code",
            "nano_etch_inscription",
            "gw_return_reweight",
            "gw_color",
            "gw_clarity",
            "gw_fluorescence",
            "gw_remarks",
        ]
        return generate_csv(
            filename, dir_name, field_names, queryset, field_map={"nano_etch_inscription": "external_id"}
        )

    def generate_gia_grading_template(self, request, queryset):
        filename = "GIA_Grading_Template_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "csv_downloads/gia_grading_template/"
        field_names = [
            "internal_id",
            "date_from_gia",
            "nano_etch_inscription",
            "gia_code",
            "gia_diamond_description",
            "gia_color",
            "gia_remarks",
        ]
        return generate_csv(
            filename, dir_name, field_names, queryset, field_map={"nano_etch_inscription": "external_id"}
        )

    def generate_to_goldway_csv(self, request, queryset):
        filename = "To_Goldway_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/to_goldway/"

        # Generate the triple verified external ids
        for stone in queryset:
            stone.generate_triple_verified_external_id()

        field_names = [
            "date_to_gw",
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

        return generate_csv(
            filename, dir_name, field_names, queryset, field_map={"nano_etch_inscription": "external_id"}
        )

    def generate_to_GIA_csv(self, queryset):
        filename = "To_GIA_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/to_GIA/"
        field_names = [
            "internal_id",
            "date_to_gia",
            "nano_etch_inscription",
            "gw_return_reweight",
            "gw_color_adjusted_final",
        ]

        return generate_csv(
            filename, dir_name, field_names, queryset, field_map={"nano_etch_inscription": "external_id"}
        )

    def generate_adjust_GIA_csv(self, queryset):
        filename = "Adjust_GIA" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/adjust_gia/"
        field_names = [
            "internal_id",
            "gia_code",
            "nano_etch_inscription",
            "gia_adjust_grader_1",
            "gia_adjust_grader_2",
            "gia_adjust_grader_3",
            "gia_color",
            "gw_color_adjusted_final",
            "gia_color_adjusted_1",
            "gia_color_adjusted_2",
            "gia_color_adjusted_3",
            "gia_color_adjusted_final",
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

        return generate_csv(
            filename, dir_name, field_names, queryset, field_map={"nano_etch_inscription": "external_id"}
        )

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
        filename = "Triple_Report_Lab_Export" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        dir_name = settings.MEDIA_ROOT + "/csv_downloads/Triple_Report/"

        field_names = [
            "date",
            "gradia_ID",
            "carat",
            "color",
            "clarity",
            "fluorescence",
            "culet",
            "culet_description",
            "cut",
            "polish",
            "symmetry",
            "table_size",
            "crown_angle",
            "pavilion_angle",
            "star_length",
            "lower_half",
            "girdle_thickness",
            "girdle_maximum",
            "girdle_minimum",
            "crown_height",
            "pavilion_depth",
            "total_depth",
            "comments",
            "diameter_min",
            "diameter_max",
            "height",
            "goldway_AI_code",
            "GIA_batch_code",
            "inclusion",
        ]
        field_map = {
            "date": "adjust_gia_date",
            "gradia_ID": "external_id",
            "carat": "basic_carat",
            "color": "gia_color_adjusted_final",
            "clarity": "gw_clarity_adjusted_final",
            "fluorescence": "gw_fluorescence_adjusted_final",
            "culet": "gia_culet_adjusted_final",
            "culet_description": "gia_culet_characteristic_final",
            "cut": "auto_final_gradia_cut_grade",
            "polish": "basic_polish_final",
            "symmetry": "sarine_symmetry",
            "girdle_thickness": "girdle_thickness_rounded",
            "girdle_maximum": "girdle_max_grade",
            "girdle_minimum": "basic_girdle_min_grade_final",
            "table_size": "table_size_rounded",
            "crown_angle": "crown_angle_rounded",
            "pavilion_angle": "pavilion_angle_rounded",
            "star_length": "star_length_rounded",
            "lower_half": "lower_half_rounded",
            "crown_height": "crown_height_rounded",
            "pavilion_depth": "pavilion_depth_rounded",
            "total_depth": "total_depth_rounded",
            "goldway_AI_code": "gw_verification",
            "GIA_batch_code": "gia_verification",
            "inclusion": "basic_inclusions_final",
        }

        return generate_csv(filename, dir_name, field_names, queryset, field_map=field_map)


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
    closed = models.BooleanField(default=False)
    reference_price_per_carat = models.PositiveIntegerField()

    admin_url = "admin:grading_parcel_change"
    close_url = "grading:close_parcel"

    def __str__(self):
        return f"parcel {self.customer_parcel_code} ({self.total_carats}ct, {self.total_pieces}pcs, {self.receipt})"

    class Meta:
        abstract = True

    def closed_out(self):
        return self.closed

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
        close_parcel = f"<a href='{reverse('grading:close_parcel', args=[self.id])}'>Close Parcel</a>"

        if transfer.fresh:
            if transfer.to_user == user:
                if transfer.in_transit():
                    confirm_received = (
                        f"<a href='{reverse('grading:confirm_received', args=[self.id])}'>Confirm Received</a>"
                    )
                    return format_html(f"<ul><li>{close_parcel}</li><{confirm_received}</li></ul>")
                else:
                    return_to_vault = (
                        f"<a href='{reverse('grading:return_to_vault', args=[self.id])}'>Return to Vault</a>"
                    )
                    return format_html(f"<ul><li>{close_parcel}</li><{return_to_vault}</li></ul>")
            if (
                transfer.in_transit()
                and transfer.to_user.username == "vault"
                and user.groups.filter(name="vault_manager").exists()
            ):
                confirm_stones = (
                    f"<a href='{reverse('grading:confirm_received', args=[self.id])}'>Confirm Stones for Vault</a>"
                )
                return format_html(f"<ul><li>{close_parcel}</li><{confirm_stones}</li></ul>")
        return format_html(f"{close_parcel}")

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
    invoice_number = models.CharField(max_length=15, unique=True, blank=True)
    started = models.DateTimeField(auto_now_add=True)

    @property
    def code(self):
        return self.invoice_number

    def summary(self):
        return f"{self.stone_set.count()} stones"


class GiaVerification(models.Model):
    receipt_number = models.CharField(max_length=15, blank=True)
    invoice_number = models.CharField(max_length=15, blank=True)
    started = models.DateTimeField(auto_now_add=True)

    @property
    def code(self):
        return self.receipt_number

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
    external_id = models.CharField(max_length=11, db_index=True, unique=True, blank=True, null=True)

    macro_filename = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nano_filename = models.CharField(max_length=20, unique=True, null=True, blank=True)

    objects = StoneManager()

    def __str__(self):
        text = self.external_id if self.external_id is not None else self.internal_id
        return str(text)

    @property
    def macro_image_uploaded(self):
        """
        Returns True if macro image has been upload and returns False otherwise.
        Here, were technically just returning True if the macro_filename field is not None
        and returning False otherwise
        """
        if self.macro_filename is None:
            return False

        return True

    @property
    def nano_image_uploaded(self):
        """
        Returns True if nano image has been uploaded and returns False otherwise.
        """
        if self.nano_filename is None:
            return False

        return True

    @property
    def customer_receipt_number(self):
        return self.split_from.original_parcel.receipt.code

    def current_location(self):
        return StoneTransfer.get_current_location(self)

    def generate_id_later_part(self):
        """
        Returns  the last 3 digits of the internal id
        """
        # if internal_id is 1 === 001
        return f"{self.internal_id% 1000:03d}"

    # use a modular to save instead of repeating these twice
    def save_external(self):
        try:
            self.save()
        except IntegrityError:
            # email error to everyone
            raise IntegrityError("External Id already exists")

    def generate_payload(self):
        payload = (
            f" {self.internal_id}, {self.basic_color_final}, {self.basic_clarity_final},"
            f" {self.sarine_cut_pre_polish_symmetry}, {self.culet_size}"
        )

        return payload

    def generate_triple_verified_external_id(self):
        """
        Generates full triple verified external_id and updates the stone's external_id value
        :returns:
        """
        self.generate_basic_external_id()
        self.external_id = self.external_id[:-2]  # Just strip of -B
        self.save_external()

    def generate_basic_external_id(self):
        """
        Generates full basic external_id
        :returns:
        """
        payload_part = self.generate_payload()
        later_part = self.generate_id_later_part()

        hashed = hashlib.blake2b(digest_size=3)
        hashed.update(payload_part.encode("utf-8"))  # 4 characters # GB starts the ID
        self.external_id = f"G{hashed.hexdigest()[:-1]}{later_part}-B"
        self.save_external()

    @property
    def is_sarine_grading_complete(self):
        """
        Returns true / false on whether it is done with sarine grading
        :return:
        """
        # Technically, this property is not very significant since, sarine grading results
        # is what even makes the stone instance exists in the 1st place
        fields = [field.name for field in SarineGradingMixin._meta.get_fields()]
        is_empty = False
        for field in fields:
            if getattr(self, field) is None:
                is_empty = True
                break
        return not is_empty

    @property
    def is_basic_grading_complete(self):
        """
        Returns true / false on whether it is done with basic grading
        :return:
        """
        fields = [field.name for field in BasicGradingMixin._meta.get_fields()]
        is_empty = False
        for field in fields:
            if getattr(self, field) is None:
                is_empty = True
                break
        return not is_empty

    @property
    def is_goldway_grading_complete(self):
        """
        Returns true / false on whether it is done with goldway grading
        :return:
        """
        return self.gw_verification is not None and self.date_from_gw is not None

    @property
    def is_gia_grading_complete(self):
        """
        Returns true /false on whether it is done with gia grading
        :return:
        """
        return self.gia_verification is not None and self.date_from_gia is not None

    @property
    def is_goldway_adjusting_grading_complete(self):
        """
        Returns true / false on whether it is done with goldway adjusting grading
        :return:
        """
        fields = [field.name for field in GWGradingAdjustMixin._meta.get_fields()]
        is_empty = False
        for field in fields:
            if getattr(self, field) is None:
                is_empty = True
                break
        return not is_empty

    @property
    def is_gia_adjusting_grading_complete(self):
        """
        Returns true / false on whether it is done with gia adjusting grading
        :return:
        """
        fields = [field.name for field in GIAGradingAdjustMixin._meta.get_fields()]
        is_empty = False
        for field in fields:
            if getattr(self, field) is None:
                is_empty = True
                break
        return not is_empty

    @property
    def is_triple_grading_complete(self):
        """
        Returns true / false on whether it is completely done with all the grading
        stages
        :return:
        """
        return (
            self.is_sarine_grading_complete
            and self.is_basic_grading_complete
            and self.is_goldway_grading_complete
            and self.is_goldway_adjusting_grading_complete
            and self.is_gia_grading_complete
            and self.is_gia_adjusting_grading_complete
        )

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from customers.models import Entity
from ownerships.models import ParcelTransfer, StoneTransfer
from .helpers import get_model_fields, get_field_names, CSVManager

import os
import csv

# import StringIO
from datetime import datetime
from django.conf import settings
from django.utils.timezone import utc


class StoneManager(models.Manager):
    def download_ids(self, queryset):
        filename = (
            "Gradia_id_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".csv"
        )
        file_path = settings.MEDIA_ROOT + "/csv_downloads/download_ids/" + filename
        with CSVManager(file_path, "w") as file:
            # if we don't want it saved on the server
            # f = StringIO.StringIO()
            writer = csv.writer(file, delimiter=",")
            writer.writerow(
                [
                    "internal_id",
                ]
            )
            for stone in reversed(queryset.all()):
                writer.writerow(
                    [
                        stone.internal_id,
                    ]
                )

        return file_path

    def download_master_reports(self, queryset):
        filename = (
            "Master_report_"
            + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S"))
            + ".csv"
        )
        file_path = settings.MEDIA_ROOT + "/csv_downloads/master_reports/" + filename
        with CSVManager(file_path, "w") as file:
            # if we don't want it saved on the server
            # f = StringIO.StringIO()
            writer = csv.writer(file, delimiter=",")
            model_fields = get_model_fields(Stone)
            field_names = get_field_names(model_fields)
            writer.writerow(field_names)
            for stone in reversed(queryset.all()):
                values = []
                for field in field_names:
                    value = getattr(stone, field)
                    values.append(value)
                writer.writerow(values)

        return file_path

    def download_to_goldway_csv(self, queryset):
        filename = (
            "To_Goldway_"
            + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S"))
            + ".csv"
        )
        file_path = settings.MEDIA_ROOT + "/csv_downloads/to_goldway/" + filename
        with CSVManager(file_path, "w") as file:
            # if we don't want it saved on the server
            # f = StringIO.StringIO()
            writer = csv.writer(file, delimiter=",")
            field_names = ["date_to_GW", "internal_id", "basic_carat"]
            writer.writerow(field_names)
            for stone in reversed(queryset.all()):
                values = []
                for field in field_names:
                    value = getattr(stone, field)
                    values.append(value)
                writer.writerow(values)

        return file_path


class Split(models.Model):
    original_parcel = models.OneToOneField(
        "Parcel", on_delete=models.PROTECT, primary_key=True
    )

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
    intake_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="signed_off_on_stone_intake"
    )
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
    split_from = models.ForeignKey(
        Split, on_delete=models.PROTECT, blank=True, null=True
    )
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

    def summary(self):
        return f"{self.stone_set.count()} stones"


class GiaVerification(models.Model):
    receipt_number = models.CharField(max_length=10, blank=True)
    invoice_number = models.CharField(max_length=10, blank=True)
    started = models.DateTimeField(auto_now_add=True)

    def summary(self):
        return f"{self.stone_set.count()} stones"


class ColorGrades:
    COLORLESS_D = "D"
    COLORLESS_E = "E"
    COLORLESS_F = "F"
    NEARLY_COLORLESS_G = "G"
    NEARLY_COLORLESS_H = "H"
    NEARLY_COLORLESS_I = "I"
    NEARLY_COLORLESS_J = "J"

    CHOICES = (
        (COLORLESS_D, "Colorless D"),
        (COLORLESS_E, "Colorless E"),
        (COLORLESS_F, "Colorless F"),
        (NEARLY_COLORLESS_G, "Nearly Colorless G"),
        (NEARLY_COLORLESS_H, "Nearly Colorless H"),
        (NEARLY_COLORLESS_I, "Nearly Colorless I"),
        (NEARLY_COLORLESS_J, "Nearly Colorless J"),
    )


class ClarityGrades:
    INTERNALLY_FLAWLESS = "IF"
    VERY_VERY_SLIGHTLY_INCLUDED_DEGREE_1 = "VVS1"
    VERY_VERY_SLIGHTLY_INCLUDED_DEGREE_2 = "VVS2"
    VERY_SLIGHTLY_INCLUDED_DEGREE_1 = "VS1"
    VERY_SLIGHTLY_INCLUDED_DEGREE_2 = "VS2"
    SLIGHTLY_INCLUDED_DEGREE_1 = "SI1"
    SLIGHTLY_INCLUDED_DEGREE_2 = "SI2"
    INCLUDED = "I1"

    CHOICES = (
        (INTERNALLY_FLAWLESS, "Internally Flawless"),
        (VERY_VERY_SLIGHTLY_INCLUDED_DEGREE_1, "Very Very Slightly Included Degree 1"),
        (VERY_VERY_SLIGHTLY_INCLUDED_DEGREE_2, "Very Very Slightly Included Degree 2"),
        (VERY_SLIGHTLY_INCLUDED_DEGREE_1, "Very Slightly Included Degree 1"),
        (VERY_SLIGHTLY_INCLUDED_DEGREE_2, "Very Slightly Included Degree 2"),
        (SLIGHTLY_INCLUDED_DEGREE_1, "Slightly Included Degree 1"),
        (SLIGHTLY_INCLUDED_DEGREE_2, "Slightly Included Degree 2"),
        (INCLUDED, "Included"),
    )


class GeneralGrades:
    EXCELLENT = "EX"
    VERY_GOOD = "VG"
    GOOD = "GOOD"
    FAIR = "F"
    POOR = "P"

    CHOICES = (
        (EXCELLENT, "Excellent"),
        (VERY_GOOD, "Very Good"),
        (GOOD, "Good"),
        (FAIR, "Fair"),
        (POOR, "Poor"),
    )


class FluorescenceGrades:
    VERY_STRONG = "VS"
    STRONG = "S"
    MEDIUM = "M"
    FAINT = "F"
    NONE = "N"

    CHOICES = (
        (VERY_STRONG, "Very Strong"),
        (STRONG, "Strong"),
        (MEDIUM, "Medium"),
        (FAINT, "Faint"),
        (NONE, "None"),
    )


class GirdleGrades:
    EXTREMELY_THIN = "EXT"
    VERY_THIN = "VTN"
    THIN = "THIN"
    MEDIUM = "MED"
    SLIGHTLY_THICK = "STK"
    THICK = "THK"
    VERY_THICK = "VTK"
    EXTREMELY_THICK = "EXT"
    FACETED = "F"
    SMOOTH = "SM"
    EXTREMELY_THIN_TO_VERY_THIN = "ETN TO VTN"

    CHOICES = (
        (EXTREMELY_THIN, "Extremely Thin"),
        (VERY_THIN, "Very Thin"),
        (THIN, "Thin"),
        (MEDIUM, "Medium"),
        (SLIGHTLY_THICK, "Slightly Thick"),
        (THICK, "Thick"),
        (VERY_THICK, "Very Thick"),
        (EXTREMELY_THICK, "Extremely Thick"),
        (FACETED, "Faceted"),
        (SMOOTH, "Smooth"),
        (EXTREMELY_THIN_TO_VERY_THIN, "Extremely thin - very thin"),
    )


class Inclusions:
    BRUISE = "BR"
    CAVITY = "CV"
    CHIP = "CH"
    CLOUD = "CL"
    FEATHER = "F"
    INCLUDED_CRYSTAL = "IC"
    INDENTED_NATURAL = "IN"
    INTERNAL_GRAINING = "IG"
    KNOT = "KN"
    NEEDLE = "ND"
    PINPOINT = "PP"
    ABRASION = "AB"
    SCRATCH = "SC"
    NICK = "NK"
    POLISH_LINE = "PL"
    PIT = "PT"
    NATURAL = "N"
    EXTRA_FEET = "EF"
    SURFACE_GRAINING = "SG"

    CHOICES = (
        (BRUISE, "Bruise"),
        (CAVITY, "Cavity"),
        (CHIP, "Chip"),
        (CLOUD, "Cloud"),
        (FEATHER, "Feather"),
        (INCLUDED_CRYSTAL, "Included crystal"),
        (INDENTED_NATURAL, "Indented natural"),
        (INTERNAL_GRAINING, "Internal graining"),
        (KNOT, "knot"),
        (NEEDLE, "Needle"),
        (PINPOINT, "Pinpoint"),
        (ABRASION, "Abrasion"),
        (SCRATCH, "Scratch"),
        (NICK, "Nick"),
        (POLISH_LINE, "Polish Line"),
        (PIT, "Pit"),
        (NATURAL, "Natural"),
        (EXTRA_FEET, "Extra Feet"),
        (SURFACE_GRAINING, "Surface Graining"),
    )


class CuletGrades:
    NONE = "N"
    VERY_SMALL = "VS"
    SMALL = "S"
    MEDIUM = "M"
    SLIGHTLY_LARGE = "SL"
    LARGE = "L"
    VERY_LARGE = "VL"
    EXTREMELY_LARGE = "XL"

    CHOICES = (
        (NONE, "None"),
        (VERY_SMALL, "Very Small"),
        (SMALL, "Small"),
        (MEDIUM, "Medium"),
        (SLIGHTLY_LARGE, "Slightly Large"),
        (LARGE, "Large"),
        (VERY_LARGE, "Very Large"),
        (EXTREMELY_LARGE, "Extremely Large"),
    )


class Inclusion(models.Model):
    inclusion = models.CharField(choices=Inclusions.CHOICES, max_length=3, unique=True)

    def __str__(self):
        return self.inclusion


class Stone(models.Model):
    data_entry_user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="entered_data_for_stone"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    internal_id = models.IntegerField(unique=True)
    external_id = models.CharField(max_length=11, unique=True, blank=True, null=True)
    # you can get the parcel and the receipt from split_from
    split_from = models.ForeignKey(Split, on_delete=models.PROTECT)
    # we are merging all comments and remarks into a single field
    remarks = models.TextField(blank=True, null=True)

    ########################################################################
    # basic grading                                                        #
    ########################################################################
    diamond_description = models.CharField(max_length=120, null=True, blank=True)
    basic_carat = models.DecimalField(max_digits=5, decimal_places=3)
    basic_culet = models.CharField(choices=CuletGrades.CHOICES, max_length=2)
    basic_fluorescence = models.CharField(
        choices=FluorescenceGrades.CHOICES, max_length=4
    )
    inclusions = models.ManyToManyField(Inclusion)

    # basic stuff that requires multiple graders
    grader_1 = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="grader_1_for_stone"
    )
    grader_2 = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="grader_2_for_stone", null=True
    )
    grader_3 = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="grader_3_for_stone", null=True
    )

    basic_color_1 = models.CharField(choices=ColorGrades.CHOICES, max_length=1)
    basic_color_2 = models.CharField(
        choices=ColorGrades.CHOICES, max_length=1, null=True
    )
    basic_color_3 = models.CharField(
        choices=ColorGrades.CHOICES, max_length=1, null=True
    )
    basic_final_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1)

    basic_clarity_1 = models.CharField(choices=ClarityGrades.CHOICES, max_length=4)
    basic_clarity_2 = models.CharField(
        choices=ClarityGrades.CHOICES, max_length=4, null=True
    )
    basic_clarity_3 = models.CharField(
        choices=ClarityGrades.CHOICES, max_length=4, null=True
    )
    basic_final_clarity = models.CharField(choices=ClarityGrades.CHOICES, max_length=4)

    basic_polish_1 = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    basic_polish_2 = models.CharField(
        choices=GeneralGrades.CHOICES, max_length=4, null=True
    )
    basic_polish_3 = models.CharField(
        choices=GeneralGrades.CHOICES, max_length=4, null=True
    )
    basic_final_polish = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    # basic stuff that are sarine measurements, and calculated fields
    diameter_min = models.DecimalField(max_digits=5, decimal_places=3)
    diameter_max = models.DecimalField(max_digits=5, decimal_places=3)
    height = models.DecimalField(max_digits=5, decimal_places=3)
    girdle_min = models.CharField(choices=GirdleGrades.CHOICES, max_length=10)
    girdle_max = models.CharField(choices=GirdleGrades.CHOICES, max_length=10)
    girdle_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    culet_size = models.CharField(choices=CuletGrades.CHOICES, max_length=4)
    total_depth = models.DecimalField(max_digits=4, decimal_places=1)
    total_depth_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    sheryl_cut = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    sarine_cut = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    cut_grade_est_table = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    sheryl_symmetry = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    sarine_symmetry = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    symmetry_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    roundness = models.DecimalField(max_digits=4, decimal_places=1)
    roundness_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    table_size = models.DecimalField(max_digits=4, decimal_places=1)
    table_size_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    crown_angle = models.DecimalField(max_digits=4, decimal_places=1)
    crown_angle_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    pavilion_angle = models.DecimalField(max_digits=4, decimal_places=1)
    pavilion_angle_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    star_length = models.DecimalField(max_digits=4, decimal_places=1)
    star_length_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    lower_half = models.DecimalField(max_digits=4, decimal_places=1)
    lower_half_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    girdle_thick = models.DecimalField(max_digits=4, decimal_places=1)
    girdle_thick_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    crown_height = models.DecimalField(max_digits=4, decimal_places=1)
    crown_height_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    pavilion_depth = models.DecimalField(max_digits=4, decimal_places=1)
    pavilion_depth_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    misalignment = models.DecimalField(max_digits=4, decimal_places=1)
    misalignment_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    table_edge_var = models.DecimalField(max_digits=4, decimal_places=1)
    table_edge_var_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    table_off_center = models.DecimalField(max_digits=4, decimal_places=1)
    table_off_center_grade = models.CharField(
        choices=GeneralGrades.CHOICES, max_length=4
    )
    culet_off_center = models.DecimalField(max_digits=4, decimal_places=1)
    culet_off_center_grade = models.CharField(
        choices=GeneralGrades.CHOICES, max_length=4
    )
    table_off_culet = models.DecimalField(max_digits=4, decimal_places=1)
    table_off_culet_grade = models.CharField(
        choices=GeneralGrades.CHOICES, max_length=4
    )
    star_angle = models.DecimalField(max_digits=4, decimal_places=1)
    star_angle_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    upper_half_angle = models.DecimalField(max_digits=4, decimal_places=1)
    upper_half_angle_grade = models.CharField(
        choices=GeneralGrades.CHOICES, max_length=4
    )
    lower_half_angle = models.DecimalField(max_digits=4, decimal_places=1)
    lower_half_angle_grade = models.CharField(
        choices=GeneralGrades.CHOICES, max_length=4
    )

    ########################################################################
    # GW results                                                           #
    ########################################################################
    goldway_verification = models.ForeignKey(
        GoldwayVerification, on_delete=models.PROTECT, blank=True, null=True
    )
    GW_color = models.CharField(
        choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True
    )
    post_GW_final_color = models.CharField(
        choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True
    )
    GW_clarity = models.CharField(
        choices=ClarityGrades.CHOICES, max_length=4, null=True, blank=True
    )
    post_GW_final_clarity = models.CharField(
        choices=ClarityGrades.CHOICES, max_length=4, null=True, blank=True
    )

    GW_fluo = models.CharField(
        choices=FluorescenceGrades.CHOICES, max_length=4, null=True, blank=True
    )
    post_GW_fluo = models.CharField(
        choices=FluorescenceGrades.CHOICES, max_length=4, null=True, blank=True
    )
    fluoresence = models.CharField(
        choices=FluorescenceGrades.CHOICES, max_length=4, null=True, blank=True
    )
    GW_culet = models.CharField(
        choices=CuletGrades.CHOICES, max_length=2, null=True, blank=True
    )
    post_GW_culet = models.CharField(
        choices=CuletGrades.CHOICES, max_length=2, null=True, blank=True
    )
    GW_carat = models.DecimalField(
        max_digits=5, decimal_places=3, null=True, blank=True
    )
    post_GW_final_carat = models.DecimalField(
        max_digits=5, decimal_places=3, null=True, blank=True
    )
    GW_repolish_carat = models.DecimalField(
        max_digits=5, decimal_places=3, null=True, blank=True
    )

    date_to_GW = models.DateTimeField(null=True, blank=True)
    GW_returned_date = models.DateTimeField(null=True, blank=True)
    goldway_AI_code = models.CharField(max_length=15, null=True, blank=True)
    post_GW_rejection = models.TextField(null=True, blank=True)

    ########################################################################
    # GIA results                                                          #
    ########################################################################

    gia_verification = models.ForeignKey(
        GiaVerification, on_delete=models.PROTECT, blank=True, null=True
    )
    date_to_GIA = models.DateTimeField(null=True, blank=True)
    GIA_returned_date = models.DateTimeField(null=True, blank=True)
    GIA_batch_code = models.IntegerField(null=True, blank=True)
    post_GIA_rejection = models.TextField(null=True, blank=True)

    ########################################################################
    # blockchain results                                                   #
    ########################################################################
    blockchain_ID_code = models.CharField(max_length=15, null=True, blank=True)

    ########################################################################
    # final results                                                   #
    ########################################################################
    color = models.CharField(
        choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True
    )
    clarity = models.CharField(
        choices=ClarityGrades.CHOICES, max_length=4, null=True, blank=True
    )
    culet = models.CharField(
        choices=CuletGrades.CHOICES, max_length=2, null=True, blank=True
    )
    cut_grade = models.CharField(
        choices=GeneralGrades.CHOICES, max_length=4, null=True, blank=True
    )
    carat_weight = models.DecimalField(
        max_digits=4, decimal_places=3, null=True, blank=True
    )
    objects = StoneManager()

    def current_location(self):
        return StoneTransfer.get_current_location(self)

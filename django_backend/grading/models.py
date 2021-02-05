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
    GOOD = "GD"
    FAIR = "F"
    POOR = "P"

    CHOICES = ((EXCELLENT, "Excellent"), (VERY_GOOD, "Very Good"), (GOOD, "Good"), (FAIR, "Fair"), (POOR, "Poor"))


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
    BRUISE = "Br"
    CAVITY = "Cv"
    CHIP = "Ch"
    CLEAVAGE = "Clv"
    CLOUD = "Cld"
    CRYSTAL = "Xtl"
    FEATHER = "Ftr"
    GRAIN_CENTER = "GrCnt"
    INDENTED_NATURAL = "IndN"
    INTERNAL_GRAINING = "IntGr"
    KNOT = "K"
    LASER_DRILL_HOLE = "LDH"
    NEEDLE = "Ndl"
    PINPOINT = "Pp"
    TWINNING_WISP = "W"
    ABRASION = "Abr"
    NATURAL = "N"
    NICK = "Nk"
    PIT = "Pit"
    POLISH_LINE = "PL"
    BURN_MASK = "Brn"
    SCRATCH = "S"
    SURFACE_GRAINING = "SGr"
    EXTRA_FEET = "EF"

    CHOICES = (
        (BRUISE, "Bruise"),
        (CAVITY, "Cavity"),
        (CHIP, "Chip"),
        (CLEAVAGE, "Cleavage"),
        (CLOUD, "Cloud"),
        (CRYSTAL, "Xtl"),
        (FEATHER, "Feather"),
        (GRAIN_CENTER, "Grain Center"),
        (INDENTED_NATURAL, "Indented natural"),
        (INTERNAL_GRAINING, "Internal graining"),
        (KNOT, "knot"),
        (LASER_DRILL_HOLE, "Laser Drill Hole"),
        (NEEDLE, "Needle"),
        (PINPOINT, "Pinpoint"),
        (TWINNING_WISP, "Twinning Wisp"),
        (ABRASION, "Abrasion"),
        (NATURAL, "Natural"),
        (NICK, "Nick"),
        (PIT, "Pit"),
        (POLISH_LINE, "Polish Line"),
        (BURN_MASK, "Burn Mask"),
        (SCRATCH, "Scratch"),
        (SURFACE_GRAINING, "Surface Graining"),
        (EXTRA_FEET, "Extra Feet"),
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

    MULTI_CHOICES = list(itertools.combinations(CHOICES, 2))
    MULTI_CHOICES = [list(item) for item in MULTI_CHOICES]
    MULTI_CHOICES = [sorted(item) for item in MULTI_CHOICES]
    MULTI_CHOICES = tuple((f"{a[0]}/{b[0]}", f"{a[1]} / {b[1]}") for (a, b) in MULTI_CHOICES)


class Inclusion(models.Model):
    inclusion = models.CharField(choices=Inclusions.CHOICES, max_length=5, unique=True)

    def __str__(self):
        return self.inclusion


class BasicGradingMixin(models.Model):
    # internal_id = models.IntegerField(unique=True)
    # external_id = models.CharField(max_length=11, unique=True, blank=True, null=True)
    diamond_description = models.CharField(max_length=120, null=True, blank=True)

    grader_1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="grader_1_for_stone")
    grader_2 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="grader_2_for_stone", blank=True, null=True)
    grader_3 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="grader_3_for_stone", blank=True, null=True)

    basic_carat = models.DecimalField(max_digits=5, decimal_places=3)

    basic_color_1 = models.CharField(choices=ColorGrades.CHOICES, max_length=1)
    basic_color_2 = models.CharField(choices=ColorGrades.CHOICES, max_length=1, null=True)
    basic_color_3 = models.CharField(choices=ColorGrades.CHOICES, max_length=1, null=True)
    basic_final_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1)

    basic_clarity_1 = models.CharField(choices=ClarityGrades.CHOICES, max_length=4)
    basic_clarity_2 = models.CharField(choices=ClarityGrades.CHOICES, max_length=4, null=True)
    basic_clarity_3 = models.CharField(choices=ClarityGrades.CHOICES, max_length=4, null=True)
    basic_final_clarity = models.CharField(choices=ClarityGrades.CHOICES, max_length=4)

    basic_fluorescence = models.CharField(choices=FluorescenceGrades.CHOICES, max_length=4)
    basic_culet = models.CharField(choices=CuletGrades.CHOICES, max_length=2)
    basic_inclusions = models.ManyToManyField(Inclusion, related_name="basic_inclusions")
    # remarks = models.TextField(blank=True, null=True)

    basic_polish_1 = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    basic_polish_2 = models.CharField(choices=GeneralGrades.CHOICES, max_length=4, null=True)
    basic_polish_3 = models.CharField(choices=GeneralGrades.CHOICES, max_length=4, null=True)
    basic_final_polish = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    diameter_min = models.DecimalField(max_digits=5, decimal_places=2)
    diameter_max = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)

    table_size = models.DecimalField(max_digits=4, decimal_places=1)
    crown_angle = models.DecimalField(max_digits=4, decimal_places=2)
    pavilion_angle = models.DecimalField(max_digits=4, decimal_places=2)
    star_length = models.DecimalField(max_digits=4, decimal_places=1)
    lower_half = models.DecimalField(max_digits=4, decimal_places=1)
    girdle_thick = models.DecimalField(max_digits=4, decimal_places=2)

    girdle_min = models.DecimalField(max_digits=4, decimal_places=2)
    girdle_max = models.DecimalField(max_digits=4, decimal_places=2)
    culet_size = models.DecimalField(max_digits=4, decimal_places=2)
    crown_height = models.DecimalField(max_digits=4, decimal_places=2)

    pavilion_depth = models.DecimalField(max_digits=4, decimal_places=2)
    total_depth = models.DecimalField(max_digits=4, decimal_places=2)

    table_size_pct = models.IntegerField()
    table_size_pct_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    crown_angle_degree = models.DecimalField(max_digits=4, decimal_places=1)
    crown_angle_degree_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    pavilion_angle_degree = models.DecimalField(max_digits=4, decimal_places=1)
    pavilion_angle_degree_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    star_length_degree = models.IntegerField(null=True, blank=True)
    star_length_degree_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4, null=True, blank=True)

    lower_half_pct = models.IntegerField()
    lower_half_pct_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    girdle_thick_pct = models.DecimalField(max_digits=4, decimal_places=1)
    girdle_thick_pct_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4, null=True, blank=True)
    girdle_min_description = models.CharField(choices=GirdleGrades.CHOICES, max_length=10)
    girdle_max_description = models.CharField(choices=GirdleGrades.CHOICES, max_length=10)
    girdle_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    culet_size_description = models.CharField(choices=CuletGrades.MULTI_CHOICES, max_length=5)

    crown_height_pct = models.DecimalField(max_digits=4, decimal_places=1)
    crown_height_pct_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    pavilion_depth_pct = models.DecimalField(max_digits=4, decimal_places=1)

    total_depth_pct = models.DecimalField(max_digits=4, decimal_places=1)
    total_depth_pct_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    star_length_pct = models.DecimalField(max_digits=4, decimal_places=1)
    star_length_pct_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    parameter_cut_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    est_table_cut_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    gradia_cut = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    final_gradia_cut = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    final_sarine_cut = models.CharField(choices=GeneralGrades.CHOICES, max_length=4, null=True, blank=True)
    sarine_cut = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    sarine_symmetry = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    roundness = models.DecimalField(max_digits=4, decimal_places=1)
    roundness_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    table_size_dev = models.DecimalField(max_digits=4, decimal_places=1)
    table_size_dev_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    crown_angle_dev = models.DecimalField(max_digits=4, decimal_places=1)
    crown_angle_dev_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    pavilion_angle_dev = models.DecimalField(max_digits=4, decimal_places=1)
    pavilion_angle_dev_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    star_length_dev = models.DecimalField(max_digits=4, decimal_places=1)
    star_length_dev_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    lower_half_dev = models.DecimalField(max_digits=4, decimal_places=1)
    lower_half_dev_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    girdle_thick_dev = models.DecimalField(max_digits=4, decimal_places=1)
    girdle_thick_dev_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    crown_height_dev = models.DecimalField(max_digits=4, decimal_places=1)
    crown_height_dev_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    pavilion_depth_dev = models.DecimalField(max_digits=4, decimal_places=1)
    pavilion_depth_dev_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    misalignment = models.DecimalField(max_digits=4, decimal_places=1)
    misalignment_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    table_edge_var = models.DecimalField(max_digits=4, decimal_places=1)
    table_edge_var_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    table_off_center = models.DecimalField(max_digits=4, decimal_places=1)
    table_off_center_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    culet_off_center = models.DecimalField(max_digits=4, decimal_places=1)
    culet_off_center_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    table_off_culet = models.DecimalField(max_digits=4, decimal_places=1)
    table_off_culet_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    star_angle = models.DecimalField(max_digits=4, decimal_places=1)
    star_angle_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    upper_half_angle = models.DecimalField(max_digits=4, decimal_places=1)
    upper_half_angle_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)
    lower_half_angle = models.DecimalField(max_digits=4, decimal_places=1)
    lower_half_angle_grade = models.CharField(choices=GeneralGrades.CHOICES, max_length=4)

    class Meta:
        abstract = True


class GWAIGradingMixin(models.Model):
    gw_returned_date = models.DateTimeField(null=True, blank=True)

    # Clashing -> Causing errors
    # internal_id = models.IntegerField(unique=True)
    # external_id = models.CharField(max_length=11, unique=True, blank=True, null=True)

    gw_carat = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    gw_repolish_carat = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    gw_fluorescence = models.CharField(choices=FluorescenceGrades.CHOICES, max_length=4, null=True, blank=True)
    gw_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True)
    gw_clarity = models.CharField(choices=ClarityGrades.CHOICES, max_length=4, null=True, blank=True)
    gw_culet = models.CharField(choices=CuletGrades.CHOICES, max_length=2, null=True, blank=True)

    class Meta:
        abstract = True


class PostGWGradingMixin(models.Model):
    date_to_gw = models.DateTimeField(null=True, blank=True)
    # gw_returned_date = models.DateTimeField(null=True, blank=True)
    # gw_ai_code = models.CharField(max_length=15, null=True, blank=True)
    # external_id = models.CharField(max_length=11, unique=True, blank=True, null=True)
    # basic_carat = models.DecimalField(max_digits=5, decimal_places=3)

    # gw_carat = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    post_gw_final_carat = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    # gw_repolish_carat = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)

    # basic_final_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1)

    # gw_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True)
    post_gw_final_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True)

    # basic_final_clarity = models.CharField(choices=ClarityGrades.CHOICES, max_length=4)

    # gw_clarity = models.CharField(choices=ClarityGrades.CHOICES, max_length=4, null=True, blank=True)
    post_gw_final_clarity = models.CharField(choices=ClarityGrades.CHOICES, max_length=4)

    # basic_fluorescence = models.CharField(choices=FluorescenceGrades.CHOICES, max_length=4)

    # gw_fluorescence = models.CharField(choices=FluorescenceGrades.CHOICES, max_length=4, null=True, blank=True)
    post_gw_fluorescence = models.CharField(choices=FluorescenceGrades.CHOICES, max_length=4, null=True, blank=True)

    # basic_final_culet = models.CharField(choices=CuletGrades.CHOICES, max_length=2)

    # gw_culet = models.CharField(choices=CuletGrades.CHOICES, max_length=2)
    post_gw_culet = models.CharField(choices=CuletGrades.CHOICES, max_length=2)

    post_gw_rejection = models.TextField(null=True, blank=True)

    post_gw_inclusions = models.ManyToManyField(Inclusion, related_name="post_gw_inclusions")

    class Meta:
        abstract = True


class GIAGradingMixin(models.Model):
    gia_returned_date = models.DateTimeField(null=True, blank=True)
    # external_id = models.CharField(max_length=11, unique=True, blank=True, null=True)
    # post_gw_final_carat = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    # basic_final_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1)
    # post_gw_final_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True)
    gia_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True)
    post_gia_final_color = models.CharField(choices=ColorGrades.CHOICES, max_length=1, null=True, blank=True)
    gia_material_testing = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        abstract = True


class Stone(GIAGradingMixin, PostGWGradingMixin, GWAIGradingMixin, BasicGradingMixin):
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
            f" {self.internal_id}, {self.basic_final_color}, {self.basic_final_clarity},"
            f" {self.sarine_cut}, {self.culet_size}"
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
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.html import format_html

from customers.models import Entity
from ownerships.models import ParcelTransfer, StoneTransfer


class Split(models.Model):
    original_parcel = models.OneToOneField("Parcel", on_delete=models.PROTECT, primary_key=True)

    split_by = models.ForeignKey(User, on_delete=models.PROTECT)
    split_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Split of {self.original_parcel}"


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

    def get_action_html_link(self):
        # in the future might have to check user permissions here
        if not self.closed_out():
            link = reverse(self.close_url, args=[self.id])
            return format_html(f'<a href="{link}">Close Out</a>')
        return "-"

    get_receipt_with_html_link.short_description = "receipt"
    get_receipt_with_html_link.admin_order_field = "receipt"


class Receipt(AbstractReceipt):
    class Meta:
        verbose_name = "Customer Receipt"


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


class Stone(models.Model):
    data_entry_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="entered_data_for_stone")
    grader_1 = models.ForeignKey(User, on_delete=models.PROTECT, related_name="grader_1_for_stone")
    grader_2 = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="grader_2_for_stone", null=True, blank=True
    )
    grader_3 = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="grader_3_for_stone", null=True, blank=True
    )
    sequence_number = models.IntegerField()
    stone_id = models.CharField(max_length=15)
    carats = models.DecimalField(max_digits=5, decimal_places=3)
    color = models.CharField(max_length=1)
    grader_1_color = models.CharField(max_length=1, blank=True)
    grader_2_color = models.CharField(max_length=1, blank=True)
    grader_3_color = models.CharField(max_length=1, blank=True)
    clarity = models.CharField(max_length=4)
    grader_1_clarity = models.CharField(max_length=4, blank=True)
    grader_2_clarity = models.CharField(max_length=4, blank=True)
    grader_3_clarity = models.CharField(max_length=4, blank=True)
    fluo = models.CharField(max_length=4)
    culet = models.CharField(max_length=2)
    inclusion_remarks = models.TextField(blank=True)
    grader_1_inclusion = models.TextField(blank=True)
    grader_2_inclusion = models.TextField(blank=True)
    grader_3_inclusion = models.TextField(blank=True)
    rejection_remarks = models.TextField(blank=True)

    split_from = models.ForeignKey(Split, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f"{self.stone_id} ({self.carats}ct {self.color} {self.clarity})"

    def current_location(self):
        return StoneTransfer.get_current_location(self)

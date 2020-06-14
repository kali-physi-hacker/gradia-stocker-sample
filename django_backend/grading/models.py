from django.contrib.auth.models import User
from django.db import models

from customers.models import Entity
from ownerships.models import ParcelTransfer, SplitParcelTransfer


class AbstractReceipt(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    code = models.CharField(max_length=15)
    intake_date = models.DateTimeField(auto_now_add=True)
    release_date = models.DateTimeField(null=True, blank=True)
    intake_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="signed_off_on_stone_intake")
    release_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="signed_off_on_stone_release", null=True, blank=True
    )

    def __str__(self):
        return "receipt " + self.code

    class Meta:
        abstract = True

    def closed_out(self):
        return self.release_by is not None and self.release_date is not None

    closed_out.boolean = True


class Receipt(AbstractReceipt):
    pass


class AbstractParcel(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT)
    code = models.CharField(max_length=15)

    total_carats = models.DecimalField(max_digits=5, decimal_places=3)
    total_pieces = models.IntegerField()

    def __str__(self):
        return f"parcel {self.code} ({self.total_carats}ct, {self.total_pieces}pcs, {self.receipt})"

    class Meta:
        abstract = True


class Parcel(AbstractParcel):
    def current_owner(self):
        most_recent = ParcelTransfer.most_recent_transfer(self)
        ownership = [most_recent.to_user]
        if most_recent.in_transit():
            ownership.append("unconfirmed")
        if most_recent.expired:
            ownership.append("expired")
        if len(ownership) == 1:
            ownership.append("confirmed")

        return ownership


class SplitParcel(models.Model):
    parcel = models.ForeignKey(Parcel, on_delete=models.PROTECT)
    split_parcel_code = models.CharField(max_length=15)
    total_carats = models.DecimalField(max_digits=5, decimal_places=3)
    total_pieces = models.IntegerField()

    split_by = models.ForeignKey(User, on_delete=models.PROTECT)
    split_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.split_parcel_code}"

    def current_owner(self):
        most_recent = SplitParcelTransfer.most_recent_transfer(self)
        ownership = [most_recent.to_user]
        if most_recent.in_transit():
            ownership.append("unconfirmed")
        if most_recent.expired:
            ownership.append("expired")
        if len(ownership) == 1:
            ownership.append("confirmed")

        return ownership


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

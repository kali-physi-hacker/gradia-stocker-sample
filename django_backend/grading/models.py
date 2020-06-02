from django.contrib.auth.models import User
from django.db import models

from customers.models import Entity


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
    name = models.CharField(max_length=15)
    code = models.CharField(max_length=15)

    total_carats = models.DecimalField(max_digits=5, decimal_places=3)
    total_pieces = models.IntegerField()

    def __str__(self):
        return f"parcel {self.name} ({self.total_carats}ct, {self.total_pieces}pcs, {self.receipt})"

    class Meta:
        abstract = True


class Parcel(AbstractParcel):
    pass

from django.contrib.auth.models import User
from django.db import models

from customers.models import AbstractAuthorizedPersonnel, AbstractEntity
from grading.models import AbstractParcel, AbstractReceipt


class Seller(AbstractEntity):
    pass


class AuthorizedPersonnel(AbstractAuthorizedPersonnel):
    entity = models.ForeignKey(Seller, on_delete=models.PROTECT)


class Receipt(AbstractReceipt):
    entity = models.ForeignKey(Seller, on_delete=models.PROTECT)
    intake_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="signed_off_on_stone_purchase_intake")
    release_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="signed_off_on_stone_purchase_release", null=True, blank=True
    )


class Parcel(AbstractParcel):
    receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT)
    code = models.CharField(max_length=15)

    rejected_carats = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    rejected_pieces = models.IntegerField(null=True, blank=True)

    reference_price_per_carat = models.PositiveIntegerField()
    total_price_paid = models.IntegerField(null=True, blank=True)

    def closed_out(self):
        return (self.rejected_pieces is not None) and (self.total_price_paid is not None)

    closed_out.boolean = True

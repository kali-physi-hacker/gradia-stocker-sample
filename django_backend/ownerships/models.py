from django.contrib.auth.models import User
from django.db import models


class AbstractTransfer(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="gave_parcels")
    initiated_date = models.DateTimeField(auto_now_add=True)
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="received_parcels")
    confirmed_date = models.DateTimeField(blank=True, null=True)
    expired = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    def in_transit(self):
        return self.confirmed_date is None

    @classmethod
    def most_recent_transfer(cls, item):
        try:
            return cls.objects.filter(item=item).latest("initiated_date")
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_current_holding(cls, user):
        try:
            latest_holding = cls.objects.filter(to_user=user).latest("initiated_date")
        except cls.DoesNotExist:
            return None
        if latest_holding.expired:
            return None
        return latest_holding.item

    @classmethod
    def initiate_transfer(cls, item, from_user, to_user):
        last_transfer = cls.most_recent_transfer(item)
        assert last_transfer.to_user == from_user, "you are not the current owner"
        assert last_transfer.to_user != to_user, "you are transferring to yourself"
        assert not last_transfer.expired, "your ownership is stale- you may not currently own this item"
        assert not last_transfer.in_transit(), "have not confirmed transfer yet"

        cls.objects.create(item=last_transfer.item, from_user=from_user, to_user=to_user)
        last_transfer.expired = True
        last_transfer.save()

    def __str__(self):
        return f"{self.item}: {self.from_user} -> {self.to_user}"


class ParcelTransfer(AbstractTransfer):
    item = models.ForeignKey("grading.Parcel", on_delete=models.PROTECT)


class SplitParcelTransfer(AbstractTransfer):
    item = models.ForeignKey("grading.SplitParcel", on_delete=models.PROTECT)

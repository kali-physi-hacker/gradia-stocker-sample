from django.contrib.auth.models import User
from django.db import models


class ParcelTransfer(models.Model):
    parcel = models.ForeignKey("grading.Parcel", on_delete=models.PROTECT)
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="gave_parcels")
    initiated_date = models.DateTimeField(auto_now_add=True)
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="received_parcels")
    confirmed_date = models.DateTimeField(blank=True, null=True)
    expired = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.parcel}: {self.from_user} -> {self.to_user}"

    def in_transit(self):
        return self.confirmed_date is None

    @classmethod
    def most_recent_transfer(cls, parcel):
        try:
            return cls.objects.filter(parcel=parcel).latest("initiated_date")
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
        return latest_holding.parcel

    @classmethod
    def initiate_transfer(cls, parcel, from_user, to_user):
        last_transfer = cls.most_recent_transfer(parcel)
        assert last_transfer.to_user == from_user, "you are not the current owner"
        assert last_transfer.to_user != to_user, "you are transferring to yourself"
        assert not last_transfer.expired, "your ownership is stale- you may not currently own this parcel"
        assert not last_transfer.in_transit(), "have not confirmed transfer yet"

        cls.objects.create(parcel=last_transfer.parcel, from_user=from_user, to_user=to_user)
        parcel.expired = True
        parcel.save()

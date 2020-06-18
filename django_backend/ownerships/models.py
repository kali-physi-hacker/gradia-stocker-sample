from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class AbstractItemTransfer(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="gave_parcels")
    initiated_date = models.DateTimeField(auto_now_add=True)
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="received_parcels")
    confirmed_date = models.DateTimeField(blank=True, null=True)
    fresh = models.BooleanField(default=True)
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
        if not latest_holding.fresh:
            return None
        return latest_holding.item

    @classmethod
    def can_create_transfer(cls, item, from_user, to_user):
        last_transfer = cls.most_recent_transfer(item)
        if last_transfer.to_user != from_user:
            raise "you are not the current owner"
        if last_transfer.to_user == to_user:
            raise "you are transferring to yourself"
        if not last_transfer.fresh:
            raise "your ownership is stale- you may not currently own this item"
        if last_transfer.in_transit():
            raise "have not confirmed transfer yet"

    @classmethod
    def initiate_transfer(cls, item, from_user, to_user):
        last_transfer = cls.most_recent_transfer(item)

        cls.can_create_transfer(item, from_user, to_user)

        cls.objects.create(item=last_transfer.item, from_user=from_user, to_user=to_user)
        last_transfer.fresh = False
        last_transfer.save()

    @classmethod
    def can_confirm_received(cls, item, user):
        owner, status = item.current_location()
        if owner != user:
            if not (owner.username == "vault" and user.username in ["anthony", "admin", "gary"]):
                raise f"you are not in possession of the parcel- it should be with {owner}"
        if status != "unconfirmed":
            raise f"You are in possession of the parcel but its status shows up as {status} so you cannot confirm it"

    @classmethod
    def confirm_received(cls, item):
        last_transfer = cls.most_recent_transfer(item)
        cls.can_confirm_received(item, last_transfer.to_user)
        last_transfer.confirmed_date = datetime.now()
        last_transfer.save()

    def __str__(self):
        return f"{self.item}: {self.from_user} -> {self.to_user}"


class ParcelTransfer(AbstractItemTransfer):
    item = models.ForeignKey("grading.Parcel", on_delete=models.PROTECT)


class StoneTransfer(AbstractItemTransfer):
    item = models.ForeignKey("grading.Stone", on_delete=models.PROTECT)

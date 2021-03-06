from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Q
from django.utils.timezone import utc


class AbstractItemTransfer(models.Model):
    initiated_date = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="gave_parcels")
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="received_parcels")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_parcels")
    confirmed_date = models.DateTimeField(blank=True, null=True)
    fresh = models.BooleanField(default=True)
    remarks = models.TextField(blank=True)

    def in_transit(self):
        return self.confirmed_date is None

    class Meta:
        abstract = True

    @classmethod
    def most_recent_transfer(cls, item):
        try:
            return cls.objects.filter(item=item).latest("initiated_date")
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_current_location(cls, item):
        most_recent = cls.most_recent_transfer(item)
        location = [most_recent.to_user]
        if not most_recent.fresh:
            location.append("expired")
        if most_recent.in_transit():
            location.append("unconfirmed")
        if len(location) == 1:
            location.append("confirmed")
        return location

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
        split = User.objects.get(username="split")
        last_transfer = cls.most_recent_transfer(item)
        if last_transfer.to_user != from_user and to_user != split:
            raise PermissionDenied(
                f"you are not the current owner, only the user signed in as {last_transfer.to_user} can do this"
            )
        if last_transfer.to_user == to_user:
            raise PermissionDenied("you are creating a transfer from yourself to yourself")
        if not last_transfer.fresh:
            raise PermissionDenied(
                "even though the most recent transfer is to you, your ownership "
                "is stale- you may not currently own this item. did you split it?"
            )
        if last_transfer.in_transit():
            raise PermissionDenied(
                "you have not confirmed you received this item yet, so you cannot transfer it away"
            )

    @classmethod
    def initiate_transfer(cls, item, from_user, to_user, created_by, remarks=""):
        last_transfer = cls.most_recent_transfer(item)

        cls.can_create_transfer(item, from_user, to_user)
        last_transfer.fresh = False
        last_transfer.save()

        created = cls.objects.create(
            item=last_transfer.item, from_user=from_user, to_user=to_user, remarks=remarks, created_by=created_by
        )
        return created

    @classmethod
    def can_confirm_received(cls, item, user):
        owner, status = item.current_location()
        if owner != user:
            if owner.username == "vault" and user.groups.filter(name="vault_manager").exists():
                # okay if it is to vault and user is a vault manager
                pass
            else:
                raise PermissionDenied(
                    f"you are not in possession of the parcel- it is currently with {owner}, "
                    "so you cannot confirm you have received it"
                )
        if status != "unconfirmed":
            raise PermissionDenied(
                f"You are in possession of the parcel but its status shows up as {status} so you cannot confirm it"
            )

    @classmethod
    def confirm_received(cls, item):
        last_transfer = cls.most_recent_transfer(item)
        cls.can_confirm_received(item, last_transfer.to_user)
        last_transfer.confirmed_date = datetime.utcnow().replace(tzinfo=utc)
        last_transfer.save()

    def __str__(self):
        return f"{self.item}: {self.from_user} -> {self.to_user}"


class ParcelTransfer(AbstractItemTransfer):
    item = models.ForeignKey("grading.Parcel", on_delete=models.PROTECT)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item"], condition=Q(fresh=True), name="only_one_fresh_transfer_per_parcel"
            )
        ]


class StoneTransfer(AbstractItemTransfer):
    item = models.ForeignKey("grading.Stone", on_delete=models.PROTECT)
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="gave_stones")
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="received_stones")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_stones")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item"], condition=Q(fresh=True), name="only_one_fresh_transfer_per_stone"
            )
        ]

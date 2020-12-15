import json
import os

from django.contrib.auth.models import User

from grading.models import Parcel, Split, Stone
from ownerships.models import ParcelTransfer, StoneTransfer

split_user = User.objects.get(username="split")
admin_user = User.objects.get(username="gradialab")
vault_user = User.objects.get(username="vault")

# bootstrap the first transfer for all parcels
for parcel in Parcel.objects.all():
    if parcel.split_from is None:
        transfer = ParcelTransfer.objects.create(
            item=parcel, fresh=True, from_user=admin_user, to_user=vault_user, created_by=admin_user
        )
        ParcelTransfer.confirm_received(parcel)
    else:
        transfer = ParcelTransfer.objects.create(
            item=parcel, fresh=True, from_user=split_user, to_user=vault_user, created_by=admin_user
        )
        ParcelTransfer.confirm_received(parcel)

# split parcels also have a second transfer
for split in Split.objects.all():
    original_location, status = split.original_parcel.current_location()
    assert status == "confirmed"
    ParcelTransfer.initiate_transfer(split.original_parcel, original_location, split_user, admin_user)
    ParcelTransfer.confirm_received(split.original_parcel)

# create stones
migrate_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(migrate_dir, "old_stones.json")) as f:
    stones_json = json.load(f)

for s_json in stones_json:
    fields = s_json["fields"]
    fields["data_entry_user"] = User.objects.get(pk=fields["data_entry_user"])
    fields["grader_1"] = User.objects.get(pk=fields["grader_1"])
    if fields["grader_2"] is not None:
        fields["grader_2"] = User.objects.get(pk=fields["grader_2"])
    if fields["grader_3"] is not None:
        fields["grader_3"] = User.objects.get(pk=fields["grader_3"])
    fields["split_from"] = Split.objects.get(pk=fields["split_from"])
    del fields["inclusion_remarks"]
    del fields["grader_1_inclusion"]
    del fields["grader_2_inclusion"]
    del fields["grader_3_inclusion"]

    stone = Stone.objects.create(**fields)

    # they were all created from splitting
    transfer = StoneTransfer.objects.create(
        item=stone, fresh=True, from_user=split_user, to_user=vault_user, created_by=admin_user
    )
    StoneTransfer.confirm_received(stone)

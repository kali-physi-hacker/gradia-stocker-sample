from django.contrib import admin
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from customers.models import Entity
from grading.models import Parcel, Receipt

from ..models import ParcelTransfer


class ParcelTransferTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user")
        created_receipt = Receipt.objects.create(
            entity=Entity.objects.create(name="Van Klaren", address="addressy", phone="12345678", email="vk@vk.com"),
            code="VK-0001",
            intake_by=self.user,
        )
        self.parcel = Parcel.objects.create(
            receipt=created_receipt,
            gradia_parcel_code="VK20200701",
            customer_parcel_code="cust-parcel-1",
            total_carats=2,
            total_pieces=2,
            reference_price_per_carat=1,
        )
        self.transfer = ParcelTransfer.objects.create(
            item=self.parcel, fresh=True, from_user=self.user, to_user=self.user
        )

    def test_registered_in_admin(self):
        self.assertTrue(admin.site.is_registered(ParcelTransfer))

    def test_cannot_create_multiple_fresh_parcel_transfers(self):
        # can create many non-fresh parcels
        ParcelTransfer.objects.create(item=self.parcel, fresh=False, from_user=self.user, to_user=self.user)
        ParcelTransfer.objects.create(item=self.parcel, fresh=False, from_user=self.user, to_user=self.user)
        # but cannot create fresh parcel
        with self.assertRaises(IntegrityError):
            ParcelTransfer.objects.create(item=self.parcel, fresh=True, from_user=self.user, to_user=self.user)

    def test_has_useful_repr(self):
        self.assertEqual(str(self.transfer), "parcel VK20200701 (2ct, 2pcs, receipt VK-0001): user -> user")

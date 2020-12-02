import os

from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient

from grading.models import Stone, Split, Parcel


class TestCSVUpload(TestCase):
    def setUp(self):
        receipt_number = "s1o2m3e_r4a5n6d7m_n8u9m0b1e2r"

        self.basic_grading_url = reverse("basic_grading")
        self.GW_url = reverse("GW", args=(receipt_number,))
        self.post_GW_checks_url = reverse("post_GW_checks", args=(receipt_number,))
        self.GIA_url = reverse("GIA", args=(receipt_number,))

        self.csv_file = open("parcelABC123.csv", "r")
        self.gradia_parcel_code = "parcelABC123"
        self.invalid_csv_file = open("invalid.csv", "r")

        self.parcel = Parcel.objects.get(gradia_parcel_code=self.gradia_parcel_code)

        self.client = APIClient()

    def test_views_basic_grading_uploads_with_valid_in_csv_file_fields_and_returns_201(self):
        response = self.client.post(self.basic_grading_url, {"file": self.csv_file})
        self.assertEqual(response.status, 201)
        # self.assertEqual(response.json()["message"], "Data upload successful")

        # After upload of 50 entries, 50 stones and parcels should be created

        # TODO: Splitting
        #  1. Get an existing parcel name
        #  2. Create stones from the csv rows using the parcel name of the csv file
        #  3. Add an entry to the Split table
        #  4

        # TODO: What Question I have left
        #  The Calendar

        stones = Stone.objects.all()
        self.assertEqual(len(stones), 50)

        split = Split.objects.filter(original_parcel=self.parcel)

        stones_truth = all(stone.split_from == split for stone in stones)
        self.assertTrue(stones_truth)

    def test_views_basic_grading_does_not_upload_and_returns_400_with_invalid_csv_file_fields(self):
        response = self.client.post(self.basic_grading_url, {"file": self.invalid_csv_file})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"],
                         "Invalid field name(s)")  # Will be modified later to make it more clear

    def test_views_basic_grading_does_not_upload_and_returns_400_with_invalid_csv_file_field_values(self):
        pass

    def test_views_basic_grading_returns_404_if_parcel_name_not_found(self):
        pass

    def test_views_GW_uploads_with_valid_csv_file_fields_and_returns_201(self):
        pass

    def test_views_GW_does_not_upload_and_returns_400_with_invalid_csv_file_fields(self):
        pass

    def test_views_GW_does_not_upload_and_returns_400_with_invalid_csv_file_field_values(self):
        pass

    def test_views_GW_returns_404_if_receipt_reference_number_not_found(self):
        pass

    def test_views_post_GW_checks_uploads_with_valid_csv_file_fields_and_returns_201(self):
        pass

    def test_views_post_GW_checks_does_not_upload_and_returns_400_with_invalid_csv_file_fields(self):
        pass

    def test_views_post_GW_checks_does_not_upload_and_returns_400_with_invalid_csv_file_field_values(self):
        pass

    def test_views_post_GW_checks_returns_404_if_receipt_reference_number_not_found(self):
        pass

    def test_views_GIA_uploads_with_valid_csv_file_fields_and_returns_201(self):
        pass

    def test_views_GIA_does_not_upload_and_returns_400_with_invalid_csv_file_fields(self):
        pass

    def test_views_GIA_does_not_upload_and_returns_400_with_invalid_csv_file_field_values(self):
        pass

    def test_views_GIA_returns_404_if_receipt_reference_number_not_found(self):
        pass

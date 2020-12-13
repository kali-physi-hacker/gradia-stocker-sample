import os

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from grading.models import Stone, Split, Parcel


User = get_user_model()


class TestCSVUpload(TestCase):

    fixtures = ("grading/tests/fixtures/basic_grading_fixtures.json", "grading/tests/fixtures/default_users.json")

    def setUp(self):
        receipt_number = "012345689"

        self.basic_grading_url = reverse("grading:upload_parcel_csv")
        # self.GW_url = reverse("GW", args=(receipt_number,))
        # self.post_GW_checks_url = reverse("post_GW_checks", args=(receipt_number,))
        # self.GIA_url = reverse("GIA", args=(receipt_number,))

        self.csv_file = open("grading/tests/fixtures/123456789.csv", "r")
        self.gradia_parcel_code = "123456789"
        self.invalid_csv_file = open("grading/tests/fixtures/invalid.csv", "r")

        self.parcel = Parcel.objects.get(gradia_parcel_code=self.gradia_parcel_code)
        
    def test_views_basic_grading_uploads_with_valid_in_csv_file_fields_and_returns_201(self):

        self.client.login(username="graderuser", password="Passw0rd!")
        response = self.client.post(self.basic_grading_url, {"file": self.csv_file})
        self.assertEqual(response.status_code, 302)

        stones = Stone.objects.all()
        self.assertEqual(len(stones), 19)

        split = Split.objects.get(original_parcel=self.parcel)

        # This is a python idiom and a generator is returned which is
        # a performance gain over a native loop
        # truth = all(stone.split_from == split for stone in stones)
        # self.assertTrue(truth)

        for stone in stones:
            self.assertEqual(stone.split_from, split)

    def test_views_basic_grading_does_not_upload_and_returns_400_with_invalid_csv_file_fields(self):
        response = self.client.post(self.basic_grading_url, {"file": self.invalid_csv_file})

        self.assertEqual(response.status_code, 302)

        stones = Stone.objects.all()
        self.assertEqual(len(stones), 0)

    def test_views_basic_csv_upload_generates_basic_id_hash(self):
        """
        Tests that basic csv upload generates id hashing
        :return:
        """
        self.client.login(username="graderuser", password="Passw0rd!")
        self.client.post(self.basic_grading_url, {"file": self.csv_file})

        stone = Stone.objects.all()[0]
        self.assertIsNotNone(stone.external_id)

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

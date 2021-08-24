from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import pandas as pd

from grading.models import Parcel, Split, Stone


User = get_user_model()


class TestCSVUpload(TestCase):

    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        # receipt_number = "012345689"

        self.basic_grading_url = reverse("grading:upload_parcel_csv")
        self.sarine_data_upload_url = reverse("grading:sarine_data_upload_url")
        # self.GW_url = reverse("GW", args=(receipt_number,))
        # self.post_GW_checks_url = reverse("post_GW_checks", args=(receipt_number,))
        # self.GIA_url = reverse("GIA", args=(receipt_number,))

        self.sarine_upload_csv_file = open("grading/tests/fixtures/sarine-01.csv", "r")
        self.gradia_parcel_code = "sarine-01"
        self.invalid_csv_file = open("grading/tests/fixtures/invalid.csv", "r")

        self.parcel = Parcel.objects.get(gradia_parcel_code=self.gradia_parcel_code)

        self.grader = {"username": "gary", "password": "password"}
        # delete the already existing stone
        # Stone.objects.first().delete()

    def test_sarine_data_upload_get_page(self):
        """
        Tests that sarine data upload get page returns 200
        :return:
        """
        template_title = "Upload a csv file containing sarine data"
        self.client.login(**self.grader)
        response = self.client.get(reverse("grading:sarine_data_upload_url"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(template_title, response.content.decode())
        button = '<input type="submit" value="Upload CSV" class="default" name="_upload"/>'
        self.assertIn(button, response.content.decode())

    def test_sarine_data_upload_success_if_valid_csv(self):
        """
        Tests that sarine data can be uploaded successfully if the csv file is valid
        :return:
        """
        Stone.objects.all().delete()
        self.client.login(username="gary", password="password")
        response = self.client.post(self.sarine_data_upload_url, {"file": self.sarine_upload_csv_file})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Stone.objects.count(), 3)

    def xtest_views_basic_grading_uploads_with_valid_in_csv_file_fields_and_returns_201(self):
        self.client.login(username="gary", password="password")
        response = self.client.post(self.basic_grading_url, {"file": self.csv_file})
        self.assertEqual(response.status_code, 302)
        stones = Stone.objects.all()
        self.assertEqual(len(stones), 14)

        split = Split.objects.get(original_parcel=self.parcel)

        # This is a python idiom and a generator is returned which is
        # a performance gain over a native loop
        # truth = all(stone.split_from == split for stone in stones)
        # self.assertTrue(truth)

        for stone in stones:
            self.assertEqual(stone.split_from, split)

    def xtest_views_basic_grading_does_not_upload_and_returns_400_with_invalid_csv_file_fields(self):
        response = self.client.post(self.basic_grading_url, {"file": self.invalid_csv_file})
        self.assertEqual(response.status_code, 302)

        stones = Stone.objects.all()
        self.assertEqual(len(stones), 0)

    def xtest_views_basic_csv_upload_generates_basic_id_hash(self):
        """
        Tests that basic csv upload generates id hashing
        :return:
        """
        # Before Upload Check that all external IDs from CSV file is None
        data = pd.read_csv(self.csv_file)
        self.csv_file.close()
        external_ids = pd.DataFrame(data, columns=("external_id",))

        for external_id in external_ids.values:
            self.assertTrue(pd.isna(external_id[0]))

        # Reopen file and upload ===> Cursor reached end after above action
        self.csv_file = open("grading/tests/fixtures/123456789.csv", "r")
        self.client.login(username="gary", password="password")
        self.client.post(self.basic_grading_url, {"file": self.csv_file})

        # Check that all uploaded stones have external_ids
        for stone in Stone.objects.all():
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

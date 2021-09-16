from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages.api import get_messages

from stonegrading.models import Inclusion

import pandas as pd
from grading.views import BasicGradingUploadView

from grading.models import Parcel, Split, Stone


User = get_user_model()


class TestCSVUpload(TestCase):

    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.sarine_data_upload_url = reverse("grading:sarine_data_upload_url")
        self.basic_grading_data_upload_url = reverse("grading:basic_grading_data_upload_url")

        self.sarine_upload_csv_file = open("grading/tests/fixtures/sarine-01.csv", "r")
        self.gradia_parcel_code = "sarine-01"
        self.invalid_csv_file = open("grading/tests/fixtures/no-parcel.csv", "r")

        self.basic_grading_upload_csv_file = open("grading/tests/fixtures/basic-01.csv", "r")

        self.parcel = Parcel.objects.get(gradia_parcel_code=self.gradia_parcel_code)

        self.grader = {"username": "gary", "password": "password"}

    def setup_sarine_data(self):
        Stone.objects.all().delete()
        self.client.login(**self.grader)
        response = self.client.post(self.sarine_data_upload_url, {"file": self.sarine_upload_csv_file})

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
        self.client.login(**self.grader)
        response = self.client.post(self.sarine_data_upload_url, {"file": self.sarine_upload_csv_file})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Stone.objects.count(), 3)

    def xtest_sarine_data_upload_fails_if_invalid_csv_filename(self):
        """
        Tests that sarine data upload endpoint errors if invalid csv file
        Format: ==> We're expecting that csv filename to be equal to gradia_parcel_code
        returns:
        """
        self.client.login(**self.grader)
        response = self.client.post(reverse("grading:sarine_data_upload_url"), {"file": self.invalid_csv_file})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("grading:sarine_data_upload_url"))
        request = response.wsgi_request
        django_messages = get_messages(request)
        self.assertEqual(len(django_messages), 1)
        for message in django_messages:
            self.assertEqual(str(message), "Parcel name does not exist")

    def xtest_sarine_data_upload_fails_field_names_missing(self):
        self.client.login(**self.grader)
        response = self.client.post(reverse("grading:sarine_data_upload_url"), {"file": self.invalid_csv_file})
        self.assertEqual(response.status_code, 302)

    def test_basic_grading_data_upload_get_page(self):
        """
        Tests that basic grading upload get page returns 200
        :return:
        """
        template_title = "Upload a csv file containing basic grading data"
        self.client.login(**self.grader)
        response = self.client.get(reverse("grading:basic_grading_data_upload_url"))
        self.assertEqual(response.status_code, 200)
        self.assertIn(template_title, response.content.decode())
        button = '<input type="submit" value="Upload CSV" class="default" name="_upload"/>'
        self.assertIn(button, response.content.decode())

    def test_basic_grading_data_upload_success_if_valid_csv(self):
        """
        Tests that basic grading data can be uploaded successfully if the csv file is valid
        :return:
        """
        Stone.objects.all().delete()
        self.setup_sarine_data()
        self.client.login(**self.grader)
        response = self.client.post(self.basic_grading_data_upload_url, {"file": self.basic_grading_upload_csv_file})
        self.assertEqual(response.status_code, 302)
        stone_1 = Stone.objects.get(internal_id=1)
        # float() because django will return a Decimal of 0.090
        self.assertEqual(float(stone_1.basic_carat), 0.09)

    def test_basic_grading_view_process_users(self):
        graders = {"basic_grader_1": "gary", "basic_grader_2": None, "basic_grader_3": None}
        result = BasicGradingUploadView._process_graders(self=None, data_dict=graders)
        self.assertEqual(result["basic_grader_1"], User.objects.get(username="gary"))

        graders = {"basic_grader_1": "Not-Exist-User", "basic_grader_2": None, "basic_grader_3": None}
        result = BasicGradingUploadView._process_graders(self=None, data_dict=graders)
        self.assertEqual(result["basic_grader_1"], None)

    def test_basic_grading_view_process_inclusions(self):
        """
        Tests that _process_inclusions returns desired inclusion dictionary object
        """
        inclusions = {
            "basic_inclusions_1": "Br, Cv, Ch",
            "basic_inclusions_2": "Clv, Cld, Xtl",
            "basic_inclusions_3": "Clv, Cv, Br",
            "basic_inclusions_final": "Br, Cv, Ch",
        }
        basic_inclusions_1 = [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Br", "Cv", "Ch")]
        basic_inclusions_2 = [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Clv", "Cld", "Xtl")]
        basic_inclusions_3 = [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Clv", "Cv", "Br")]
        basic_inclusions_final = [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Br", "Cv", "Ch")]

        processed_inclusions = BasicGradingUploadView._process_inclusions(self=None, data_dict=inclusions)

        self.assertEqual(basic_inclusions_1, processed_inclusions["basic_inclusions_1"])
        self.assertEqual(basic_inclusions_2, processed_inclusions["basic_inclusions_2"])
        self.assertEqual(basic_inclusions_3, processed_inclusions["basic_inclusions_3"])
        self.assertEqual(basic_inclusions_final, processed_inclusions["basic_inclusions_final"])

    def xtest_views_basic_csv_upload_generates_basic_id_hash(self):
        """
        Tests that basic csv upload generates id hashing
        :return:
        """
        # upload sarine file
        Stone.objects.all().delete()
        self.setup_sarine_data()

        # Before Upload Check that all external IDs from CSV file is None (not in use because no such column)
        # basic_grading_data = pd.read_csv(self.basic_grading_upload_csv_file)
        # self.basic_grading_upload_csv_file.close()
        # external_ids = pd.DataFrame(basic_grading_data, columns=("external_id",))

        # for external_id in external_ids.values:
        #     self.assertTrue(pd.isna(external_id[0]))

        # uploads basic grading csv
        self.client.login(**self.grader)
        self.client.post(self.basic_grading_data_upload_url, {"file": self.basic_grading_upload_csv_file})

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

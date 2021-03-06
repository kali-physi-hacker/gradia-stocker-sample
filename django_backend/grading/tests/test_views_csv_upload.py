import re
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.contrib.messages.api import get_messages

from grading.models import Parcel, Split, Stone
from ownerships.models import StoneTransfer


User = get_user_model()


class TestCSVUpload(TestCase):

    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.sarine_data_upload_url = reverse("grading:sarine_data_upload_url")
        self.basic_grading_data_upload_url = reverse("grading:basic_grading_data_upload_url")
        self.gw_data_upload_url = reverse("grading:gw_data_upload_url")

        self.sarine_upload_csv_file = open("grading/tests/fixtures/sarine-01.csv", "r")
        self.basic_upload_csv_file = open("grading/tests/fixtures/basic-01.csv", "r")

        self.gradia_parcel_code = "sarine-01"
        self.invalid_csv_file = open("grading/tests/fixtures/no-parcel.csv", "r")

        self.basic_grading_upload_csv_file = open("grading/tests/fixtures/basic-01.csv", "r")
        self.gw_data_upload_csv_file = open("grading/tests/fixtures/gold_way-01.csv", "r")

        self.parcel = Parcel.objects.get(gradia_parcel_code=self.gradia_parcel_code)

        self.grader = {"username": "vault", "password": "password"}

    def setup_sarine_data(self):
        Stone.objects.all().delete()
        self.client.login(**self.grader)
        response = self.client.post(self.sarine_data_upload_url, {"file": self.sarine_upload_csv_file})

    def setup_basic_data(self):
        self.client.login(**self.grader)
        response = self.client.post(self.basic_grading_data_upload_url, {"file": self.basic_upload_csv_file})

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

    def test_sarine_data_upload_fails_if_invalid_csv_filename(self):
        """
        Tests that sarine data upload endpoint errors if invalid csv file
        Format: ==> We're expecting that csv filename to be equal to gradia_parcel_code
        returns:
        """
        self.client.login(**self.grader)
        response = self.client.post(reverse("grading:sarine_data_upload_url"), {"file": self.invalid_csv_file})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "grading/csv_errors.html")
        has_error_message = (
            response.content.decode().find(
                "No parcel with such a parcel code. Please be sure the csv file name matches the parcel code"
            )
            != -1
        )
        self.assertTrue(has_error_message)

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

    def test_gw_grading_data_upload_get_page(self):
        """
        Tests that gold way grading upload get page returns 200
        :return:
        """
        template_title = "Upload a csv file containing gold way grading data"
        self.client.login(**self.grader)
        response = self.client.get(self.gw_data_upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(template_title, response.content.decode())
        button = '<input type="submit" value="Upload CSV" class="default" name="_upload"/>'
        self.assertIn(button, response.content.decode())

    def test_gw_grading_data_upload_success_if_valid_csv(self):

        Stone.objects.all().delete()
        self.setup_sarine_data()
        self.setup_basic_data()
        self.client.login(**self.grader)

        # Confirm and transfer stones
        for stone_id in (1, 5, 6):
            stone = Stone.objects.get(internal_id=stone_id)
            split = User.objects.get(username="split")
            goldway = User.objects.get(username="goldway")
            vault = User.objects.get(username="vault")

            StoneTransfer.initiate_transfer(item=stone, from_user=split, to_user=goldway, created_by=vault)
            StoneTransfer.confirm_received(item=stone)

        response = self.client.post(self.gw_data_upload_url, {"file": self.gw_data_upload_csv_file})
        self.assertEqual(response.status_code, 302)
        stone_1 = Stone.objects.get(internal_id=1)

    def test_gia_adjusting_upload_success(self):
        """
        Tests that GIAGrading Results can be uploaded successfully
        :return:
        """
        csv_file = open("grading/tests/fixtures/gia_adjusting.csv", "rb")
        self.client.login(**self.grader)
        self.setup_sarine_data()
        response = self.client.post(reverse("grading:gia_adjusting_data_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(re.match(r"^/admin/grading/split/\d+/change/", response.url))

    def test_gia_adjusting_upload_failed(self):
        """
        Tests that GIAGrading Results failed if invalid csv_file
        :return:
        """
        invalid_csv_file = open("grading/tests/fixtures/gia_adjusting_invalid.csv", "rb")
        self.client.login(**self.grader)
        self.setup_sarine_data()
        response = self.client.post(
            reverse("grading:gia_adjusting_data_upload_url"), data={"file": invalid_csv_file}
        )
        self.assertEqual(response.status_code, 200)
        has_error_message = response.content.decode().find("Data Upload Failed") != -1
        self.assertTrue(has_error_message)

    def test_macro_file_name_upload_success(self):

        self.csv_file = open("grading/tests/fixtures/macro_image.csv")
        Stone.objects.all().delete()
        self.setup_sarine_data()

        # Generate external_id for stones
        for stone in Stone.objects.all():
            stone.generate_triple_verified_external_id()
            stone.save()

        self.client.login(**self.grader)
        response = self.client.post(reverse("grading:macro_filename"), {"file": self.csv_file})
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(re.match(r"^/admin/grading/split/\d+/change/", response.url))

    def test_macro_file_name_upload_fails(self):

        self.csv_file = open("grading/tests/fixtures/macro_image.csv")
        self.client.login(**self.grader)
        response = self.client.post(reverse("grading:macro_filename"), {"file": self.csv_file})
        self.assertEqual(response.status_code, 200)

    def test_nano_file_name_upload_success(self):

        self.csv_file = open("grading/tests/fixtures/nano_image.csv")

        Stone.objects.all().delete()
        self.setup_sarine_data()
        # Generate external_id for stones
        for stone in Stone.objects.all():
            stone.generate_triple_verified_external_id()
            stone.save()

        self.client.login(**self.grader)
        response = self.client.post(reverse("grading:nano_filename"), {"file": self.csv_file})
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(re.match(r"^/admin/grading/split/\d+/change/", response.url))

    def test_nano_file_name_upload_fails(self):

        self.csv_file = open("grading/tests/fixtures/nano_image.csv")
        self.client.login(**self.grader)
        response = self.client.post(reverse("grading:nano_filename"), {"file": self.csv_file})
        self.assertEqual(response.status_code, 200)

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

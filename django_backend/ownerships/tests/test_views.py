import re

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from grading.forms import SarineUploadForm, BasicUploadForm
from grading.models import Stone, GoldwayVerification


User = get_user_model()


class StoneTransferViews(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.grader_user = {"username": "kary", "password": "password"}
        self.stone_ids = (1, 5, 6)

    def do_initial_uploads(self):
        user = User.objects.get(username="kary")
        sarine_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        form = SarineUploadForm(
            data={}, user=user, files={"file": SimpleUploadedFile(sarine_file.name, sarine_file.read())}
        )
        form.is_valid()
        form.save()

        # Do basic upload
        basic_file = open("grading/tests/fixtures/basic-01.csv", "rb")
        form = BasicUploadForm(
            data={},
            user=user,
            files={"file": SimpleUploadedFile(basic_file.name, basic_file.read())},
        )
        form.is_valid()
        form.save()

        for stone_id in self.stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            stone.gw_verification = GoldwayVerification.objects.create(invoice_number=f'invoice-for-{stone_id}')
            stone.save()


    def test_transfer_to_goldway_success(self):
        self.do_initial_uploads()

        csv_file = open("ownerships/tests/resources/G048RV.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(reverse("ownerships:goldway_transfer_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 200)

        expected_content_ids = []
        with open("ownerships/tests/resources/gia.csv") as csv_file:
            expected_content_ids.extend(csv_file.read().split("\n")[1:])

        expected_content_ids.reverse()

        actual_content = response.content.decode().split("\n")[1:]

        for index, expected_id in enumerate(expected_content_ids):
            stone = Stone.objects.get(internal_id=expected_id)
            internal_id, external_id, basic_carat = actual_content[index].split(",")[1:]
            self.assertEqual(internal_id, expected_id)
            self.assertEqual(external_id, stone.external_id)
            self.assertEqual(float(basic_carat), float(stone.basic_carat))

    def test_transfer_to_goldway_fail(self):
        csv_file = open("ownerships/tests/resources/G048RV.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(reverse("ownerships:goldway_transfer_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 200)

        matches = re.findall(r"Stone With ID `\d+` does not exist", response.content.decode())

        self.assertEqual(len(matches), 3)

        

    def test_transfer_to_gia_success(self):
        self.do_initial_uploads()

        csv_file = open("ownerships/tests/resources/gia.csv")
        self.client.login(**self.grader_user)

        
        response = self.client.post(reverse("ownerships:gia_transfer_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 200)

        expected_content_ids = []
        with open("ownerships/tests/resources/gia.csv") as csv_file:
            expected_content_ids.extend(csv_file.read().split("\n")[1:])

        expected_content_ids.reverse()

        actual_content = response.content.decode().split("\n")[1:]

        for index, expected_id in enumerate(expected_content_ids):
            stone = Stone.objects.get(internal_id=expected_id)
            internal_id, external_id, basic_carat = actual_content[index].split(",")[1:]
            self.assertEqual(internal_id, expected_id)
            self.assertEqual(external_id, stone.external_id)
            self.assertEqual(float(basic_carat), float(stone.basic_carat))

    def test_transfer_to_gia_fail(self):
        csv_file = open("ownerships/tests/resources/gia.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(reverse("ownerships:gia_transfer_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 200)

        matches = re.findall(r"Stone With ID `\d+` does not exist", response.content.decode())

        self.assertEqual(len(matches), 3)

    def test_transfer_to_customer_success(self):
        self.do_initial_uploads()
        customer = User.objects.create(username="Test")
        csv_file = open("ownerships/tests/resources/gia.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(
            reverse("ownerships:external_transfer_url"), data={"file": csv_file, "customer": customer.pk}
        )

        self.assertEqual(response.status_code, 200)  # Does not do a redirect]
        self.assertEqual(response["Content-Type"], "text/csv")

        expected_content_ids = []
        with open("ownerships/tests/resources/gia.csv") as csv_file:
            expected_content_ids.extend(csv_file.read().split("\n")[1:])

        expected_content_ids.reverse()

        actual_content = response.content.decode().split("\n")[1:]

        for index, expected_id in enumerate(expected_content_ids):
            stone = Stone.objects.get(internal_id=expected_id)
            internal_id, external_id, basic_carat = actual_content[index].split(",")[1:]
            self.assertEqual(internal_id, expected_id)
            self.assertEqual(external_id, stone.external_id)
            self.assertEqual(float(basic_carat), float(stone.basic_carat))

    def transfer_to_customer_fail(self):
        customer = User.objects.create(username="Test")
        csv_file = open("ownerships/tests/resources/gia.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(
            reverse("ownerships:external_transfer_url"), data={"file": csv_file, "customer": customer.pk}
        )
        self.assertEqual(response.status_code, 200)

        matches = re.findall(r"Stone With ID `\d+` does not exist", response.content.decode())

        self.assertEqual(len(matches), 3)

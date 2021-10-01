import re

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from grading.forms import SarineUploadForm, BasicUploadForm


User = get_user_model()


class StoneTransferViews(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.grader_user = {"username": "kary", "password": "password"}

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
            files={"file": SimpleUploadedFile(basic_file.name, basic_file.read())},
        )
        form.is_valid()
        form.save()

    def test_transfer_to_goldway_success(self):
        self.do_initial_uploads()
        # Create goldway user
        User.objects.create_user(username="goldway", password="password")

        csv_file = open("ownerships/tests/resources/gw.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(reverse("ownerships:goldway_transfer_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/ownerships/stonetransfer/")

    def test_transfer_to_goldway_fail(self):
        csv_file = open("ownerships/tests/resources/gw.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(reverse("ownerships:goldway_transfer_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 200)

        matches = re.findall(r"Stone With ID `\d+` does not exist", response.content.decode())

        self.assertEqual(len(matches), 3)

    def test_transfer_to_gia_success(self):
        self.do_initial_uploads()
        # Create gia user
        User.objects.create_user(username="gia", password="password")

        csv_file = open("ownerships/tests/resources/gia.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(reverse("ownerships:gia_transfer_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/ownerships/stonetransfer/")

    def test_transfer_to_gia_fail(self):
        csv_file = open("ownerships/tests/resources/gia.csv")
        self.client.login(**self.grader_user)
        response = self.client.post(reverse("ownerships:gia_transfer_upload_url"), data={"file": csv_file})
        self.assertEqual(response.status_code, 200)

        matches = re.findall(r"Stone With ID `\d+` does not exist", response.content.decode())

        self.assertEqual(len(matches), 3)

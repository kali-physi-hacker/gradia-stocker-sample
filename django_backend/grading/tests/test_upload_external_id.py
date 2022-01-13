import csv
import io

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

from grading.forms import SarineUploadForm, BasicUploadForm
from grading.models import Stone


User = get_user_model()


class UploadExternalIdsManagementCommandTest(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.upload_initial_stone_data()
        self.valid_csv_file = "grading/tests/fixtures/valid_upload_ids.csv"
        self.invalid_csv_file = "grading/tests/fixtures/invalid_upload_ids.csv"

    def get_stone_ids_map(self):
        """
        Returns a dict of internal_id:external_id of ids (1, 5, 6)
        :return:
        """
        with open(self.valid_csv_file) as file:
            reader = csv.reader(file)
            header = [head.strip() for head in next(reader)]
            rows = [row for row in reader]

        internal_id_index = header.index("internal_id")
        external_id_index = header.index("external_id")

        data = {row[internal_id_index]: row[external_id_index] for row in rows}
        return data

    def upload_initial_stone_data(self):
        """
        Upload sarine and basic grading results
        :return:
        """
        with open("grading/tests/fixtures/sarine-01.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        form = SarineUploadForm(data={}, files={"file": upload_file}, user=User.objects.get(username="kary"))
        self.assertTrue(form.is_valid())
        form.save()

        with open("grading/tests/fixtures/basic-01.csv", "rb") as csv_file:
            upload_file = SimpleUploadedFile(csv_file.name, csv_file.read())

        form = BasicUploadForm(data={}, files={"file": upload_file}, user=User.objects.get(username="kary"))
        self.assertTrue(form.is_valid())
        form.save()

    def test_external_id_upload_success(self):
        """
        Tests that upload_external_id command works successfully if provided with correct csv file path
        containing valid internal_ids
        :return:
        """

        out = io.StringIO()
        call_command("upload_external_ids", f"-f {self.valid_csv_file}", stdout=out)
        data = self.get_stone_ids_map()

        for internal_id, external_id in data.items():
            stone = Stone.objects.get(internal_id=internal_id)
            self.assertEqual(stone.external_id, external_id)

    def test_external_id_upload_file_does_not_exist(self):
        """
        Tests that upload_external_id command fails if invalid file path
        :return:
        """
        out = io.StringIO()
        with self.assertRaises(CommandError):
            call_command("upload_external_ids", "-f invalid_file_path.csv", stdout=out)

    def test_internal_id_upload_id_does_not_exist(self):
        """
        Tests that upload_external_id command fails if internal_id does not exist
        :return:
        """
        out = io.StringIO()
        with self.assertRaises(CommandError):
            call_command("upload_external_ids", f"-f{self.invalid_csv_file}", stdout=out)

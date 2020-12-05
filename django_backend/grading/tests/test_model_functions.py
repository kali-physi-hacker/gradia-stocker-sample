import csv
from django.test import TestCase
from grading.models import Stone
from grading.helpers import get_model_fields, get_field_names


class TestPdfGeneration(TestCase):
    fixtures = ("data_migration/test_data.json",)

    def setUp(self):
        self.stone1 = Stone.objects.get(internal_id=1)
        self.stone2 = Stone.objects.get(internal_id=1)

    def test_download_id_csv_is_created(self):
        """
        Send File and 200 response status if report id (gradia_ID)
        is valid and exists
        Returns:
        """
        queryset = Stone.objects.all()
        file_path = Stone.objects.download_ids(queryset=queryset)

        file = open(file_path)
        # import pdb; pdb.set_trace()
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            # import pdb; pdb.set_trace()
            self.assertTrue("internal_id" in row)

            break

    def test_master_download(self):

        queryset = Stone.objects.all()
        file_path = Stone.objects.download_master_reports(queryset=queryset)

        file = open(file_path)
        model_fields = get_model_fields(Stone)
        field_names = get_field_names(model_fields)
        # import pdb; pdb.set_trace()
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            # import pdb; pdb.set_trace()
            for field in field_names:
                self.assertTrue(field in row)

            break

    def test_download_to_goldway_csv(self):

        queryset = Stone.objects.all()
        file_path = Stone.objects.download_to_goldway_csv(queryset=queryset)

        file = open(file_path)
        field_names = ["date_to_GW", "internal_id", "basic_carat"]
        # import pdb; pdb.set_trace()
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            # import pdb; pdb.set_trace()
            for field in field_names:
                self.assertTrue(field in row)

            break
import os
import csv
from django.test import TestCase
from grading.models import Stone
from grading.helpers import get_model_fields, get_field_names


class TestPdfGeneration(TestCase):
    fixtures = ("data_migration/test_data.json",)

    def setUp(self):
        self.stone1 = Stone.objects.get(internal_id=1)
        self.stone3 = Stone.objects.get(internal_id=3)

    def test_download_id_csv_is_created(self):
        """
        Send File and 200 response status if report id (gradia_ID)
        is valid and exists
        Returns:
        """
        queryset = Stone.objects.all()
        file_path = Stone.objects.download_ids(queryset=queryset)
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            csv_list = list(reader)
            self.assertTrue(4, len(csv_list))
            self.assertTrue(str(self.stone3.internal_id), csv_list[0]['internal_id'])
            self.assertTrue(str(self.stone1.internal_id), csv_list[2]['internal_id'])
            self.assertIn("internal_id", reader.fieldnames)

    def test_master_download(self):

        queryset = Stone.objects.all()
        file_path = Stone.objects.download_master_reports(queryset=queryset)

        file = open(file_path)
        model_fields = get_model_fields(Stone)
        field_names = get_field_names(model_fields)
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            csv_list = list(reader)
            self.assertTrue(4, len(csv_list))
            self.assertTrue(str(self.stone3.data_entry_user), csv_list[0]['data_entry_user'])
            self.assertTrue(str(self.stone1.date_created), csv_list[2]['date_created'])
            for field in field_names:
                self.assertIn(field, reader.fieldnames)

    def test_download_to_goldway_csv(self):

        queryset = Stone.objects.all()
        file_path = Stone.objects.download_to_goldway_csv(queryset=queryset)
        field_names = ["date_to_GW", "internal_id", "basic_carat"]
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            csv_list = list(reader)
            self.assertTrue(4, len(csv_list))
            self.assertTrue(str(self.stone3.basic_carat), csv_list[0]['basic_carat'])
            self.assertTrue(str(self.stone1.internal_id), csv_list[2]['internal_id'])
            for field in field_names:
                self.assertIn(field, reader.fieldnames)

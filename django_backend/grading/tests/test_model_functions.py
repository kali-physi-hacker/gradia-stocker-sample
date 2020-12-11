import os
import csv
from django.test import TestCase
from grading.models import Stone
from grading.helpers import get_stone_fields


class TestCSVGeneration(TestCase):
    fixtures = ("data_migration/test_data.json",)

    def setUp(self):
        self.stone1 = Stone.objects.get(internal_id=1)
        self.stone3 = Stone.objects.get(internal_id=3)

    def test_generated_id_csv(self):
        """
        Send File and 200 response status if report id (gradia_ID)
        is valid and exists
        Returns:
        """
        queryset = Stone.objects.all()
        file_path = Stone.objects.generate_id_csv(queryset=queryset)
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            csv_list = list(reader)
            self.assertTrue(len(csv_list) == 3)
            self.assertTrue(str(self.stone3.internal_id), csv_list[0]["internal_id"])
            self.assertTrue(str(self.stone1.internal_id), csv_list[2]["internal_id"])
            self.assertIn("internal_id", reader.fieldnames)

    def test_generated_master_report_csv(self):

        queryset = Stone.objects.all()
        file_path = Stone.objects.generate_master_report_csv(queryset=queryset)

        file = open(file_path)
        field_names = get_stone_fields(Stone)
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            csv_list = list(reader)
            self.assertTrue(len(csv_list) == 3)
            self.assertTrue(
                str(self.stone3.data_entry_user), csv_list[0]["data_entry_user"]
            )
            self.assertTrue(str(self.stone1.date_created), csv_list[2]["date_created"])
            for field in field_names:
                self.assertIn(field, reader.fieldnames)

    def test_generated_to_goldway_csv(self):

        queryset = Stone.objects.all()
        file_path = Stone.objects.generate_to_goldway_csv(queryset=queryset)
        field_names = ["date_to_GW", "internal_id", "basic_carat"]
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            csv_list = list(reader)
            self.assertTrue(len(csv_list) == 3)
            self.assertTrue(str(self.stone3.basic_carat), csv_list[0]["basic_carat"])
            self.assertTrue(str(self.stone1.internal_id), csv_list[2]["internal_id"])
            for field in field_names:
                self.assertIn(field, reader.fieldnames)

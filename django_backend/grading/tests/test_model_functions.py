import os
import csv
from django.test import TestCase
from grading.models import Stone
from grading.helpers import get_stone_fields


class TestCSVGeneration(TestCase):
    fixtures = ("data_migration/test_data.json",)

    def setUp(self):
        self.stone1 = Stone.objects.get(internal_id=1)
        self.stone2 = Stone.objects.get(internal_id=2)
        self.stone3 = Stone.objects.get(internal_id=3)

        self.stone1.external_id = "G00000001"
        self.stone1.carat_weight = "0.090"
        self.stone1.color = "F"
        self.stone1.save()

        self.stone2.external_id = "G00000002"
        self.stone2.carat_weight = "0.100"
        self.stone2.color = "E"
        self.stone2.save()

        self.stone3.external_id = "G00000003"
        self.stone3.carat_weight = "0.150"
        self.stone3.color = "G"
        self.stone3.save()

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
            self.assertIn("internal_id", reader.fieldnames)
            csv_list = list(reader)
        self.assertEqual(3, len(csv_list))
        self.assertEqual(str(self.stone3.internal_id), csv_list[0]["internal_id"])
        self.assertEqual(str(self.stone1.internal_id), csv_list[2]["internal_id"])

    def test_generated_master_report_csv(self):

        queryset = Stone.objects.all()
        file_path = Stone.objects.generate_master_report_csv(queryset=queryset)

        file = open(file_path)
        field_names = get_stone_fields(Stone)
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for field in field_names:
                self.assertIn(field, reader.fieldnames)
            csv_list = list(reader)
        self.assertEqual(3, len(csv_list))
        self.assertEqual(str(self.stone3.data_entry_user), csv_list[0]["data_entry_user"])
        self.assertEqual(str(self.stone1.date_created), csv_list[2]["date_created"])

    def test_generated_to_goldway_csv(self):

        queryset = Stone.objects.all()
        file_path = Stone.objects.generate_to_goldway_csv(queryset=queryset)
        field_names = ["date_to_GW", "internal_id", "basic_carat"]
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for field in field_names:
                self.assertIn(field, reader.fieldnames)

    def test_generated_to_GIA_csv(self):
        queryset = Stone.objects.all()
        file_path = Stone.objects.generate_to_GIA_csv(queryset=queryset)
        field_names = ["date_to_GIA", "external_id", "carat_weight", "color"]
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for field in field_names:
                self.assertIn(field, reader.fieldnames)
            csv_list = list(reader)
        self.assertTrue(len(csv_list) == 3)
        self.assertEqual(str(self.stone3.external_id), csv_list[0]["external_id"])
        self.assertEqual(str(self.stone1.carat_weight), csv_list[2]["carat_weight"])

    def test_generated_basic_report_csv(self):
        queryset = Stone.objects.all()
        file_path = Stone.objects.generate_basic_report_csv(queryset=queryset)
        field_names = [
            "date_to_GIA",
            "external_id",
            "carat_weight",
            "color",
            "fluoresence",
            "culet",
            "inclusions",
            "cut_grade",
            "basic_final_polish",
            "symmetry_grade",
            "table_size",
            "crown_angle",
            "pavilion_angle",
            "star_length",
            "lower_half",
            "girdle_thick",
            "girdle_min",
            "girdle_max",
            "crown_height",
            "pavilion_depth",
            "total_depth",
        ]
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for field in field_names:
                self.assertIn(field, reader.fieldnames)
            csv_list = list(reader)
        self.assertTrue(len(csv_list) == 3)
        self.assertEqual(str(self.stone3.total_depth), csv_list[0]["total_depth"])
        self.assertEqual(str(self.stone1.inclusions), csv_list[2]["inclusions"])

    def test_generated_triple_report_csv(self):
        queryset = Stone.objects.all()
        file_path = Stone.objects.generate_triple_report_csv(queryset=queryset)
        field_names = ["internal_id", "external_id", "carat_weight", "color", "clarity"]
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for field in field_names:
                self.assertIn(field, reader.fieldnames)
            csv_list = list(reader)
        self.assertTrue(len(csv_list) == 3)
        self.assertEqual(str(self.stone3.carat_weight), csv_list[0]["carat_weight"])
        self.assertEqual(str(self.stone1.color), csv_list[2]["color"])

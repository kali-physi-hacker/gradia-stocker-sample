from decimal import Decimal

from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
import pandas as pd

from grading.admin import StoneAdmin
from grading.models import Stone
from grading.forms import (
    SarineUploadForm,
    BasicUploadForm,
    GWGradingUploadForm,
    GWAdjustingUploadForm,
    GIAUploadForm,
    GIAAdjustingUploadForm,
)

from ownerships.models import StoneTransfer

from stonegrading.mixins import GWGradingAdjustMixin, GIAGradingAdjustMixin, BasicGradingMixin
from stonegrading.grades import CuletCharacteristics


User = get_user_model()

"""
What did you implement? / What implementations do you need tests for?
- download basic grading template 
- download_basic_grading_template
- download_to_goldway_csv
- download_adjust_goldway_csv
- download_to_GIA_csv
- download_adjust_GIA_csv
- download_to_basic_report_csv (unsure about if I have the correct fields for this)
- download_to_triple_report_csv (unsure about if I have the correct fields for this)
-
"""

"""
We have methods we can go about the testing
- We can implement them as view tests, where we make a request to a url submitting the data
- We can implement them as method specific test, mocking some components -> StoneAdmin.download_basic_grading_template(request, queryset)
"""


class DownloadCSVAdminTest(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.queryset = Stone.objects.all()
        admin_site = AdminSite()
        self.admin = StoneAdmin(model=Stone, admin_site=admin_site)

        self.request = RequestFactory()

    def upload_initial_grading_results(self):
        """
        Upload both basic and sarine
        :return:
        """
        grading_form = (SarineUploadForm, BasicUploadForm)
        csv_upload_files = ("sarine-01.csv", "basic-01.csv")

        for form_class, csv_filename in zip(grading_form, csv_upload_files):
            file = open(f"grading/tests/fixtures/{csv_filename}", "rb")
            kwargs = {
                "data": {},
                "files": {"file": SimpleUploadedFile(file.name, file.read())},
                "user": User.objects.get(username="gary"),
            }
            form = form_class(**kwargs)
            self.assertTrue(form.is_valid())
            form.save()

    def upload_adjusting_results(self):
        """
        Upload both GWAdjusting and GIAAdjusting results
        :return:
        """
        grading_form = (GWAdjustingUploadForm, GIAAdjustingUploadForm)
        csv_upload_files = ("gw_adjust.csv", "gia_adjusting.csv")

        for form_class, csv_filename in zip(grading_form, csv_upload_files):
            file = open(f"grading/tests/fixtures/{csv_filename}", "rb")
            kwargs = {"data": {}, "files": {"file": SimpleUploadedFile(file.name, file.read())}}
            form = form_class(**kwargs)
            self.assertTrue(form.is_valid())
            form.save()

    def upload_third_party_grading_results(self):
        """
        Upload both gia and gw grading results
        :return:
        """
        grading_form = (GWGradingUploadForm, GIAUploadForm)
        csv_upload_files = ("gold_way-01.csv", "gia.csv")

        split = User.objects.get(username="split")
        vault = User.objects.get(username="vault")
        goldway = User.objects.get(username="goldway")
        gia = User.objects.get(username="gia")
        grader = User.objects.get(username="tanly")

        for index, (form_class, csv_filename) in enumerate(zip(grading_form, csv_upload_files)):
            file = open(f"grading/tests/fixtures/{csv_filename}", "rb")
            kwargs = {
                "data": {},
                "files": {"file": SimpleUploadedFile(file.name, file.read())},
                "user": User.objects.get(username="gary"),
            }
            form = form_class(**kwargs)
            self.assertTrue(form.is_valid())

            # Do stone transfer here index == 0 == GW results, index == 1 == GIA results
            for stone_id in (1, 5, 6):
                stone = Stone.objects.get(internal_id=stone_id)
                if index == 0:
                    from_user = split
                    to_user = goldway
                else:
                    from_user = vault
                    to_user = gia

                StoneTransfer.initiate_transfer(item=stone, from_user=from_user, to_user=to_user, created_by=grader)
                StoneTransfer.confirm_received(item=stone)

            form.save()

    def upload_all_grading_results(self):
        """
        Upload all grading results fixture
        :return:
        """
        self.upload_initial_grading_results()
        self.upload_third_party_grading_results()
        self.upload_adjusting_results()

    def test_download_basic_grading_template_success(self):
        response = self.admin.download_basic_grading_template(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Basic_Grading_Template_"))

        # Test content of csv file
        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")

        self.assertEqual(len(headers), 41)
        for field in [field.name for field in BasicGradingMixin._meta.get_fields()]:
            self.assertIn(field, headers)

        self.assertIn("internal_id", headers)
        self.assertIn("girdle_min_grade", headers)

    def test_download_adjust_goldway_csv_success(self):
        response = self.admin.download_adjust_goldway_csv(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Adjust_Goldway"))

        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")
        self.assertEqual(len(headers), 24)

        for field in [field.name for field in GWGradingAdjustMixin._meta.get_fields()]:
            self.assertIn(field, headers)

        self.assertIn("internal_id", headers)
        self.assertIn("nano_etch_inscription", headers)

    def test_download_to_gia_csv_success(self):
        # give the stones a nanoetch ...
        for stone in Stone.objects.all():
            stone.external_id = f"inscription-{stone.pk}"
            stone.save()

        response = self.admin.download_to_GIA_csv(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("To_GIA"))

        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")

        self.assertEqual(len(headers), 5)
        field_names = (
            "internal_id",
            "date_to_gia",
            "nano_etch_inscription",
            "gw_return_reweight",
            "gw_color_adjusted_final",
        )
        for field in headers:
            self.assertIn(field, field_names)

    @patch("django.contrib.messages.warning")
    def test_download_to_gia_csv_failure(self, mocked_messages):
        self.request.path = "grading:errors_page"  # just for testing --> like mocking
        response = self.admin.download_to_GIA_csv(request=self.request, queryset=self.queryset)

        self.assertTrue(mocked_messages.called)
        message = mocked_messages.call_args_list[0].args[1]
        self.assertEqual(message, "There is not enough data to download")

    def test_download_adjust_gia_csv_success(self):
        response = self.admin.download_adjust_GIA_csv(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Adjust_GIA"))

        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")
        self.assertEqual(len(headers), 23)

        fields = [field.name for field in GIAGradingAdjustMixin._meta.get_fields() if "polish" not in field.name] + [
            "internal_id",
            "gia_code",
            "nano_etch_inscription",
            "gia_color",
            "gw_color_adjusted_final",
            "basic_culet_final",
            "basic_culet_characteristic_final",
        ]
        self.assertEqual(len(fields), len(headers))

        for field in headers:
            self.assertIn(field, fields)
        self.assertIn("gia_code", headers)
        self.assertIn("nano_etch_inscription", headers)

    def test_download_to_basic_report_csv_success(self):
        response = self.admin.download_to_basic_report_csv(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Basic_Report"))

        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")
        self.assertEqual(len(headers), 64)

        field_names = (
            "internal_id",
            "diameter_min",
            "diameter_max",
            "height",
            "table_size",
            "crown_angle",
            "pavilion_angle",
            "star_length",
            "lower_half",
            "girdle_thickness_number",
            "girdle_min_number",
            "girdle_max_number",
            "culet_size",
            "crown_height",
            "pavilion_depth",
            "total_depth",
            "table_size_rounded",
            "crown_angle_rounded",
            "pavilion_angle_rounded",
            "star_length_rounded",
            "lower_half_rounded",
            "girdle_thickness_rounded",
            "girdle_min_grade",
            "girdle_max_grade",
            "culet_size_description",
            "crown_height_rounded",
            "pavilion_depth_rounded",
            "total_depth_rounded",
            "sarine_cut_pre_polish_symmetry",
            "sarine_symmetry",
            "roundness",
            "roundness_grade",
            "table_size_dev",
            "table_size_dev_grade",
            "crown_angle_dev",
            "crown_angle_dev_grade",
            "pavilion_angle_dev",
            "pavilion_angle_dev_grade",
            "star_length_dev",
            "star_length_dev_grade",
            "lower_half_dev",
            "lower_half_dev_grade",
            "girdle_thick_dev",
            "girdle_thick_dev_grade",
            "crown_height_dev",
            "crown_height_dev_grade",
            "pavilion_depth_dev",
            "pavilion_depth_dev_grade",
            "misalignment",
            "misalignment_grade",
            "table_edge_var",
            "table_edge_var_grade",
            "table_off_center",
            "table_off_center_grade",
            "culet_off_center",
            "culet_off_center_grade",
            "table_off_culet",
            "table_off_culet_grade",
            "star_angle",
            "star_angle_grade",
            "upper_half_angle",
            "upper_half_angle_grade",
            "lower_half_angle",
            "lower_half_angle_grade",
        )
        for field in headers:
            self.assertIn(field, field_names)

    def test_download_export_triple_report_to_lab_success(self):
        """
        Tests export to triple graded stone report to lab
        :return:
        """
        self.upload_all_grading_results()
        queryset = self.queryset.filter(internal_id__in=(1, 5, 6))
        response = self.admin.download_export_triple_report_to_lab(request=self.request, queryset=queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Triple_Report_Lab_Export"))

        content = [row for row in response.content.decode().split("\n") if row != ""]
        content, headers = content[1:], content[0]
        headers = headers.split(",")
        self.assertEqual(len(headers), 29)

        field_names = (
            "date",
            "gradia_ID",
            "carat",
            "color",
            "clarity",
            "fluorescence",
            "culet",
            "culet_description",
            "cut",
            "polish",
            "symmetry",
            "table_size",
            "crown_angle",
            "pavilion_angle",
            "star_length",
            "lower_half",
            "girdle_thickness",
            "girdle_maximum",
            "girdle_minimum",
            "crown_height",
            "pavilion_depth",
            "total_depth",
            "comments",
            "diameter_min",
            "diameter_max",
            "height",
            "goldway_AI_code",
            "GIA_batch_code",
            "inclusion",
        )

        for field_name in headers:
            self.assertIn(field_name, field_names)

        db_fields = (
            "external_id",
            "basic_carat",
            "gia_color_adjusted_final",
            "gw_clarity_adjusted_final",
            "gw_fluorescence_adjusted_final",
            "gia_culet_adjusted_final",
            "gia_culet_characteristic_final",
            "auto_final_gradia_cut_grade",
            "basic_polish_final",
            "sarine_symmetry",
            "table_size_rounded",
            "crown_angle_rounded",
            "pavilion_angle_rounded",
            "star_length_rounded",
            "lower_half_rounded",
            "girdle_thickness_rounded",
            "girdle_max_grade",
            "basic_girdle_min_grade_final",
            "crown_height_rounded",
            "pavilion_depth_rounded",
            "total_depth_rounded",
            "comments",
            "diameter_min",
            "diameter_max",
            "height",
            "goldway_AI_code",
            "GIA_batch_code",
            "basic_inclusions_final",
        )
        special_fields = ("comments", "goldway_AI_code", "GIA_batch_code", "basic_inclusions_final")
        omit_plus_or_minus_fields = (
            "gia_color_adjusted_final",
            "gw_clarity_adjusted_final",
            "gw_fluorescence_adjusted_final",
            "basic_polish_final",
        )

        for index, row in enumerate(content):
            data = row.split(",")[1:]  # Leave out date field

            if data[-1][-1] == '"':
                # Fix inclusion split problem
                inclusions = ", ".join([inclusion.strip('" ') for inclusion in data[-2:]])
                data.pop()
                data.pop()
                data.append(inclusions)

            stone = queryset.get(external_id=data[0])
            expected_data = [getattr(stone, field) if field not in special_fields else field for field in db_fields]

            special_fields_map = {
                "goldway_AI_code": stone.gw_verification.code,
                "GIA_batch_code": stone.gia_verification.code,
            }
            for _, (actual_value, expected_value) in enumerate(zip(data, expected_data)):
                if db_fields[_] in omit_plus_or_minus_fields:
                    expected_value = getattr(stone, db_fields[_]).strip("-").strip("+")
                    self.assertEqual(actual_value, expected_value)
                    continue

                if db_fields[_] == "gia_culet_characteristic_final":
                    expected_value = CuletCharacteristics.LAB_EXPORT_MAP[stone.gia_culet_characteristic_final]
                    self.assertEqual(actual_value, expected_value)
                    continue

                if db_fields[_] == "height":
                    expected_value = "%.2f" % round(stone.height, 2)
                    self.assertEqual(actual_value, expected_value)
                    continue

                if expected_value not in special_fields:
                    if expected_value is None:
                        self.assertEqual(actual_value, "")
                    else:
                        self.assertEqual(actual_value, str(expected_value))
                else:
                    field = db_fields[_]
                    if field == "basic_inclusions_final":
                        inclusions = ", ".join(
                            [inclusion.inclusion for inclusion in stone.basic_inclusions_final.all()]
                        )
                        self.assertEqual(actual_value, inclusions)
                        continue
                    if field != "comments":
                        self.assertEqual(actual_value, special_fields_map[db_fields[_]])

    def test_download_goldway_grading_template_success(self):
        response = self.admin.download_goldway_grading_template(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Goldway_Grading_Template_"))

        # Test content of csv file
        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")

        self.assertEqual(len(headers), 9)
        field_names = (
            "date_from_gw",
            "internal_id",
            "goldway_code",
            "nano_etch_inscription",
            "gw_return_reweight",
            "gw_color",
            "gw_clarity",
            "gw_fluorescence",
            "gw_remarks",
        )
        for field in headers:
            self.assertIn(field, field_names)

    def test_download_gia_grading_template_success(self):
        response = self.admin.download_gia_grading_template(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("GIA_Grading_Template_"))

        # Test content of csv file
        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")

        self.assertEqual(len(headers), 7)
        field_names = (
            "internal_id",
            "date_from_gia",
            "nano_etch_inscription",
            "gia_code",
            "gia_diamond_description",
            "gia_color",
            "gia_remarks",
        )
        for field in headers:
            self.assertIn(field, field_names)

    def test_download_external_ids_csv_success(self):
        response = self.admin.download_external_ids(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")

        disposition_type, file_name = response["Content-Disposition"].split("=")
        disposition_type = disposition_type.split(";")[0]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Gradia_ids_"))

        headers, content = [row for row in response.content.decode().split('\n"')]
        header = headers.split(",")
        self.assertEqual(len(header), 1)
        self.assertEqual(headers, "external_id")

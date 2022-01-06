import pandas as pd

from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.contrib.admin.sites import AdminSite
from django.http import HttpRequest, response

from grading.admin import StoneAdmin
from grading.models import Stone

from stonegrading.mixins import BasicGradingMixin, GWGradingAdjustMixin, GIAGradingAdjustMixin, BasicGradingMixin

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

    def test_download_basic_grading_template_success(self):
        response = self.admin.download_basic_grading_template(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
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
        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
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
        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("To_GIA"))

        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")

        self.assertTrue(len(headers), 4)
        field_names = (
            "date_from_gia",
            "nano_etch_inscription",
            "basic_carat",
            "basic_color_final",
        )
        for field in field_names:
            self.assertIn(field, headers)

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
        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Adjust_GIA"))

        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")
        self.assertEqual(len(headers), 22)

        for field in [
            field.name for field in GIAGradingAdjustMixin._meta.get_fields() if "polish" not in field.name
        ]:
            self.assertIn(field, headers)
        self.assertIn("gia_code", headers)
        self.assertIn("nano_etch_inscription", headers)

    def test_download_to_basic_report_csv_success(self):
        response = self.admin.download_to_basic_report_csv(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
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
        for field in field_names:
            self.assertIn(field, headers)

    def test_download_to_triple_report_csv_success(self):
        response = self.admin.download_to_triple_report_csv(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Triple_Report"))

        headers, content = [row for row in response.content.decode().split("\n") if row != ""]
        headers = headers.split(",")
        self.assertEqual(len(headers), 34)

        field_names = (
            "internal_id",
            "goldway_code",
            "gia_code",
            "basic_carat_final",
            "gw_color_adjusted_final",
            "gw_clarity_adjusted_final",
            "gw_fluorescence_adjusted_final",
            "gia_culet_characteristic_final",
            "gia_culet_adjusted_final",
            "basic_inclusions_final",
            "basic_inclusions_final",
            "gia_polish_adjusted_final",
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
            "crown_height",
            "pavilion_depth",
            "total_depth",
            "sarine_cut_pre_polish_symmetry",
            "sarine_symmetry",
            "blockchain_address",
            "basic_remarks",
            "gw_remarks",
            "gw_adjust_remarks",
            "gia_remarks",
            "post_gia_remarks",
        )

        for field in field_names:
            self.assertIn(field, headers)

    def test_download_goldway_grading_template_success(self):
        response = self.admin.download_goldway_grading_template(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
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
        for field in field_names:
            self.assertIn(field, headers)

    def test_download_gia_grading_template_success(self):
        response = self.admin.download_gia_grading_template(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")
        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
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
        for field in field_names:
            self.assertIn(field, headers)

    def test_download_external_ids_csv_success(self):
        response = self.admin.download_external_ids(request=self.request, queryset=self.queryset)
        self.assertEqual(response["Content-Type"], "text/csv")

        disposition_type, file_name = response["Content-Disposition"].split(";")
        file_name = file_name.split("/")[-1]
        self.assertEqual(disposition_type, "attachment")
        self.assertTrue(file_name.startswith("Gradia_id_"))

        headers, content = [row for row in response.content.decode().split('\n"')]
        header = headers.split(',')
        self.assertEqual(len(header), 1)
        self.assertEqual(headers, 'external_id')        
        
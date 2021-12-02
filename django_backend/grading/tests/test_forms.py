from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.datetime_safe import datetime
from django.utils.timezone import utc
from grading.forms import (
    UploadFormMetaClass,
    BaseUploadForm,
    SarineUploadForm,
    BasicUploadForm,
    GWGradingUploadForm,
    GIAUploadForm,
    GWAdjustingUploadForm,
    GIAAdjustingUploadForm,
)
from grading.models import Stone, GiaVerification
from stonegrading.mixins import SarineGradingMixin
from ownerships.models import StoneTransfer

User = get_user_model()

expected_stones = [
    {
        "internal_id": 1,
        "diameter_min": 2.9,
        "diameter_max": 2.92,
        "height": 1.77,
        "table_size": 58.4,
        "crown_angle": 33.59,
        "pavilion_angle": 40.93,
        "star_length": 44.6,
        "lower_half": 79.8,
        "girdle_thickness_number": 3.98,
        "girdle_min_number": 1.85,
        "girdle_max_number": 2.78,
        "culet_size": 0.52,
        "crown_height": 13.84,
        "pavilion_depth": 43.1,
        "total_depth": 60.92,
        "table_size_rounded": 58,
        "crown_angle_rounded": 33.5,
        "pavilion_angle_rounded": 41.0,
        "star_length_rounded": 45,
        "lower_half_rounded": 80,
        "girdle_thickness_rounded": 4,
        "girdle_min_grade": "MED",
        "girdle_max_grade": "STK",
        "culet_size_description": "N/VS",
        "crown_height_rounded": 14,
        "pavilion_depth_rounded": 43,
        "total_depth_rounded": 60.9,
        "sarine_cut_pre_polish_symmetry": "EX",
        "sarine_symmetry": "VG",
        "roundness": 0.9,
        "roundness_grade": "EX",
        "table_size_dev": 0.6,
        "table_size_dev_grade": "EX",
        "crown_angle_dev": 1,
        "crown_angle_dev_grade": "EX",
        "pavilion_angle_dev": 0.9,
        "pavilion_angle_dev_grade": "EX",
        "star_length_dev": 3.9,
        "star_length_dev_grade": "EX",
        "lower_half_dev": 3.2,
        "lower_half_dev_grade": "EX",
        "girdle_thick_dev": 0.5,
        "girdle_thick_dev_grade": "EX",
        "crown_height_dev": 0.7,
        "crown_height_dev_grade": "EX",
        "pavilion_depth_dev": 0.7,
        "pavilion_depth_dev_grade": "EX",
        "misalignment": 1.9,
        "misalignment_grade": "VG",
        "table_edge_var": 3.6,
        "table_edge_var_grade": "VG",
        "table_off_center": 0.3,
        "table_off_center_grade": "EX",
        "culet_off_center": 0.5,
        "culet_off_center_grade": "EX",
        "table_off_culet": 0.5,
        "table_off_culet_grade": "EX",
        "star_angle": 2.5,
        "star_angle_grade": "EX",
        "upper_half_angle": 1.2,
        "upper_half_angle_grade": "EX",
        "lower_half_angle": 0.8,
        "lower_half_angle_grade": "EX",
    },
    {
        "internal_id": 5,
        "diameter_min": 2.92,
        "diameter_max": 2.97,
        "height": 1.75,
        "table_size": 61.6,
        "crown_angle": 34.48,
        "pavilion_angle": 40.31,
        "star_length": 46.3,
        "lower_half": 79.5,
        "girdle_thickness_number": 4.11,
        "girdle_min_number": 1.8,
        "girdle_max_number": 3.74,
        "culet_size": 0.85,
        "crown_height": 13.21,
        "pavilion_depth": 42.15,
        "total_depth": 59.58,
        "table_size_rounded": 62,
        "crown_angle_rounded": 34.5,
        "pavilion_angle_rounded": 40.4,
        "star_length_rounded": 45,
        "lower_half_rounded": 80,
        "girdle_thickness_rounded": 4,
        "girdle_min_grade": "MED",
        "girdle_max_grade": "THK",
        "culet_size_description": "N/VS",
        "crown_height_rounded": 13,
        "pavilion_depth_rounded": 42,
        "total_depth_rounded": 59.6,
        "sarine_cut_pre_polish_symmetry": "GD",
        "sarine_symmetry": "GD",
        "roundness": 1.6,
        "roundness_grade": "VG",
        "table_size_dev": 1.5,
        "table_size_dev_grade": "VG",
        "crown_angle_dev": 1.3,
        "crown_angle_dev_grade": "VG",
        "pavilion_angle_dev": 1.1,
        "pavilion_angle_dev_grade": "VG",
        "star_length_dev": 4.7,
        "star_length_dev_grade": "EX",
        "lower_half_dev": 5.5,
        "lower_half_dev_grade": "EX",
        "girdle_thick_dev": 0.7,
        "girdle_thick_dev_grade": "EX",
        "crown_height_dev": 1.4,
        "crown_height_dev_grade": "VG",
        "pavilion_depth_dev": 1.4,
        "pavilion_depth_dev_grade": "VG",
        "misalignment": 4,
        "misalignment_grade": "GD",
        "table_edge_var": 2.9,
        "table_edge_var_grade": "VG",
        "table_off_center": 0.6,
        "table_off_center_grade": "EX",
        "culet_off_center": 1.2,
        "culet_off_center_grade": "VG",
        "table_off_culet": 1.7,
        "table_off_culet_grade": "VG",
        "star_angle": 5.8,
        "star_angle_grade": "VG",
        "upper_half_angle": 4.9,
        "upper_half_angle_grade": "EX",
        "lower_half_angle": 1.2,
        "lower_half_angle_grade": "EX",
    },
    {
        "internal_id": 6,
        "diameter_min": 2.86,
        "diameter_max": 2.9,
        "height": 1.77,
        "table_size": 60.2,
        "crown_angle": 34.75,
        "pavilion_angle": 41.89,
        "star_length": 51,
        "lower_half": 74.3,
        "girdle_thickness_number": 3.09,
        "girdle_min_number": 0.69,
        "girdle_max_number": 2.08,
        "culet_size": 0.59,
        "crown_height": 13.85,
        "pavilion_depth": 44.53,
        "total_depth": 61.51,
        "table_size_rounded": 60,
        "crown_angle_rounded": 35,
        "pavilion_angle_rounded": 41.8,
        "star_length_rounded": 50,
        "lower_half_rounded": 75,
        "girdle_thickness_rounded": 3,
        "girdle_min_grade": "ETN TO VTN",
        "girdle_max_grade": "STK",
        "culet_size_description": "N/VS",
        "crown_height_rounded": 14,
        "pavilion_depth_rounded": 44.5,
        "total_depth_rounded": 61.5,
        "sarine_cut_pre_polish_symmetry": "VG",
        "sarine_symmetry": "VG",
        "roundness": 1.3,
        "roundness_grade": "VG",
        "table_size_dev": 1,
        "table_size_dev_grade": "EX",
        "crown_angle_dev": 0.6,
        "crown_angle_dev_grade": "EX",
        "pavilion_angle_dev": 1,
        "pavilion_angle_dev_grade": "VG",
        "star_length_dev": 6.3,
        "star_length_dev_grade": "EX",
        "lower_half_dev": 3.2,
        "lower_half_dev_grade": "EX",
        "girdle_thick_dev": 1.4,
        "girdle_thick_dev_grade": "VG",
        "crown_height_dev": 1,
        "crown_height_dev_grade": "EX",
        "pavilion_depth_dev": 1.4,
        "pavilion_depth_dev_grade": "VG",
        "misalignment": 1.8,
        "misalignment_grade": "VG",
        "table_edge_var": 1.8,
        "table_edge_var_grade": "EX",
        "table_off_center": 0.5,
        "table_off_center_grade": "EX",
        "culet_off_center": 1.2,
        "culet_off_center_grade": "VG",
        "table_off_culet": 1.7,
        "table_off_culet_grade": "VG",
        "star_angle": 2.6,
        "star_angle_grade": "EX",
        "upper_half_angle": 2.9,
        "upper_half_angle_grade": "EX",
        "lower_half_angle": 1.3,
        "lower_half_angle_grade": "EX",
    },
]


class MetaClassTest(TestCase):
    def setUp(self):
        class BaseSample(metaclass=UploadFormMetaClass):
            pass

        class ChildSample(BaseSample):
            def __process_method_1(self):
                pass

            def __process_method_2(self):
                pass

        self.child = ChildSample()

    def test_process_methods(self):
        """
        Tests that the MetaClass provides the processing_methods attribute
        """
        self.assertTrue(hasattr(self.child, "processing_methods"))
        processing_methods = [method.__name__ for method in self.child.processing_methods]
        self.assertEqual(len(processing_methods), 2)
        self.assertEqual(type(processing_methods), list)
        for method in ("__process_method_1", "__process_method_2"):
            self.assertIn(method, processing_methods)


class BaseUploadFormClassTest(TestCase):
    """"""

    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        class SampleUploadClass(BaseUploadForm):
            class Meta:
                mixin = SarineGradingMixin
                new = True

            def __init__(self, user, *args, **kwargs):
                self.user = user
                super().__init__(*args, **kwargs)

        self.UploadClass = SampleUploadClass
        self.csv_file_invalid_types = open("grading/tests/fixtures/sarine-01-type.csv", "rb")
        self.gary_user = User.objects.get(username="gary")
        self.csv_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        self.csv_file_spaces = open("grading/tests/fixtures/sarine-01-spaces.csv", "rb")
        self.csv_file_no_parcel = open("grading/tests/fixtures/no-parcel.csv", "rb")
        self.csv_file_missing_header = open("grading/tests/fixtures/sarine-01-h.csv", "rb")
        self.csv_file_invalid_types = open("grading/tests/fixtures/sarine-01-type.csv", "rb")

        self.expected_stones = expected_stones

    def test_class_definition_format(self):
        """
        Tests that form class (sub classes) are defined with a class Meta
        returns:
        """

        # No Meta class
        class Sample(BaseUploadForm):
            pass

        with self.assertRaises(ValueError):
            form = Sample()

        with self.assertRaises(ValueError):
            form = Sample()

        # No mixin in Meta class
        class Sample(BaseUploadForm):
            class Meta:
                fields = "_all_"

        with self.assertRaises(ValueError):
            form = Sample()

    def test_class_attributes(self):
        """
        Tests that csv_content does universal (shared) csv content processing, calls other
        processing methods and returns a list of stone data (dicts)
        :return:
        """
        csv_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        form = self.UploadClass(
            data={}, user=None, files={"file": SimpleUploadedFile(csv_file.name, csv_file.read())}
        )

        self.assertTrue(hasattr(form, "is_valid"))
        self.assertTrue(hasattr(form, "cleaned_stone_data"))
        self.assertTrue(hasattr(form, "stone_data"))

        self.assertTrue(hasattr(form, "mixin_fields"))
        self.assertTrue(hasattr(form, "mixin"))

        # Test that csv_errors cannot be accessed until is_valid is called
        with self.assertRaises(ValueError):
            form.csv_errors

        self.assertTrue(form.is_valid())
        errors = form.csv_errors
        self.assertEqual(type(errors), dict)
        self.assertEqual(len(errors), 0)

    def test_form_invalid_type(self):
        """
        Tests that csv file content (value) has mismatch type with the expected type
        :return:
        """
        form = self.UploadClass(
            data={},
            user=self.gary_user,
            files={"file": SimpleUploadedFile(self.csv_file_invalid_types.name, self.csv_file_invalid_types.read())},
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["file"][0], "CSV File Validation Error")

        # For this type of error we're expecting a dictionary of the columns being keys and the rows with the errors being the value
        self.assertEqual(form.csv_errors[0]["pavilion_angle"][0], "Enter a number.")
        self.assertEqual(form.csv_errors[1]["girdle_max_number"][0], "Enter a number.")
        self.assertEqual(form.csv_errors[2]["height"][0], "Enter a number.")

    def test_form_invalid_for_missing_column_name(self):
        """
        Tests that form errors if required column names are missing
        :return:
        """
        form = self.UploadClass(
            data={},
            files={
                "file": SimpleUploadedFile(self.csv_file_missing_header.name, self.csv_file_missing_header.read())
            },
            user=self.gary_user,
        )

        self.assertFalse(form.is_valid())
        for error_key in form.csv_errors:
            self.assertEqual(form.csv_errors[error_key].get("diameter_min")[0], "This field is required.")
            self.assertEqual(form.csv_errors[error_key].get("lower_half_angle_grade")[0], "This field is required.")

    def test_form_validated_return_data(self):
        """
        Tests that form.cleaned_data returns a list of dictionaries of stone data
        returns:
        """
        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())},
            user=self.gary_user,
        )
        self.assertTrue(form.is_valid())
        data = form.cleaned_data
        self.assertEqual(type(data), list)
        self.assertEqual(len(data), 3)

        for actual_stone, expected_stone in zip(form.cleaned_data, self.expected_stones):
            self.assertEqual(actual_stone, expected_stone)

    def test_is_new_attr_true(self):
        """
        Tests that if is_new is True validation is applied
        :return:
        """

        class SampleUploadForm(BaseUploadForm):
            class Meta:
                mixin = SarineGradingMixin
                new = True

        form = SampleUploadForm(
            data={}, files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())}
        )
        self.assertTrue(form.is_valid())

    def test_is_new_attr_false(self):
        """
        Tests that if is_new is False validation is applied
        :return:
        """

        class AnotherUploadForm(BaseUploadForm):
            class Meta:
                mixin = SarineGradingMixin

        form = AnotherUploadForm(
            data={}, files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())}
        )

        self.assertFalse(form.is_valid())
        for row, internal_id in enumerate((1, 5, 6)):
            error = form.csv_errors[row]["internal_id"][0]
            self.assertEqual(error, f"Stone with internal id: {internal_id} does not exist")


class SarineUploadFormTest(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.csv_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        self.csv_file_spaces = open("grading/tests/fixtures/sarine-01-spaces.csv", "rb")
        self.csv_file_no_parcel = open("grading/tests/fixtures/no-parcel.csv", "rb")

        self.gary_user = User.objects.get(username="gary")

        self.expected_stones = expected_stones

    def test_csv_file_is_valid(self):
        """
        Test for validation True of csv file
        """
        # No column spaces
        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())},
            user=self.gary_user,
        )
        self.assertTrue(form.is_valid())

    def test_csv_invalid_if_wrong_parcel_code(self):
        """
        Tests that form errors
        :return:
        """
        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.csv_file_no_parcel.name, self.csv_file_no_parcel.read())},
            user=self.gary_user,
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["file"][0],
            "No parcel with such a parcel code. Please be sure the csv file name matches the parcel code",
        )

    def test_form_save_creates_stones(self):
        """
        Tests that form.save() creates stone instances in the db
        :return:
        """
        Stone.objects.all().delete()

        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())},
            user=self.gary_user,
        )
        self.assertTrue(form.is_valid())
        form.save()

        stones = Stone.objects.all()
        self.assertEqual(len(stones), 3)

        fields = self.expected_stones[0].keys()

        for actual_stone, expected_stone in zip(stones, self.expected_stones):
            for field in fields:
                raw_actual_value = getattr(actual_stone, field)
                actual_value = float(raw_actual_value) if type(raw_actual_value) == Decimal else raw_actual_value
                expected_value = expected_stone[field]
                self.assertEqual(actual_value, expected_value)
                holder = StoneTransfer.most_recent_transfer(item=actual_stone).to_user
                split = User.objects.get(username="split")
                self.assertEqual(holder, split)


class BasicUploadFormTest(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.sarine_csv_file = open("grading/tests/fixtures/sarine-01.csv", "rb")

        self.csv_file = open("grading/tests/fixtures/basic-01.csv", "rb")
        self.csv_file_spaces = open("grading/tests/fixtures/basic-01-spaces.csv", "rb")

        self.grader = User.objects.get(username="tanly")

        self.expected_stones = [
            {
                "internal_id": 1,
                "basic_diamond_description": "NATURAL",
                "basic_grader_1": User.objects.get(username="gary"),
                "basic_grader_2": User.objects.get(username="kary"),
                "basic_grader_3": User.objects.get(username="tanly"),
                "basic_carat": 0.09,
                "basic_color_1": "F+",
                "basic_color_2": "F",
                "basic_color_3": "F+",
                "basic_color_final": "F",
                "basic_clarity_1": "SI1",
                "basic_clarity_2": "SI1",
                "basic_clarity_3": "SI1+",
                "basic_clarity_final": "SI1",
                "basic_fluorescence_1": "N",
                "basic_fluorescence_2": "N",
                "basic_fluorescence_3": "N",
                "basic_fluorescence_final": "N",
                "basic_culet_1": "N",
                "basic_culet_2": "N",
                "basic_culet_3": "N",
                "basic_culet_final": "N",
                "basic_culet_characteristic_1": "N",
                "basic_culet_characteristic_2": "N",
                "basic_culet_characteristic_3": "N",
                "basic_culet_characteristic_final": "N",
                "basic_girdle_condition_1": "FAC",
                "basic_girdle_condition_2": "FAC",
                "basic_girdle_condition_3": "FAC",
                "basic_girdle_condition_final": "FAC",
                "basic_inclusions_1": "Cld, Xtl",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Cld, Xtl")],
                "basic_inclusions_2": "Cld, Xtl, IndN",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Cld, Xtl, IndN")],
                "basic_inclusions_3": "Cld, IndN",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Cld, IndN")],
                "basic_inclusions_final": "Cld, IndN",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Cld, IndN")],
                "basic_polish_1": "GD",
                "basic_polish_2": "GD",
                "basic_polish_3": "VG",
                "basic_polish_final": "VG",
                "girdle_min_grade": "STK",
                "basic_girdle_min_grade_final": "STK",
                "basic_remarks": "",
            },
            {
                "internal_id": 5,
                "basic_diamond_description": "NATURAL",
                "basic_grader_1": User.objects.get(username="gary"),
                "basic_grader_2": User.objects.get(username="kary"),
                "basic_grader_3": User.objects.get(username="tanly"),
                "basic_carat": 0.09,
                "basic_color_1": "F",
                "basic_color_2": "F",
                "basic_color_3": "F+",
                "basic_color_final": "F",
                "basic_clarity_1": "VS2",
                "basic_clarity_2": "VS2",
                "basic_clarity_3": "VS1",
                "basic_clarity_final": "VS1",
                "basic_fluorescence_1": "N",
                "basic_fluorescence_2": "N",
                "basic_fluorescence_3": "N",
                "basic_fluorescence_final": "N",
                "basic_culet_1": "N",
                "basic_culet_2": "N",
                "basic_culet_3": "N",
                "basic_culet_final": "N",
                "basic_culet_characteristic_1": "N",
                "basic_culet_characteristic_2": "N",
                "basic_culet_characteristic_3": "N",
                "basic_culet_characteristic_final": "N",
                "basic_girdle_condition_1": "FAC",
                "basic_girdle_condition_2": "FAC",
                "basic_girdle_condition_3": "FAC",
                "basic_girdle_condition_final": "FAC",
                "basic_inclusions_1": "Xtl, Ftr",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Xtl, Ftr")],
                "basic_inclusions_2": "Xtl",  # Inclusion.objects.get(inclusion="Xtl"),
                "basic_inclusions_3": "Cld",  # Inclusion.objects.get("Cld"),
                "basic_inclusions_final": "Cld",  # Inclusion.objects.get(inclusion="Cld"),
                "basic_polish_1": "GD",
                "basic_polish_2": "GD",
                "basic_polish_3": "VG",
                "basic_polish_final": "VG",
                "girdle_min_grade": "MED",
                "basic_girdle_min_grade_final": "MED",
                "basic_remarks": "",
            },
            {
                "internal_id": 6,
                "basic_diamond_description": "NATURAL",
                "basic_grader_1": User.objects.get(username="gary"),
                "basic_grader_2": User.objects.get(username="kary"),
                "basic_grader_3": User.objects.get(username="tanly"),
                "basic_carat": 0.09,
                "basic_color_1": "F",
                "basic_color_2": "F",
                "basic_color_3": "F",
                "basic_color_final": "F",
                "basic_clarity_1": "VS2",
                "basic_clarity_2": "VS2",
                "basic_clarity_3": "VS1",
                "basic_clarity_final": "VS1",
                "basic_fluorescence_1": "N",
                "basic_fluorescence_2": "N",
                "basic_fluorescence_3": "N",
                "basic_fluorescence_final": "N",
                "basic_culet_1": "N",
                "basic_culet_2": "N",
                "basic_culet_3": "N",
                "basic_culet_final": "N",
                "basic_culet_characteristic_1": "N",
                "basic_culet_characteristic_2": "N",
                "basic_culet_characteristic_3": "N",
                "basic_culet_characteristic_final": "N",
                "basic_girdle_condition_1": "FAC",
                "basic_girdle_condition_2": "FAC",
                "basic_girdle_condition_3": "FAC",
                "basic_girdle_condition_final": "FAC",
                "basic_inclusions_1": "Xtl, Cld, IndN",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Xtl, Cld, IndN")],
                "basic_inclusions_2": "Xtl, Cld",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Xtl, Cld")],
                "basic_inclusions_3": "Cld, Xtl",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Cld, Xtl")],
                "basic_inclusions_final": "Cld, Xtl",
                # [Inclusion.objects.get(inclusion=inclusion) for inclusion in ("Cld, Xtl")],
                "basic_polish_1": "EX",
                "basic_polish_2": "EX",
                "basic_polish_3": "EX",
                "basic_polish_final": "EX",
                "girdle_min_grade": "STK",
                "basic_girdle_min_grade_final": "STK",
                "basic_remarks": "",
            },
        ]

    def do_sarine_upload(self):
        """
        Perform sarine upload before Basic upload
        :return:
        """
        Stone.objects.all().delete()
        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.sarine_csv_file.name, self.sarine_csv_file.read())},
            user=User.objects.get(username="gary"),
        )
        if form.is_valid():
            form.save()

    def test_csv_file_is_valid(self):
        """
        Tests csv file True validation
        """
        self.do_sarine_upload()
        # No column spaces
        form = BasicUploadForm(
            data={},
            user=self.grader,
            files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())},
        )
        self.assertTrue(form.is_valid())

    def test_csv_file_is_valid_for_csv_with_column_spaces(self):
        self.do_sarine_upload()
        # With column spaces
        form = BasicUploadForm(
            data={},
            user=self.grader,
            files={"file": SimpleUploadedFile(self.csv_file_spaces.name, self.csv_file_spaces.read())},
        )
        self.assertTrue(form.is_valid())

    def test_save_updates_stones(self):
        self.do_sarine_upload()

        form = BasicUploadForm(
            data={},
            user=self.grader,
            files={"file": SimpleUploadedFile(self.csv_file_spaces.name, self.csv_file_spaces.read())},
        )
        self.assertTrue(form.is_valid())
        form.save()

        stones = Stone.objects.all()

        self.assertEqual(len(stones), 3)

        fields = self.expected_stones[0].keys()

        for actual_stone, expected_stone in zip(stones, self.expected_stones):
            for field in fields:
                raw_actual_value = getattr(actual_stone, field)
                actual_value = float(raw_actual_value) if type(raw_actual_value) == Decimal else raw_actual_value
                expected_value = expected_stone[field]

                if "inclusion" not in field:
                    self.assertEqual(actual_value, expected_value)


def get_date_from_str(date_string):
    day, month, year = [int(value) for value in date_string.split("/")]
    return datetime(year, month, day, tzinfo=utc)


class GoldWayGradingDataTest(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.sarine_csv_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        self.basic_csv_file = open("grading/tests/fixtures/basic-01-spaces.csv", "rb")
        self.csv_file = open("grading/tests/fixtures/gold_way-01.csv", "rb")

        self.grader = User.objects.get(username="tanly")

        self.do_initial_uploads()

        self.expected_stones = [
            {
                "internal_id": 1,
                "date_from_gw": get_date_from_str("26/2/2021"),
                # "goldway_code": "SIOT202101003",
                # "nano_etch_inscription": "G00000028",
                "gw_return_reweight": 0.09,
                "gw_color": "E",
                "gw_clarity": "VVS2",
                "gw_fluorescence": "M",
                "gw_remarks": "",
            },
            {
                "internal_id": 5,
                "date_from_gw": get_date_from_str("26/2/2021"),
                # "goldway_code": "SIOT202101003",
                # "nano_etch_inscription": "G00000030",
                "gw_return_reweight": 0.1,
                "gw_color": "F",
                "gw_clarity": "VS2",
                "gw_fluorescence": "F",
                "gw_remarks": "",
            },
            {
                "internal_id": 6,
                "date_from_gw": get_date_from_str("26/2/2021"),
                # "goldway_code": "SIOT202101003",
                # "nano_etch_inscription": "G00000031",
                "gw_return_reweight": 0.1,
                "gw_color": "D",
                "gw_clarity": "VVS2",
                "gw_fluorescence": "M",
                "gw_remarks": "",
            },
        ]

    def do_initial_uploads(self):
        # Sarine Upload setup
        Stone.objects.all().delete()
        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.sarine_csv_file.name, self.sarine_csv_file.read())},
            user=User.objects.get(username="gary"),
        )
        if form.is_valid():
            form.save()

        # Basic Upload setup
        form = BasicUploadForm(
            data={},
            user=self.grader,
            files={"file": SimpleUploadedFile(self.basic_csv_file.name, self.basic_csv_file.read())},
        )
        if form.is_valid():
            form.save()

    def test_save_updates_stones(self):
        form = GWGradingUploadForm(
            data={}, user=self.grader, files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())}
        )

        for stone_id in (1, 5, 6):
            stone = Stone.objects.get(internal_id=stone_id)
            split = User.objects.get(username="split")
            goldway = User.objects.get(username="goldway")

            # Transfer stones
            StoneTransfer.initiate_transfer(item=stone, from_user=split, to_user=goldway, created_by=self.grader)
            StoneTransfer.confirm_received(item=stone)

        self.assertTrue(form.is_valid())
        form.save()

        stones = Stone.objects.all()

        self.assertEqual(len(stones), 3)

        fields = self.expected_stones[0].keys()

        for actual_stone, expected_stone in zip(stones, self.expected_stones):
            for field in fields:
                raw_actual_value = getattr(actual_stone, field)
                actual_value = float(raw_actual_value) if type(raw_actual_value) == Decimal else raw_actual_value
                expected_value = expected_stone[field]
                self.assertEqual(actual_value, expected_value)

                holder = StoneTransfer.most_recent_transfer(item=actual_stone).to_user
                vault = User.objects.get(username="vault")
                self.assertEqual(holder, vault)


class GiaGradingUploadForm(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.sarine_csv_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        self.basic_csv_file = open("grading/tests/fixtures/basic-01.csv", "rb")
        self.csv_file = open("grading/tests/fixtures/gia.csv", "rb")
        self.csv_file_spaces = open("grading/tests/fixtures/basic-01-spaces.csv", "rb")

        self.do_initial_upload()

        self.user = User.objects.get(username="vault")

        self.expected_stones = [
            {
                "internal_id": 1,
                "date_from_gia": get_date_from_str("29/12/2020"),
                # "nano_etch_inscription": "G00000011",
                "gia_verification": "1379074279-926",
                "gia_diamond_description": "natural",
                "gia_color": "D-F",
                "gia_remarks": "",
            },
            {
                "internal_id": 5,
                "date_from_gia": get_date_from_str("29/12/2020"),
                # "nano_etch_inscription": "G00000012",
                "gia_verification": "1379074279-428",
                "gia_diamond_description": "natural",
                "gia_color": "G-H",
                "gia_remarks": "",
            },
            {
                "internal_id": 6,
                "date_from_gia": get_date_from_str("29/12/2020"),
                # "nano_etch_inscription": "G00000013",
                "gia_verification": "1379074279-926",
                "gia_diamond_description": "natural",
                "gia_color": "D-F",
                "gia_remarks": "",
            },
        ]

    def do_initial_upload(self):
        Stone.objects.all().delete()
        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.sarine_csv_file.name, self.sarine_csv_file.read())},
            user=User.objects.get(username="gary"),
        )
        if form.is_valid():
            form.save()

        form = BasicUploadForm(
            data={},
            user=User.objects.get(username="gary"),
            files={"file": SimpleUploadedFile(self.basic_csv_file.name, self.basic_csv_file.read())},
        )
        if form.is_valid():
            form.save()

    def test_save_updates_stones(self):
        """
        Tests that stones get updated when form.save() is called
        :returns:
        """
        # Send stones to GIA
        for stone_id in (1, 5, 6):
            stone = Stone.objects.get(internal_id=stone_id)
            split = User.objects.get(username="split")
            gia = User.objects.get(username="gia")
            StoneTransfer.initiate_transfer(item=stone, from_user=split, to_user=gia, created_by=self.user)
            StoneTransfer.confirm_received(item=stone)

        form = GIAUploadForm(
            data={}, user=self.user, files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())}
        )

        self.assertTrue(form.is_valid())
        form.save()

        stones = Stone.objects.all()

        self.assertEqual(len(stones), 3)

        fields = self.expected_stones[0].keys()

        for actual_stone, expected_stone in zip(stones, self.expected_stones):
            for field in fields:
                raw_actual_value = getattr(actual_stone, field)
                actual_value = float(raw_actual_value) if type(raw_actual_value) == Decimal else raw_actual_value
                expected_value = expected_stone[field]

                if field == "gia_verification":
                    expected_value = GiaVerification.objects.get(receipt_number=expected_value)

                self.assertEqual(actual_value, expected_value)


class GWAdjustingUploadFormTest(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.sarine_csv_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        self.csv_file = open("grading/tests/fixtures/gw_adjust.csv", "rb")

        self.expected_stones = [
            {
                "internal_id": 1,
                "gw_adjust_grader_1": User.objects.get(username="kary"),
                "gw_adjust_grader_2": User.objects.get(username="tanly"),
                "gw_adjust_grader_3": User.objects.get(username="gary"),
                "gw_color_adjusted_1": "D",
                "gw_color_adjusted_2": "F",
                "gw_color_adjusted_3": "E",
                "gw_color_adjusted_final": "D",
                "gw_clarity_adjusted_1": "SI1",
                "gw_clarity_adjusted_2": "SI1",
                "gw_clarity_adjusted_3": "SI1+",
                "gw_clarity_adjusted_final": "SI1",
                "gw_fluorescence_adjusted_1": "N",
                "gw_fluorescence_adjusted_2": "N",
                "gw_fluorescence_adjusted_3": "N",
                "gw_fluorescence_adjusted_final": "N",
                "gw_adjust_remarks": "nothing really",
            },
            {
                "internal_id": 5,
                "gw_adjust_grader_1": User.objects.get(username="kary"),
                "gw_adjust_grader_2": User.objects.get(username="tanly"),
                "gw_adjust_grader_3": User.objects.get(username="gary"),
                "gw_color_adjusted_1": "D",
                "gw_color_adjusted_2": "F",
                "gw_color_adjusted_3": "E",
                "gw_color_adjusted_final": "D",
                "gw_clarity_adjusted_1": "SI1",
                "gw_clarity_adjusted_2": "SI1",
                "gw_clarity_adjusted_3": "SI1+",
                "gw_clarity_adjusted_final": "SI1",
                "gw_fluorescence_adjusted_1": "N",
                "gw_fluorescence_adjusted_2": "N",
                "gw_fluorescence_adjusted_3": "N",
                "gw_fluorescence_adjusted_final": "N",
                "gw_adjust_remarks": "nothing really",
            },
            {
                "internal_id": 6,
                "gw_adjust_grader_1": User.objects.get(username="kary"),
                "gw_adjust_grader_2": User.objects.get(username="tanly"),
                "gw_adjust_grader_3": User.objects.get(username="gary"),
                "gw_color_adjusted_1": "D",
                "gw_color_adjusted_2": "F",
                "gw_color_adjusted_3": "E",
                "gw_color_adjusted_final": "D",
                "gw_clarity_adjusted_1": "SI1",
                "gw_clarity_adjusted_2": "SI1",
                "gw_clarity_adjusted_3": "SI1+",
                "gw_clarity_adjusted_final": "SI1",
                "gw_fluorescence_adjusted_1": "N",
                "gw_fluorescence_adjusted_2": "N",
                "gw_fluorescence_adjusted_3": "N",
                "gw_fluorescence_adjusted_final": "N",
                "gw_adjust_remarks": "nothing really",
            },
        ]

    def do_initial_upload(self):
        """
        Do initial uploads to create stones for updating
        :return:
        """
        Stone.objects.all().delete()
        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.sarine_csv_file.name, self.sarine_csv_file.read())},
            user=User.objects.get(username="gary"),
        )
        if form.is_valid():
            form.save()

    def test_save_updates_stones(self):
        """
        Tests that save method updates stone correctly
        :return:
        """
        self.do_initial_upload()
        form = GWAdjustingUploadForm(
            data={}, files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())}
        )
        self.assertTrue(form.is_valid())
        form.save()
        stones = Stone.objects.all()

        self.assertEqual(len(stones), 3)

        fields = self.expected_stones[0].keys()

        for actual_stone, expected_stone in zip(stones, self.expected_stones):
            for field in fields:
                raw_actual_value = getattr(actual_stone, field)
                actual_value = float(raw_actual_value) if type(raw_actual_value) == Decimal else raw_actual_value
                expected_value = expected_stone[field]
                self.assertEqual(actual_value, expected_value)


class GiaAdjustGradingUploadFormTest(TestCase):
    fixtures = ("grading/fixtures/test_data.json",)

    def setUp(self):
        self.sarine_csv_file = open("grading/tests/fixtures/sarine-01.csv", "rb")
        self.csv_file = open("grading/tests/fixtures/gia_adjusting.csv", "rb")

        self.expected_stones = [
            {
                "internal_id": 1,
                "gia_adjust_grader_1": User.objects.get(username="tanly"),
                "gia_adjust_grader_2": User.objects.get(username="kary"),
                "gia_adjust_grader_3": User.objects.get(username="gary"),
                "gia_color_adjusted_1": "E",
                "gia_color_adjusted_2": "F",
                "gia_color_adjusted_3": "D",
                "gia_color_adjusted_final": "E",
                "gia_polish_adjusted_1": "EX",
                "gia_polish_adjusted_2": "GD",
                "gia_polish_adjusted_3": "GD",
                "gia_polish_adjusted_final": "VG",
                "gia_culet_adjusted_1": "N",
                "gia_culet_adjusted_2": "N",
                "gia_culet_adjusted_3": "N",
                "gia_culet_adjusted_final": "N",
                "gia_culet_characteristic_1": "N",
                "gia_culet_characteristic_2": "N",
                "gia_culet_characteristic_3": "N",
                "gia_culet_characteristic_final": "N",
                "gia_adjust_remarks": "",
            },
            {
                "internal_id": 5,
                "gia_adjust_grader_1": User.objects.get(username="tanly"),
                "gia_adjust_grader_2": User.objects.get(username="kary"),
                "gia_adjust_grader_3": User.objects.get(username="gary"),
                "gia_color_adjusted_1": "E",
                "gia_color_adjusted_2": "F",
                "gia_color_adjusted_3": "D",
                "gia_color_adjusted_final": "E",
                "gia_polish_adjusted_1": "EX",
                "gia_polish_adjusted_2": "GD",
                "gia_polish_adjusted_3": "GD",
                "gia_polish_adjusted_final": "VG",
                "gia_culet_adjusted_1": "N",
                "gia_culet_adjusted_2": "N",
                "gia_culet_adjusted_3": "N",
                "gia_culet_adjusted_final": "N",
                "gia_culet_characteristic_1": "N",
                "gia_culet_characteristic_2": "N",
                "gia_culet_characteristic_3": "N",
                "gia_culet_characteristic_final": "N",
                "gia_adjust_remarks": "",
            },
            {
                "internal_id": 6,
                "gia_adjust_grader_1": User.objects.get(username="tanly"),
                "gia_adjust_grader_2": User.objects.get(username="kary"),
                "gia_adjust_grader_3": User.objects.get(username="gary"),
                "gia_color_adjusted_1": "E",
                "gia_color_adjusted_2": "F",
                "gia_color_adjusted_3": "D",
                "gia_color_adjusted_final": "E",
                "gia_polish_adjusted_1": "EX",
                "gia_polish_adjusted_2": "GD",
                "gia_polish_adjusted_3": "GD",
                "gia_polish_adjusted_final": "VG",
                "gia_culet_adjusted_1": "N",
                "gia_culet_adjusted_2": "N",
                "gia_culet_adjusted_3": "N",
                "gia_culet_adjusted_final": "N",
                "gia_culet_characteristic_1": "N",
                "gia_culet_characteristic_2": "N",
                "gia_culet_characteristic_3": "N",
                "gia_culet_characteristic_final": "N",
                "gia_adjust_remarks": "",
            },
        ]

    def do_initial_upload(self):
        """
        Do initial uploads to create stones for updating
        :return:
        """
        Stone.objects.all().delete()
        form = SarineUploadForm(
            data={},
            files={"file": SimpleUploadedFile(self.sarine_csv_file.name, self.sarine_csv_file.read())},
            user=User.objects.get(username="gary"),
        )
        if form.is_valid():
            form.save()

    def test_save_updates_stones(self):
        """
        Tests that save method updates stone correctly
        :return:
        """
        self.do_initial_upload()
        form = GIAAdjustingUploadForm(
            data={}, files={"file": SimpleUploadedFile(self.csv_file.name, self.csv_file.read())}
        )
        self.assertTrue(form.is_valid())
        form.save()
        stones = Stone.objects.all()

        self.assertEqual(len(stones), 3)

        fields = self.expected_stones[0].keys()

        for actual_stone, expected_stone in zip(stones, self.expected_stones):
            for field in fields:
                raw_actual_value = getattr(actual_stone, field)
                actual_value = float(raw_actual_value) if type(raw_actual_value) == Decimal else raw_actual_value
                expected_value = expected_stone[field]
                self.assertEqual(actual_value, expected_value)

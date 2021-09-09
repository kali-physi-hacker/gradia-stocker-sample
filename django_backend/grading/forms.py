import os
from datetime import datetime

import pandas as pd
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.timezone import utc

from stonegrading.mixins import SarineGradingMixin, BasicGradingMixin

from ownerships.models import ParcelTransfer, StoneTransfer

from .models import Parcel, Receipt, Stone, Split


User = get_user_model()

number_input = forms.NumberInput(attrs={"style": "width: 50px"})
text_input = forms.TextInput(attrs={"size": 1})
longer_text_input = forms.TextInput(attrs={"size": 3})
text_area = forms.Textarea(attrs={"style": "width: 100px; height: 50px"})


class StoneForm(forms.ModelForm):
    class Meta:
        widgets = {
            "color": text_input,
            "grader_1_color": text_input,
            "grader_2_color": text_input,
            "grader_3_color": text_input,
            "clarity": longer_text_input,
            "grader_1_clarity": longer_text_input,
            "grader_2_clarity": longer_text_input,
            "grader_3_clarity": longer_text_input,
            "fluo": text_input,
            "culet": text_input,
            "stone_id": forms.TextInput(attrs={"size": 8}),
            "sequence_number": number_input,
            "carats": number_input,
            "inclusions": text_area,
            "rejection_remarks": text_area,
            "table_pct": number_input,
            "pavilion_depth_pct": number_input,
            "total_depth_pct": number_input,
            "general_comments": text_area,
            "measurement": forms.TextInput(attrs={"size": 20}),
            "crown_angle": number_input,
            "girdle_thickness": forms.TextInput(attrs={"size": 11}),
            "polish": longer_text_input,
            "symmetry": longer_text_input,
            "cut": longer_text_input,
        }


class CSVImportForm(forms.Form):
    file = forms.FileField()


sarine_fields = [field.name for field in SarineGradingMixin._meta.get_fields()] + ["internal_id"]


class SarineDataForm(forms.ModelForm):
    internal_id = forms.IntegerField()

    class Meta:
        model = SarineGradingMixin
        fields = [field.name for field in SarineGradingMixin._meta.get_fields()]


class SarineUploadForm(forms.Form):
    file = forms.FileField()

    parcel = None
    __csv_errors = None
    __cleaned_stone_data = None
    __stone_data = []

    def __init__(self, user, *args, **kwargs):
        """
        Overriding constructor to provide ability to accept current user
        :param user:
        :param args:
        :param kwargs:
        """
        super(SarineUploadForm, self).__init__(*args, **kwargs)
        self.user = user

    @property
    def csv_errors(self):
        """
        Return the errors of the csv content, similar to forms.errors
        :return:
        """
        if self.__csv_errors is None:
            raise Exception("You need to call form.is_valid() first")

        return self.__csv_errors

    @property
    def cleaned_stone_data(self):
        """
        Returns a list of stones if there are no validation issues
        :return:
        """
        if self.__cleaned_stone_data is None:
            return []

        return self.__cleaned_stone_data

    @property
    def stone_data(self):
        return self.__stone_data

    def __to_db_name(self, data):
        """
        Change from display name to db name
        :return:
        """
        data = data.copy()

        # cleaning for grades
        grade_fields = [field for field in sarine_fields if "grade" in field] + [
            "sarine_cut_pre_polish_symmetry",
            "sarine_symmetry",
        ]
        grade_fields.remove("girdle_min_grade")
        grade_fields.remove("girdle_max_grade")

        choices_display_name_map = {"EXCELLENT": "EX", "VERY GOOD": "VG", "GOOD": "GD", "FAIR": "F", "POOR": "P"}

        for field in grade_fields:
            if data[field] is not None:
                data[field] = choices_display_name_map.get(data[field].upper()) or data[field]

        # cleaning for culet_descriptions
        culet_choices_display_map = {
            "NONE": "N",
            "VERY SMALL": "VS",
            "SMALL": "S",
            "MEDIUM": "M",
            "SLIGHTLY LARGE": "SL",
            "LARGE": "L",
            "VERY LARGE": "VL",
            "EXTREMELY LARGE": "XL",
        }

        data["culet_size_description"] = "/".join(
            [
                culet_choices_display_map.get(size.strip().upper())
                for size in data["culet_size_description"].split("/")
            ]
        )

        return data

    def __process_csv_content(self, csv_file):
        """
        Process and clean the content of the csv file and return a list of stone (which are dictionaries)
        :param csv_file:
        :return:
        """
        csv_data = pd.read_csv(csv_file)
        data_frame = csv_data.rename(str.strip, axis="columns")
        data_frame = pd.DataFrame(data_frame, columns=sarine_fields)
        stone_data = [dict(zip(sarine_fields, data)) for data in data_frame.values]

        for data in stone_data:
            for column in data:
                if pd.isna(data[column]):
                    data[column] = None

        stone_data = [self.__to_db_name(data) for data in stone_data]

        # clean for height and girdle_min_grade
        for data in stone_data:
            try:
                data["height"] = round(float(data["height"]), 2)
            except ValueError:
                pass

            data["girdle_min_grade"] = (
                data["girdle_min_grade"].upper()
                if type(data["girdle_min_grade"]) == str
                else data["girdle_min_grade"]
            )

        self.__stone_data = stone_data
        return stone_data

    def __build_error_dict(self, data):
        """
        Create a form instance and return form errors if it exists
        :param data:
        :return:
        """
        errors = {}
        for row, _dt in enumerate(data):
            form = SarineDataForm(_dt)
            if not form.is_valid():
                errors[row] = form.errors

        return errors

    def clean(self):
        """
        Clean the csv file and check for some errors
        :return:
        """
        cleaned_data = super(SarineUploadForm, self).clean()

        # Invalid csv file name
        file = cleaned_data["file"]
        gradia_parcel_code = os.path.splitext(file.name)[0]

        try:
            self.parcel = Parcel.objects.get(gradia_parcel_code=gradia_parcel_code)
        except Parcel.DoesNotExist:
            raise ValidationError(
                {
                    "file": "No parcel with such a parcel code. Please be sure the csv file name matches the parcel code"
                }
            )

        stone_data = self.__process_csv_content(file)

        form_errors = self.__build_error_dict(stone_data)

        if form_errors:
            self.__csv_errors = form_errors
            raise ValidationError({"file": "CSV File Validation Error"})

        self.__csv_errors = {}
        return stone_data

    def save(self):
        """
        Create and return a list of stones
        :return:
        """
        stones = []

        split = Split.objects.create(original_parcel=self.parcel, split_by=self.user)

        for stone_data in self.cleaned_data:

            stone_data["data_entry_user"] = self.user  # refactor
            stone_data["split_from"] = split
            stone = Stone.objects.create(**stone_data)

            parcel_transfer = ParcelTransfer.most_recent_transfer(self.parcel)

            if parcel_transfer is None:
                parcel_owner = User.objects.get(username="split")
            else:
                parcel_owner = parcel_transfer.from_user

            StoneTransfer.objects.create(
                item=stone,
                from_user=User.objects.get(username="split"),
                created_by=self.user,
                to_user=parcel_owner,
                confirmed_date=datetime.utcnow().replace(tzinfo=utc),
            )

            stones.append(stone)

        return stones


class BasicFormData(forms.ModelForm):
    class Meta:
        model = BasicGradingMixin
        fields = "__all__"

    def clean(self):
        """"""
        # clean basic_girdle_min_grade_final
        for data in stone_data:
            data["basic_girdle_min_grade_final"] = (
                data["basic_girdle_min_grade_final"].upper()
                if type(data["basic_girdle_min_grade_final"]) == str
                else data["basic_girdle_min_grade_final"]
            )

        # clean inclusion
        self.__process_inclusions()

        # clean graders
        self.__process_csv_graders()


class BasicUploadForm(forms.Form):
    file = forms.FileField()

    parcel = None
    __csv_errors = None
    __cleaned_stone_data = None
    __stone_data = []

    @property
    def csv_errors(self):
        """
        Return the errors of the csv content, similar to forms.errors
        :return:
        """
        if self.__csv_errors is None:
            raise Exception("You need to call form.is_valid() first")

        return self.__csv_errors

    @property
    def cleaned_stone_data(self):
        """
        Returns a list of stones if there are no validation issues
        :return:
        """
        if self.__cleaned_stone_data is None:
            return []

        return self.__cleaned_stone_data

    @property
    def stone_data(self):
        return self.__stone_data

    def __to_db_name(self, data):
        """
        Change from display name to db name
        :return:
        """
        data = data.copy()

        # cleaning for grades
        fields = (
            "basic_diamond_description",
            "basic_girdle_condition_*",
        )

    def __process_graders(self, data_dict):
        """"""
        pass

    def __process_csv_content(self, csv_file):
        """
        Process and clean the content of the csv file and return a list of stone (which are dictionaries)
        :param csv_file:
        :return:
        """
        csv_data = pd.read_csv(csv_file)
        data_frame = csv_data.rename(str.strip, axis="columns")
        data_frame = pd.DataFrame(data_frame, columns=sarine_fields)
        stone_data = [dict(zip(sarine_fields, data)) for data in data_frame.values]

        for data in stone_data:
            for column in data:
                if pd.isna(data[column]):
                    data[column] = None

        stone_data = [self.__to_db_name(data) for data in stone_data]

        self.__stone_data = stone_data
        return stone_data

    def __build_error_dict(self, data):
        """
        Create a form instance and return form errors if it exists
        :param data:
        :return:
        """
        errors = {}
        for row, _dt in enumerate(data):
            form = BasicFormData(_dt)
            if not form.is_valid():
                errors[row] = form.errors

        return errors

    def clean(self):
        """
        Clean the csv file and check for some errors
        :return:
        """
        cleaned_data = super(BasicUploadForm, self).clean()

        file = cleaned_data["file"]
        stone_data = self.__process_csv_content(file)

        form_errors = self.__build_error_dict(stone_data)

        if form_errors:
            self.__csv_errors = form_errors
            raise ValidationError({"file": "CSV File Validation Error"})

        self.__csv_errors = {}
        return stone_data

    def save(self):
        """
        Update current stone and return a list of stones
        :return:
        """

        # ignore girdle_min_grade

        stones = []

        for stone_data in self.cleaned_data:
            stone = Stone.objects.get(internal_id=stone_data["internal_id"])
            for field, value in stone_data.items():
                setattr(stone, field, value)

            inclusions = self.__inclusions
            for inclusion in inclusions:
                stone.inclusion.add(inclusion)

            stone.save()

            stones.append(stone)

        return stones

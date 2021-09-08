import os
from datetime import datetime

import pandas as pd
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.timezone import utc

from stonegrading.mixins import SarineGradingMixin

from ownerships.models import ParcelTransfer, StoneTransfer

from .models import Parcel, Receipt, Stone, Split, BasicGradingMixin


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


def get_error_headers(error_dict):
    """
    Returns a list of headers given a dict
    :param error_dict:
    returns:
    """
    error_headers = []
    for errors in error_dict:
        for error in error_dict[errors]:
            if error not in error_headers:
                error_headers.append(error)

    return error_headers


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

    def errors_as_table(self):
        """
        Return html table of the errors
        :return:
        """
        error_columns = get_error_headers(self.csv_errors)
        table_head = (
            "<thead><tr><th>Row No.</th>"
            + "".join([f"<th>{column}</th>" for column in error_columns])
            + "</tr></thead>"
        )
        table_rows = ""

        for _, error_dict in self.csv_errors.items():
            row = f"<tr><td>{int(_)+1}</td>"
            for column, error in error_dict.items():
                for error_column in error_columns:
                    if error_column == column:
                        row += f'<td class="error">{error[0]}</td>'
                    else:
                        row += '<td><i class="fas fa-check"></i></td>'
                row += "</tr>"
            table_rows += row
        table_body = f"<tbody>{table_rows}</tbody>"
        html_string = f"<table>{table_head}{table_body}</table>"
        return html_string

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


class BasicUploadForm(forms.Form):
    carat = forms.CharField()

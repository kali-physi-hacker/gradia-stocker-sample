import os
from datetime import datetime

import pandas as pd
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import utc
from ownerships.models import ParcelTransfer, StoneTransfer
from stonegrading.grades import GirdleGrades
from stonegrading.mixins import SarineGradingMixin, BasicGradingMixin
from stonegrading.models import Inclusion

from .models import Parcel, Stone, Split

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


class UploadFormMetaClass(type(forms.Form)):
    def __new__(cls, name, bases, clsdict):
        """
        Create the class object, get all processing / validation methods and assign to class
        :param name:
        :param bases:
        :param clsdict:
        """
        clsobj = super().__new__(cls, name, bases, clsdict)

        callables = [attr for _, attr in clsdict.items() if callable(attr)]

        processing_methods = [method for method in callables if method.__name__.startswith("__process_")]

        setattr(clsobj, "processing_methods", processing_methods)

        return clsobj


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


class BaseUploadForm(forms.Form, metaclass=UploadFormMetaClass):
    file = forms.FileField()

    __csv_errors = None
    __cleaned_stone_data = None
    __stone_data = []

    def __init__(self, *args, **kwargs):
        super(BaseUploadForm, self).__init__(*args, **kwargs)

        # raise a ValueError exception if no Meta class is define
        if not hasattr(self, "Meta"):
            raise ValueError("You need to define a class `Meta` for extra data")

        # raise a ValueError exception if no fields and model attributes are defined within the class Meta.
        # if not hasattr(self.Meta, "fields"):
        #     raise ValueError("You need to specify `fields` attribute in the Meta class")

        if not hasattr(self.Meta, "mixin"):
            raise ValueError("You need to specify `mixin` attribute in the Meta class")

        self.mixin_fields = [field.name for field in self.Meta.mixin._meta.get_fields()]

        if hasattr(self.Meta, "extra_fields"):
            self.extra_fields = self.Meta.extra_fields

        self.mixin = self.Meta.mixin

        extra_fields = [
            {field_name: field} for field_name, field in self.Meta.__dict__.items() if isinstance(field, forms.Field)
        ]

        self.all_fields = self.mixin_fields + ["internal_id"]

        stone_data_class = self.__get_data_class(self.mixin)
        for field_dict in extra_fields:
            for field, value in field_dict.items():
                self.all_fields.append(field)
                setattr(stone_data_class, field, value)

        setattr(self, "StoneDataForm", stone_data_class)

    def __get_data_class(self, mixin):
        """
        Creates and returns StoneDataForm form modelling
        :param mixin:
        :return:
        """

        class StoneDataForm(forms.ModelForm):
            internal_id = forms.IntegerField()

            class Meta:
                fields = [field.name for field in mixin._meta.get_fields()]
                model = mixin

        return StoneDataForm

    @property
    def csv_errors(self):
        """
        Return the errors of the csv content, similar to forms.errors
        :return:
        """
        if self.__csv_errors is None:
            raise ValueError("You need to call form.is_valid() first")

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

    def __build_error_dict(self, data):
        """
        Create a form instance and return form errors if it exists
        :param data:
        :return:
        """
        errors = {}
        for row, _dt in enumerate(data):
            form = self.StoneDataForm(_dt)
            if not form.is_valid():
                errors[row] = form.errors

        return errors

    def __to_db_name(self, data):
        """
        Change from display name to db name
        :return:
        """
        data = data.copy()

        # cleaning for grades
        grade_fields = [field for field in self.all_fields if "grade" in field] + [
            "sarine_cut_pre_polish_symmetry",
            "sarine_symmetry",
        ]
        for field in ("girdle_min_grade", "girdle_max_grade"):
            if field in grade_fields:
                grade_fields.remove(field)

        choices_display_name_map = {"EXCELLENT": "EX", "VERY GOOD": "VG", "GOOD": "GD", "FAIR": "F", "POOR": "P"}

        for field in grade_fields:
            if data.get(field) is not None:
                try:
                    data[field] = choices_display_name_map.get(data[field].upper().strip()) or data[field].strip()
                except:
                    data[field] = data[field]

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

        # Make uppercase
        fields = (
            "basic_diamond_description",
            "basic_girdle_condition_1",
            "basic_girdle_condition_2",
            "basic_girdle_condition_3",
            "basic_girdle_condition_final",
            "culet_size_description",
        )

        for field in fields:
            if field in data:
                data[field] = data[field].upper().strip()

        if "culet_size_description" in data:
            data["culet_size_description"] = "/".join(
                [culet_choices_display_map.get(size.strip()) for size in data["culet_size_description"].split("/")]
            )

        # Girdle conditions
        girdle_conditions_choices_map = {"FACETED": "FAC", "POLISHED": "POL", "BRUTED": "BRU"}

        for field, value in data.items():
            if "girdle_condition" in field:
                data[field] = (
                    girdle_conditions_choices_map[value.upper()] if value in girdle_conditions_choices_map else value
                )

        # process inclusions
        # Below code applies if we want to be very specific about which inclusion in the string is not valid
        # inclusions = [inclusion for inclusion in Inclusions.__dict__.keys() if "__" not in inclusion]
        # inclusions.remove("CHOICES")
        #
        # inclusion_values = [getattr(Inclusions, attr) for attr in inclusions]

        for field, value in data.items():
            if "inclusion" in field:
                inclusions = [value.strip() for value in value.split(",")]

                try:
                    data[field] = [Inclusion.objects.get(inclusion=inclusion) for inclusion in inclusions]
                except Inclusion.DoesNotExist:
                    pass

        return data

    def __process_csv_content(self, csv_file):
        """
        Do some processing and return data
        :param csv_file:
        :returns:
        """
        data_frame = pd.read_csv(csv_file)
        data_frame = data_frame.rename(str.strip, axis="columns")
        data_frame = data_frame.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        data_frame = pd.DataFrame(data_frame, columns=self.all_fields)
        stone_data = [dict(zip(self.all_fields, data)) for data in data_frame.values]

        for data in stone_data:
            for column in data:
                if pd.isna(data[column]):
                    data[column] = None

        stone_data = [self.__to_db_name(data) for data in stone_data]

        # clean for height and girdle_min_grade
        for data in stone_data:
            try:
                if "height" in data:
                    data["height"] = round(float(data["height"]), 2)
            except ValueError:
                pass

            girdle_grades = [grade for grade in data if "girdle_min_grade" in grade or "girdle_max_grade" in grade]

            for girdle_grade in girdle_grades:
                data[girdle_grade] = (
                    data[girdle_grade].upper() if type(data[girdle_grade]) == str else data[girdle_grade]
                )

        # Remarks
        for data in stone_data:
            for field in data:
                if "remarks" in field:
                    data[field] = "" if data[field] is None else data[field]

        self.__stone_data = stone_data

        return stone_data

    def __get_all_data_processing_methods(self):
        """
        Returns all csv data processing methods.
        :returns:
        """
        return self.processing_methods

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
            row = f"<tr><td>{int(_) + 1}</td>"
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

    def clean(self):
        """
        Clean the csv file and check for any errors
        :returns:
        """
        cleaned_data = super().clean()
        csv_file = cleaned_data["file"]
        stone_data = self.__process_csv_content(csv_file)
        csv_processing_methods = self.__get_all_data_processing_methods()

        method_errors = {}

        for method in csv_processing_methods:
            stone_data, errors = method(self, stone_data, file_name=csv_file.name)
            method_errors.update(errors)

        # Do error handling here and return error_dict
        form_errors = self.__build_error_dict(stone_data)

        for row, error_dict in method_errors.items():
            for field, error in error_dict.items():
                if field in form_errors[row]:
                    form_errors[row][field].clear()
                    form_errors[row][field].append(error)

        if form_errors:
            self.__csv_errors = form_errors
            raise ValidationError({"file": "CSV File Validation Error"})

        self.__csv_errors = {}

        return stone_data


class SarineUploadForm(BaseUploadForm):
    class Meta:
        mixin = SarineGradingMixin
        fields = [field.name for field in SarineGradingMixin._meta.get_fields()]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def __process_file_name(self, stone_data, file_name):
        """
        Raise a validation error if file name does not match any gradia parcel code
        :param stone_data:
        :param file_name:
        :returns:
        """
        gradia_parcel_code = os.path.splitext(file_name)[0]
        try:
            self.parcel = Parcel.objects.get(gradia_parcel_code=gradia_parcel_code)
        except Parcel.DoesNotExist:
            raise ValidationError(
                {
                    "file": "No parcel with such a parcel code. Please be sure the csv file name matches the parcel code"
                }
            )

        return stone_data, {}

    def save(self):
        """
        Create and return a list of stones
        :return:
        """
        stones = []

        split = Split.objects.create(original_parcel=self.parcel, split_by=self.user)

        for stone_data in self.cleaned_data:

            stone_data["data_entry_user"] = self.user
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


class BasicUploadForm(BaseUploadForm):
    class Meta:
        mixin = BasicGradingMixin
        fields = [field.name for field in BasicGradingMixin._meta.get_fields()]

        # Extra fields which are not fields in the mixin (BasicGradingMixin)
        girdle_min_grade = forms.ChoiceField(choices=GirdleGrades.CHOICES)
        # basic_remarks = forms.CharField()

    def __process_graders(self, stone_data, file_name):
        """
        Check that graders (user accounts) exists and raise validation error or return stone_data

        Conditions
        ----------
        1. basic_grading_1, basic_grading_2, basic_grading_3 ===> Not required
        2. Raise error instantly when any of them contains a user that does not exist
        :param stone_data:
        :param file_name:
        :return:
        """

        errors = {}

        for row, data in enumerate(stone_data):
            for field, value in data.items():
                if "basic_grader_" in field:
                    try:
                        data[field] = User.objects.get(username=value.lower())
                    except User.DoesNotExist:
                        errors[row] = {}
                        errors[row][field] = f"Grader user `{value}` account does not exist"

        return stone_data, errors

    def save(self):
        stones = []
        for data in self.cleaned_data:
            stone = Stone.objects.get(internal_id=data["internal_id"])  # After resolving the id stuff

            inclusions_fields = (
                "basic_inclusions_1",
                "basic_inclusions_2",
                "basic_inclusions_3",
                "basic_inclusions_final",
            )

            savable_data = data.copy()

            for field in inclusions_fields:
                inclusions = data[field]
                stone_inclusions = getattr(stone, field)

                for inclusion in inclusions:
                    stone_inclusions.add(inclusion)

                del savable_data[field]

            for field, value in savable_data.items():
                setattr(stone, field, value)

            stone.save()
            stones.append(stone)

        return stones

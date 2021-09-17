import os
from datetime import datetime
from six import with_metaclass

import pandas as pd
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.timezone import utc

from stonegrading.mixins import SarineGradingMixin, BasicGradingMixin
from stonegrading.models import Inclusion
from stonegrading.grades import Inclusions

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
        if not hasattr(self.Meta, "fields"):
            raise ValueError("You need to specify `fields` attribute in the Meta class")

        self.mixin_fields = self.Meta.fields

        if not hasattr(self.Meta, "mixin"):
            raise ValueError("You need to specify `mixin` attribute in the Meta class")

        self.mixin = self.Meta.mixin

        stone_data_class = self.__get_data_class(self.mixin_fields, self.mixin)
        setattr(self, "StoneDataForm", stone_data_class)

    def __get_data_class(self, _fields, mixin):
        """
        Creates and returns StoneDataForm form modelling
        :return:
        """

        class StoneDataForm(type(forms.ModelForm), metaclass=ModelFormDataMetaClass):
            class Meta:
                fields = _fields
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
        grade_fields = [field for field in self.mixin_fields if "grade" in field] + [
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
                    data[field] = choices_display_name_map.get(data[field].upper()) or data[field]
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
                data[field] = data[field].upper()

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
        """
        data_frame = pd.read_csv(csv_file)
        data_frame = data_frame.rename(str.strip, axis="columns")
        data_frame = pd.DataFrame(data_frame, columns=self.mixin_fields)
        stone_data = [dict(zip(self.mixin_fields, data)) for data in data_frame.values]

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

        self.__stone_data = stone_data

        return stone_data

    def __get_all_data_processing_methods(self):
        """
        Returns all csv data processing methods.
        """
        return self.processing_methods

    def clean(self):
        """
        Clean the csv file and check for any errors
        """
        cleaned_data = super().clean()
        csv_file = cleaned_data["file"]
        stone_data = self.__process_csv_content(csv_file)
        csv_processing_methods = self.__get_all_data_processing_methods()

        for method in csv_processing_methods:
            stone_data = method(self, stone_data, file_name=csv_file.name)

        import pdb

        pdb.set_trace()

        # Do error handling here and return error_dict
        form_errors = self.__build_error_dict(stone_data)
        import pdb

        pdb.set_trace()
        if form_errors:
            self.__csv_errors = form_errors
            raise ValidationError({"file": "CSV File Validation Error"})

        import pdb

        pdb.set_trace()
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

        return stone_data

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
        fields = [field.name for field in BasicGradingMixin._meta.get_fields()]  #  + ["girdle_min_grade"]

    def __process_graders(self, stone_data, file_name):
        """
        Check that graders (user accounts) exists and raise validation error or return stone_data

        Conditions
        ----------
        1. basic_grading_1, basic_grading_2, basic_grading_3 ===> Not required
        2. Raise error instantly when any of them contains a user that does not exist
        :return:
        """

        graders = []
        for data in stone_data:
            for field, value in data.items():
                if "basic_grader_" in field:
                    # import pdb; pdb.set_trace()
                    try:
                        user = User.objects.get(username=value.lower())
                    except User.DoesNotExist:
                        raise forms.ValidationError("Grader user account does not exist")

                    data[field] = user

        # import pdb; pdb.set_trace()
        return stone_data

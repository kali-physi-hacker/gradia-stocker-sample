from datetime import datetime

from django import forms
from django.utils.timezone import utc
from django.contrib.auth import get_user_model

from grading.models import Stone
from grading.forms import get_error_headers

from .models import StoneTransfer

import pandas as pd


User = get_user_model()


class CSVImportForm(forms.Form):
    file = forms.FileField()


def get_list_of_stones(file):
    data_frame = pd.read_csv(file)
    data_frame = data_frame.rename(str.strip, axis="columns")
    data_frame = data_frame.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    data = tuple(data_frame.internal_id)
    return data


class BaseTransferUploadForm(forms.Form):
    file = forms.FileField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(BaseTransferUploadForm, self).__init__(*args, **kwargs)

    __csv_errors = None

    @property
    def csv_errors(self):
        """
        Return the errors of the csv content, similar to forms.errors
        :return:
        """
        if self.__csv_errors is None:
            raise ValueError("You need to call form.is_valid() first")

        return self.__csv_errors

    def clean(self):
        file = self.cleaned_data["file"]

        data = get_list_of_stones(file)  # [G00001, G00002, G00003]

        """
        Check if stones exist
        """
        error_dict = {}

        for row, stone_id in enumerate(data):
            try:
                Stone.objects.get(internal_id=stone_id)
            except Stone.DoesNotExist:
                error_dict[row] = {}
                error_dict[row]["internal_id"] = [f"Stone With ID `{stone_id}` does not exist"]

        if error_dict:
            self.__csv_errors = error_dict
            raise forms.ValidationError({"file": "The CSV file content is invalid"})

        self.error_dict = {}

        return data

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

    def transfer_to(self, to_user, stone_id):
        item = Stone.objects.get(internal_id=stone_id)
        created_by = self.user
        confirmed_date = (datetime.utcnow().replace(tzinfo=utc),)
        from_user = item.stonetransfer_set.last().to_user

        transfer = StoneTransfer.objects.create(
            item=item,
            created_by=created_by,
            from_user=from_user,
            to_user=to_user,
            confirmed_date=datetime.now(),
            fresh=False,
        )

        return transfer


class GWStoneTransferForm(BaseTransferUploadForm):
    def save(self):
        stone_ids = self.cleaned_data

        transfers = []

        for stone_id in stone_ids:
            goldway_user = User.objects.get(username="goldway")
            transfer = self.transfer_to(to_user=goldway_user, stone_id=stone_id)
            transfers.append(transfer)

        return transfers

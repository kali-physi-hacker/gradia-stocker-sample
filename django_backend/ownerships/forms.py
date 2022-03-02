import os
from datetime import datetime

from django import forms
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.utils import IntegrityError
from django.utils.timezone import utc
from django.contrib.auth import get_user_model
from django.http import HttpResponse

from grading.models import GoldwayVerification, Stone
from grading.forms import get_error_headers
from grading.views import errors_page

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
    file = forms.FileField(required=False)

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

        # Get name of file
        file_name = os.path.splitext(file.name)[0]

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

        self.__csv_errors = {}

        # Get customer id for external transfer
        customer = self.cleaned_data.get("customer")

        if customer is not None:
            return data, customer, file_name

        return data, file_name

    def errors_as_table(self):
        """
        Return html table of the errors
        :return:
        """
        # if not self.is_valid():

        #     return f"<a style='color: red'>{self.errors.get('__all__')}</a>"

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

    def transfer_to(self, stone_id, to_user, from_user=None):
        item = Stone.objects.get(internal_id=stone_id)
        created_by = self.user
        confirmed_date = (datetime.utcnow().replace(tzinfo=utc),)

        if from_user is None:
            from_user = StoneTransfer.most_recent_transfer(item=item).to_user

        transfer = StoneTransfer.initiate_transfer(
            item=item, from_user=from_user, to_user=to_user, created_by=created_by
        )

        # TODO: Remove Confirm stone received temporal
        StoneTransfer.confirm_received(item=item)

        return transfer


class GWStoneTransferForm(BaseTransferUploadForm):
    def clean(self):
        """
        Raises validation error if invoice number already been used
        :returns:
        """

        stone_id, invoice_number = super().clean()

        try:
            GoldwayVerification.objects.get(invoice_number=invoice_number)
            raise forms.ValidationError(
                {"file": f"Stones with this {invoice_number} invoice number has already been transferred to goldway"}
            )
        except GoldwayVerification.DoesNotExist:
            pass

        return stone_id, invoice_number

    def save(self):
        stone_ids, invoice_number = self.cleaned_data

        goldway_verification = GoldwayVerification.objects.create(invoice_number=invoice_number)

        transfers = []

        for stone_id in stone_ids:
            goldway_user = User.objects.get(username="goldway")
            transfer = self.transfer_to(to_user=goldway_user, stone_id=stone_id)
            transfers.append(transfer)

            # Create the GoldwayVerification instance and assign to stone
            stone = Stone.objects.get(internal_id=stone_id)
            # import pdb; pdb.set_trace()
            stone.gw_verification = goldway_verification
            stone.save()

        return transfers


class GiaStoneTransferForm(BaseTransferUploadForm):
    def clean(self):
        """
        Raises validation error if stone does not have goldway_verification
        :returns:
        """
        stone_ids, invoice_number = super().clean()

        for stone_id in stone_ids:
            stone = Stone.objects.get(internal_id=stone_id)
            if stone.gw_verification is None:
                raise forms.ValidationError(
                    {"file": f"Stone doesn't have goldway verification, have you confirmed with goldway"}
                )
        return stone_ids, invoice_number

    def save(self):
        stone_ids, _ = self.cleaned_data
        transfers = []
        for stone_id in stone_ids:
            gia_user = User.objects.get(username="gia")
            transfer = self.transfer_to(to_user=gia_user, stone_id=stone_id)
            transfers.append(transfer)

        return transfers


class ExternalStoneTransferForm(BaseTransferUploadForm):
    customer = forms.CharField()

    def save(self):
        """
        Transfer to customer
        :return:
        """
        transfers = []
        stone_ids, customer_id, _ = self.cleaned_data

        customer = User.objects.get(pk=customer_id)

        for stone_id in stone_ids:
            transfer = self.transfer_to(stone_id=stone_id, to_user=customer)
            transfers.append(transfer)

        return transfers

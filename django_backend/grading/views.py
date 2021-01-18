import os
from datetime import datetime

import pandas as pd

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import utc
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from ownerships.models import ParcelTransfer, StoneTransfer

from .models import Parcel, Receipt, Stone, Split, ParcelTransfer

from .helpers import column_tuple_to_value_tuple_dict_map, get_field_names_snake_case

from .forms import CSVImportForm


class ReturnToVaultView(View):
    def get(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_create_transfer(
                item=parcel, from_user=request.user, to_user=User.objects.get(username="vault")
            )
        except Exception as e:
            return HttpResponse(e)

        return render(
            request, "grading/return_to_vault_confirmation.html", {"username": request.user.username, "item": parcel}
        )

    def post(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_create_transfer(
                item=parcel, from_user=request.user, to_user=User.objects.get(username="vault")
            )
        except Exception as e:
            return HttpResponse(e)
        ParcelTransfer.initiate_transfer(
            item=parcel, from_user=request.user, to_user=User.objects.get(username="vault"), created_by=request.user
        )
        return HttpResponseRedirect(reverse("admin:grading_parcel_change", args=[parcel.id]))


class ConfirmReceivedView(View):
    def get(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)

        try:
            ParcelTransfer.can_confirm_received(parcel, request.user)
        except Exception as e:
            return HttpResponse(e)

        parcel_owner, status = parcel.current_location()

        return render(request, "grading/confirm_received.html", {"username": request.user.username, "item": parcel})

    def post(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_confirm_received(parcel, request.user)
        except Exception as e:
            return HttpResponse(e)

        ParcelTransfer.confirm_received(parcel)
        return HttpResponseRedirect(reverse("admin:grading_parcel_change", args=[parcel.id]))


class CloseReceiptView(View):
    def get(self, request, pk, *args, **kwargs):
        receipt = Receipt.objects.get(pk=pk)
        return render(request, "grading/close_receipt.html", {"username": request.user.username, "receipt": receipt})

    def post(self, request, pk, *args, **kwargs):
        receipt = Receipt.objects.get(pk=pk)
        receipt.release_by = request.user
        receipt.release_date = datetime.utcnow().replace(tzinfo=utc)
        receipt.save()
        return HttpResponseRedirect(reverse("admin:grading_receipt_change", args=[receipt.id]))


# @ConradHo ---> Possible refactor here, to help make error messages better (improving user experience)
def clean_basic_csv_upload_file(file_path):
    """
    Validate the file by checking the column field names if they're valid, validating the content of the
    field values and return a tuple of True and the field values, else return False and None
    :param file_path:
    :return:
    """
    pass


class UploadParcelCSVFile(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        """
        Page to return HTML for upload input field
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = {"form": CSVImportForm()}
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return render(request, "grading/upload.html", context)

    def post(self, request, *args, **kwargs):
        """
        Decouple file and do the splitting
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        csv_file = request.FILES["file"]

        # Get parcel code name from file name
        gradia_parcel_code = os.path.splitext(csv_file.name)[0]

        try:
            parcel = Parcel.objects.get(gradia_parcel_code=gradia_parcel_code)
        except Parcel.DoesNotExist:
            parcel = None

        if parcel is None:
            messages.add_message(request, messages.ERROR, "Parcel name does not exist")
            return HttpResponseRedirect(
                reverse("grading:upload_parcel_csv")
            )  # Return a redirect with an error message

        split = Split.objects.create(original_parcel=parcel, split_by=request.user)

        csv_columns = get_field_names_snake_case(Stone)

        csv_data = pd.read_csv(csv_file)
        data_frame = pd.DataFrame(csv_data, columns=csv_columns)

        # Get parcel owner
        parcel_transfer = ParcelTransfer.most_recent_transfer(parcel)

        if parcel_transfer is None:
            parcel_owner = User.objects.get(username="split")
        else:
            parcel_owner = parcel_transfer.from_user

        # Map column_fields to values in a dictionary data structure
        for stone_entry in data_frame.values:
            data_dict = column_tuple_to_value_tuple_dict_map(csv_columns, stone_entry)
            data_dict["data_entry_user"] = request.user

            # Delete ID
            del data_dict["ID"]

            # Set the split_from value
            data_dict["split_from"] = split
            for data in data_dict:
                if pd.isna(data_dict[data]):
                    data_dict[data] = None

            # Will change this implementation later for a better way of giving error messages
            try:
                data_dict["grader_1"] = User.objects.get(username=data_dict["grader_1"])
            except User.DoesNotExist:
                messages.add_message(request, messages.ERROR, f"Grader: {data_dict['grader_1']} Does not exist")
                return HttpResponseRedirect(reverse("grading:upload_parcel_csv"))

            # Create Stones
            stone = Stone.objects.create(**data_dict)
            stone.split_from = split
            stone.save()

            # Generates basic id hash
            stone.generate_basic_external_id()

            # Do a stone transfer
            StoneTransfer.objects.create(
                item=stone,
                from_user=User.objects.get(username="split"),
                created_by=request.user,
                to_user=parcel_owner,
                confirmed_date=datetime.utcnow().replace(tzinfo=utc),
            )
        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split.pk,)))


"""
class ConfirmTransferToGoldwayView(View):
    def get(self, request, pk, *args, **kwargs):
        stone = Stone.objects.get(pk=pk)
        assert stone.goldway_verification == ""
        return render(request, "grading/confirm_received.html", {"username": request.user.username, "item": parcel})

    def post(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_confirm_received(parcel, request.user)
        except Exception as e:
            return HttpResponse(e)

        ParcelTransfer.confirm_received(parcel)
        return HttpResponseRedirect(reverse("admin:grading_parcel_change", args=[parcel.id]))
"""

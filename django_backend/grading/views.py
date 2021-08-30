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

from .models import Parcel, Receipt, Stone, Split, ParcelTransfer, BasicGradingMixin

from .helpers import column_tuple_to_value_tuple_dict_map, get_model_fields

from stonegrading.models import Inclusion
from stonegrading.mixins import SarineGradingMixin

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


class AllUploadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        template = "grading/all-uploads-to.html"
        context = {}
        return render(request, template, context)


class SarineUploadView(LoginRequiredMixin, View):
    fields = [field.name for field in SarineGradingMixin._meta.get_fields()] + ["internal_id"]

    def get(self, request, *args, **kwargs):
        """
        Page to return the HTML for sarine data upload
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form = CSVImportForm()
        context = {"template_title": "Upload a csv file containing sarine data", "form": form}
        return render(request, "grading/upload.html", context)

    def post(self, request, *args, **kwargs):
        """
        Get csv file content with pandas
        Convert pandas data to dictionary
        loop through diction to create Stone instances while performing other operations such:
        - Ownership transfer stuff,
        - etc
        Split parcel (csv file) into stones by creating stone instances, etc
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
                reverse("grading:sarine_data_upload_url")
            )  # Return a redirect with an error message

        split = Split.objects.create(original_parcel=parcel, split_by=request.user)

        csv_data = pd.read_csv(csv_file)
        data_frame = pd.DataFrame(csv_data, columns=self.fields)

        # Get parcel owner
        parcel_transfer = ParcelTransfer.most_recent_transfer(parcel)

        if parcel_transfer is None:
            parcel_owner = User.objects.get(username="split")
        else:
            parcel_owner = parcel_transfer.from_user

        for stone_entry in data_frame.values:
            data_dict = column_tuple_to_value_tuple_dict_map(self.fields, stone_entry)
            data_dict["data_entry_user"] = request.user

            # Set the split_from value
            data_dict["split_from"] = split
            for data in data_dict:
                if pd.isna(data_dict[data]):
                    data_dict[data] = None

            stone = Stone.objects.create(**data_dict)
            stone.split_from = split
            stone.save()

            # Do a stone transfer
            StoneTransfer.objects.create(
                item=stone,
                from_user=User.objects.get(username="split"),
                created_by=request.user,
                to_user=parcel_owner,
                confirmed_date=datetime.utcnow().replace(tzinfo=utc),
            )

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split.pk,)))


class UploadBasicParcelCSVFile(LoginRequiredMixin, View):
    fields = get_model_fields(BasicGradingMixin)
    fields.append("internal_id")

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

        csv_data = pd.read_csv(csv_file)
        data_frame = pd.DataFrame(csv_data, columns=self.fields)

        # Get parcel owner
        parcel_transfer = ParcelTransfer.most_recent_transfer(parcel)

        if parcel_transfer is None:
            parcel_owner = User.objects.get(username="split")
        else:
            parcel_owner = parcel_transfer.from_user

        # Map column_fields to values in a dictionary data structure
        for stone_entry in data_frame.values:
            data_dict = column_tuple_to_value_tuple_dict_map(self.fields, stone_entry)
            data_dict["data_entry_user"] = request.user

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

            data_dict["grader_2"] = User.objects.filter(username=data_dict["grader_2"]).first()
            data_dict["grader_3"] = User.objects.filter(username=data_dict["grader_3"]).first()

            # Process inclusions here
            inclusion_name_list = data_dict["basic_inclusions"].split(", ")
            inclusions = []
            for inclusion in inclusion_name_list:
                try:
                    inclusion = Inclusion.objects.get(inclusion=inclusion)
                    inclusions.append(inclusion)
                except Inclusion.DoesNotExist:
                    messages.add_message(
                        request, messages.ERROR, f"Inclusion: {data_dict['basic_inclusions']} Does not exist"
                    )
                    return HttpResponseRedirect(reverse("grading:upload_parcel_csv"))

            del data_dict["basic_inclusions"]

            # Create Stones
            stone = Stone.objects.create(**data_dict)
            stone.split_from = split
            for inclusion in inclusions:
                stone.basic_inclusions.add(inclusion.pk)
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

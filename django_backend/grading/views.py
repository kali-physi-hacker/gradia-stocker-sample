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
from .forms import SarineUploadForm

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
        form = SarineUploadForm(user=request.user, data={}, files=request.FILES)
        if not form.is_valid():
            # get the csv errors and return them to some template as context variables and render as error page
            HttpResponseRedirect(reverse("grading:sarine_data_upload_url"))
        stones = form.save()
        split_id = stones[0].split_from.pk

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split_id,)))


class BasicGradingUploadView(LoginRequiredMixin, View):
    fields = [field.name for field in BasicGradingMixin._meta.get_fields()]
    fields.append("internal_id")

    def get(self, request, *args, **kwargs):
        """
        Page to return HTML for upload input field
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        context = {"template_title": "Upload a csv file containing basic grading data"}
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return render(request, "grading/upload.html", context)

    def _process_graders(self, data_dict):
        """
        Return the basic graders or None. Eg. {"basic_grader_1"}
        """
        # Will change this implementation later for a better way of giving error messages
        graders = {"basic_grader_1": None, "basic_grader_2": None, "basic_grader_3": None}

        for grader in graders:
            try:
                graders[grader] = User.objects.get(username=data_dict[grader])
            except User.DoesNotExist:
                pass

        return graders

    # Simple table for displaying the errors == form.errors = {"height": []}

    def _process_inclusions(self, data_dict):
        basic_inclusions = {
            "basic_inclusions_1": None,
            "basic_inclusions_2": None,
            "basic_inclusions_3": None,
            "basic_inclusions_final": None,
        }

        for inclusion in basic_inclusions:
            inclusion_list = data_dict[inclusion].replace(" ", "").split(",")
            inclusion_instances = []
            for inclusion_name in inclusion_list:
                try:
                    inclusion_instances.append(Inclusion.objects.get(inclusion=inclusion_name))
                except Inclusion.DoesNotExist:
                    basic_inclusions[inclusion] = None
                    break
            basic_inclusions[inclusion] = inclusion_instances

        return basic_inclusions

    def post(self, request, *args, **kwargs):
        """
        Decouple file and do the splitting
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        csv_file = request.FILES["file"]

        csv_data = pd.read_csv(csv_file)
        data_frame = pd.DataFrame(csv_data, columns=self.fields)

        # Map column_fields to values in a dictionary data structure
        for stone_entry in data_frame.values:
            data_dict = column_tuple_to_value_tuple_dict_map(self.fields, stone_entry)
            data_dict["data_entry_user"] = request.user

            for data in data_dict:
                if pd.isna(data_dict[data]):
                    data_dict[data] = None

            users = self._process_graders(data_dict)

            if users["basic_grader_1"] is None:
                messages.add_message(request, messages.ERROR, f"User: {data_dict['basic_grader_1']} does not exist")
                return HttpResponseRedirect(reverse("grading:basic_grading_data_upload_url"))

            data_dict.update(users)

            inclusions = self._process_inclusions(data_dict)

            if inclusions["basic_inclusions_1"] is None:
                messages.add_message(
                    request, messages.ERROR, f"Inclusion: {data_dict[inclusion]} does not exist or is empty"
                )
                return HttpResponseRedirect(reverse("grading:basic_grading_data_upload_url"))

            if inclusions["basic_inclusions_final"] is None:
                messages.add_message(
                    request, messages.ERROR, f"Inclusion: {data_dict[inclusion]} does not exist or is empty"
                )
                return HttpResponseRedirect(reverse("grading:basic_grading_data_upload_url"))

            stone = Stone.objects.get(internal_id=data_dict["internal_id"])

            for inclusion in inclusions:
                for single_inclusion_instance in inclusions.get(inclusion):
                    stone_inclusion = getattr(stone, inclusion)
                    stone_inclusion.add(single_inclusion_instance)

            fields_without_inclusions = [field.name for field in BasicGradingMixin._meta.get_fields()]
            fields_without_inclusions.remove("basic_inclusions_1")
            fields_without_inclusions.remove("basic_inclusions_2")
            fields_without_inclusions.remove("basic_inclusions_3")
            fields_without_inclusions.remove("basic_inclusions_final")

            # grab and update stone object
            for field in fields_without_inclusions:
                setattr(stone, field, data_dict[field])
                # exec(f"stone.{field} = data_dict[{field}]")

            # hash and assign gradia ID

            stone.save()

            # Create Stones
            # stone = Stone.objects.create(**data_dict)
            # stone.split_from = split
            # for inclusion in inclusions:
            #     stone.basic_inclusions.add(inclusion.pk)
            # stone.save()

            # # Generates basic id hash
            # stone.generate_basic_external_id()

            # # Do a stone transfer
            # StoneTransfer.objects.create(
            #     item=stone,
            #     from_user=User.objects.get(username="split"),
            #     created_by=request.user,
            #     to_user=parcel_owner,
            #     confirmed_date=datetime.utcnow().replace(tzinfo=utc),
            # )

        return HttpResponseRedirect(reverse("grading:basic_grading_data_upload_url"))


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
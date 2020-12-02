import os
from datetime import datetime

import pandas as pd

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import utc
from django.views import View

from ownerships.models import ParcelTransfer, StoneTransfer

from .models import Parcel, Receipt, Stone, Split, ParcelTransfer

from .helpers import column_tuple_to_value_tuple_dict_map, get_field_names_snake_case


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


class UploadParcelCSVFile(View):
    def get(self, request, *args, **kwargs):
        """
        Page to return HTML for upload input field
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def post(self, request, *args, **kwargs):
        """
        Decouple file and do the splitting
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        csv_file = request.FILES["parcel_csv_file"]

        # TODO: What is happening here ?
        #  1. Get the gradia_parcel_code from the filename
        #  2. Get the existing parcel (original) using the gradia_parcel_code)
        #  2. Do the split if exists else return 404

        # Get parcel code name from file name
        gradia_parcel_code = os.path.splitext(csv_file.name)[0]

        try:
            parcel = Parcel.objects.get(gradia_parcel_code=gradia_parcel_code)
        except Parcel.DoesNotExist:
            parcel = None

        if parcel is None:
            return Http404("Parcel name in the csv does not exist")

        split = Split.objects.get(original_parcel=parcel)

        # TODO: Ways of Implementing the csv_columns
        #  1. By manually entering them
        #  2. By use django's model._meta.fields and passing that to a function that returns
        #       a snake case word

        # TODO: 1 Using the 1st Implementation for 1st Cut
        # csv_columns = (
        #     'gradia_id', 'split_from', 'remarks', 'sample_stone',
        #     'shape_and_cutting', 'diamond_description', 'basic_carat', 'basic_culet',
        #     'basic_fluorescence', 'inclusions', 'grader_1', 'grader_2', 'grader_3',
        #     'basic_color_1', 'basic_color_2', 'basic_color_3', 'basic_final_color',
        #     'basic_clarity_1', 'basic_clarity_2', 'basic_clarity_3', 'basic_final_clarity',
        #     'basic_polish_1', 'basic_polish_2', 'basic_polish_3', 'basic_final_polish',
        #     'diameter_min', 'diameter_max', 'height', 'girdle_min', 'girdle_max', 'girdle_grade',
        #     'culet_size', 'total_depth', 'total_depth_grade', 'sheryl_cut', 'sarine_cut',
        #     'symmetry_grade', 'roundness', 'roundness_grade', 'table_size', 'table_size_grade',
        #     'crown_angle', 'crown_angle_grade', 'pavilion_angle', 'pavilion_angle_grade',
        #     'star_length', 'star_length_grade', 'lower_half', 'lower_half_grade', 'girdle_thick',
        #     'girdle_thick_grade', 'crown_height', 'crown_height_grade', 'pavilion_depth', 'pavilion_depth_angle',
        #     'misalignment', 'misalignment_grade', 'table_edge_var', 'table_edge_var_grade', 'table_off_center',
        #     'table_off_center_grade', 'culet_off_center', 'culet_off_center_grade', 'table_off_culet',
        #     'table_off_culet_grade', 'star_angle', 'star_angle_grade', 'upper_half_angle', 'upper_half_angle_grade',
        #     'lower_half_angle', 'lower_half_angle_grade'
        # )

        # TODO: Going by the second implementation
        csv_columns = get_field_names_snake_case(Stone)

        csv_data = pd.read_csv(csv_file)
        data_frame = pd.DataFrame(csv_data, columns=csv_columns)

        # Get parcel owner
        parcel_owner = ParcelTransfer.most_recent_transfer(parcel).from_user

        # Map column_fields to values in a dictionary data structure
        for stone_entry in data_frame.values:
            data_dict = column_tuple_to_value_tuple_dict_map(csv_columns, stone_entry)
            data_dict['data_entry_user'] = request.user

            # Create Stones
            stone = Stone.objects.create(**data_dict)
            stone.split_from = split
            stone.save()

            # Do a stone transfer
            StoneTransfer.objects.create(
                item=stone,
                from_user=User.objects.get(username="split"),
                created_by=request.user,
                to_user=parcel_owner,
                confirmed_date=datetime.utcnow().replace(tzinfo=utc)
            )


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

from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import utc
from django.views import View

from ownerships.models import ParcelTransfer

from .models import Parcel, Receipt


class ReturnToVaultView(View):
    def get(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_create_transfer(
                item=parcel,
                from_user=request.user,
                to_user=User.objects.get(username="vault"),
            )
        except Exception as e:
            return HttpResponse(e)

        return render(
            request,
            "grading/return_to_vault_confirmation.html",
            {"username": request.user.username, "item": parcel},
        )

    def post(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_create_transfer(
                item=parcel,
                from_user=request.user,
                to_user=User.objects.get(username="vault"),
            )
        except Exception as e:
            return HttpResponse(e)
        ParcelTransfer.initiate_transfer(
            item=parcel,
            from_user=request.user,
            to_user=User.objects.get(username="vault"),
            created_by=request.user,
        )
        return HttpResponseRedirect(
            reverse("admin:grading_parcel_change", args=[parcel.id])
        )


class ConfirmReceivedView(View):
    def get(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)

        try:
            ParcelTransfer.can_confirm_received(parcel, request.user)
        except Exception as e:
            return HttpResponse(e)

        parcel_owner, status = parcel.current_location()

        return render(
            request,
            "grading/confirm_received.html",
            {"username": request.user.username, "item": parcel},
        )

    def post(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_confirm_received(parcel, request.user)
        except Exception as e:
            return HttpResponse(e)

        ParcelTransfer.confirm_received(parcel)
        return HttpResponseRedirect(
            reverse("admin:grading_parcel_change", args=[parcel.id])
        )


class CloseReceiptView(View):
    def get(self, request, pk, *args, **kwargs):
        receipt = Receipt.objects.get(pk=pk)
        return render(
            request,
            "grading/close_receipt.html",
            {"username": request.user.username, "receipt": receipt},
        )

    def post(self, request, pk, *args, **kwargs):
        receipt = Receipt.objects.get(pk=pk)
        receipt.release_by = request.user
        receipt.release_date = datetime.utcnow().replace(tzinfo=utc)
        receipt.save()
        return HttpResponseRedirect(
            reverse("admin:grading_receipt_change", args=[receipt.id])
        )

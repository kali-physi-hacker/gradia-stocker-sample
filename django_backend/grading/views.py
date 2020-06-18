from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from ownerships.models import ParcelTransfer

from .models import Parcel


class ReturnToVaultView(View):
    def get(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_create_transfer(
                item=parcel, from_user=request.user, to_user=User.objects.get(username="vault")
            )
        except Exception as e:
            return HttpResponse(e.message)

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
            return HttpResponse(e.message)
        ParcelTransfer.initiate_transfer(
            item=parcel, from_user=request.user, to_user=User.objects.get(username="vault")
        )
        return HttpResponseRedirect(reverse("admin:grading_parcel_change", args=[parcel.id]))


class ConfirmReceivedView(View):
    def get(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)

        try:
            ParcelTransfer.can_confirm_received(parcel, request.user)
        except Exception as e:
            return HttpResponse(e.message)

        parcel_owner, status = parcel.current_location()

        return render(request, "grading/confirm_received.html", {"username": request.user.username, "item": parcel})

    def post(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        try:
            ParcelTransfer.can_confirm_received(parcel, request.user)
        except Exception as e:
            return HttpResponse(e.message)

        ParcelTransfer.confirm_received(parcel)
        return HttpResponseRedirect(reverse("admin:grading_parcel_change", args=[parcel.id]))

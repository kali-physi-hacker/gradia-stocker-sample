from datetime import datetime
from multiprocessing import context
from re import template

from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.timezone import utc
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import Parcel, Receipt, ParcelTransfer

from .forms import (
    SarineUploadForm,
    BasicUploadForm,
    GWGradingUploadForm,
    GWAdjustingUploadForm,
    GIAUploadForm,
    GIAAdjustingUploadForm,
    MacroImageFilenameUploadForm,
    NanoImageFilenameUploadForm,
)

from stonegrading.mixins import BasicGradingMixin, SarineGradingMixin, GWGradingMixin, GIAGradingMixin

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


class CloseParcelView(View):
    def get(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        return render(request, "grading/close_parcel.html", {"username": request.user.username, "parcel": parcel})

    def post(self, request, pk, *args, **kwargs):
        parcel = Parcel.objects.get(pk=pk)
        parcel.closed = True
        parcel.save()
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


def errors_page(request, title, form, link):
    template = "grading/csv_errors.html"
    context = {"form": form, "title": title, "link": link}
    return render(request, template, context)


class FileNameUploadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        template = "grading/all-filename-uploads.html"
        context = {}
        return render(request, template, context)

    def errors_page(request, title, form):
        template = "grading/csv_errors.html"
        context = {"form": form, "title": title}
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
            return errors_page(request=request, title="Sarine Grading", form=form, link="grading")

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
        form = CSVImportForm()
        context = {"template_title": "Upload a csv file containing basic grading data", "form": form}
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
        form = BasicUploadForm(data={}, user=request.user, files=request.FILES)
        if not form.is_valid():
            return errors_page(request=request, title="Basic Grading", form=form, link="grading")

        stones = form.save()
        split_id = stones[0].split_from.pk

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split_id,)))


class GIAGradingAdjustView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        """
        Return get page from uploading GIAGradingAdjust Results
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form = CSVImportForm()
        context = {"template_title": "Upload a csv file containing basic grading data", "form": form}
        return render(request, "grading/upload.html", context)

    def post(self, request, *args, **kwargs):
        form = GIAAdjustingUploadForm(data={}, files=request.FILES)
        if not form.is_valid():
            return errors_page(request=request, title="GIA Adjusting Grading", form=form, link="grading")

        stones = form.save()
        split_id = stones[0].split_from_id

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split_id,)))


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


class GWGradingAdjustView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        """
        Return get page from uploading GoldwayGradingAdjust Results
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form = CSVImportForm()
        context = {"template_title": "Upload a csv file containing basic goldway data", "form": form}
        return render(request, "grading/upload.html", context)

    def post(self, request, *args, **kwargs):
        form = GWAdjustingUploadForm(data={}, files=request.FILES)
        if not form.is_valid():
            return errors_page(request=request, title="GW Adjusting Grading", form=form, link="grading")

        stones = form.save()
        split_id = stones[0].split_from_id

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split_id,)))


class GWGradingUploadView(LoginRequiredMixin, View):
    fields = [field.name for field in GWGradingMixin._meta.get_fields()]
    fields.append("internal_id")

    def get(self, request, *args, **kwargs):

        form = CSVImportForm()
        context = {"template_title": "Upload a csv file containing gold way grading data", "form": form}
        if "errors" in kwargs:
            context["errors"] = kwargs["errors"]
        return render(request, "grading/upload.html", context)

    def post(self, request, *args, **kwargs):

        form = GWGradingUploadForm(data={}, user=request.user, files=request.FILES)
        if not form.is_valid():
            return errors_page(request=request, title="Goldway Grading", form=form, link="grading")

        stones = form.save()
        split_id = stones[0].split_from.pk

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split_id,)))


class GIAGradingUploadView(LoginRequiredMixin, View):
    fields = [field.name for field in GIAGradingMixin._meta.get_fields()]
    fields.append("internal_id")

    def get(self, request, *args, **kwargs):
        """
        Page to return the HTML for sarine data upload
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form = CSVImportForm()
        context = {"template_title": "Upload a csv file containing gia grading data", "form": form}
        return render(request, "grading/upload.html", context)

    def post(self, request, *args, **kwargs):
        """
        Decouple file and do the splitting
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        form = GIAUploadForm(data={}, user=request.user, files=request.FILES)
        if not form.is_valid():
            return errors_page(request=request, title="GIA Grading", form=form, link="grading")

        stones = form.save()
        split_id = stones[0].split_from.pk

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split_id,)))


class MacroFileNameUpload(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        form = CSVImportForm()
        context = {"template_title": "Upload a csv file containing macro image filename and stone id", "form": form}
        return render(request, "grading/upload.html", context)

    def post(self, request, *args, **kwargs):

        form = MacroImageFilenameUploadForm(data={}, files=request.FILES)

        if not form.is_valid():

            return render(request, "grading/filename_upload_csv_error.html", {"form": form})
        stones = form.save()
        split_id = stones[0].split_from.pk

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split_id,)))


class NanoFileNameUpload(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        form = CSVImportForm()
        context = {"template_title": "Upload a csv file containing nano image filename and stone id", "form": form}
        return render(request, "grading/upload.html", context)

    def post(self, request, *args, **kwargs):

        form = NanoImageFilenameUploadForm(data={}, files=request.FILES)

        if not form.is_valid():
            return render(request, "grading/filename_upload_csv_error.html", {"form": form})
        stones = form.save()

        split_id = stones[0].split_from.pk

        return HttpResponseRedirect(reverse("admin:grading_split_change", args=(split_id,)))

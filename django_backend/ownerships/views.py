from datetime import datetime

from django.db import OperationalError
from django.utils.timezone import utc
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

from .forms import CSVImportForm, GWStoneTransferForm, GiaStoneTransferForm, ExternalStoneTransferForm

from grading.views import errors_page


User = get_user_model()


def confirm_stones_checked(self, request, obj):
    if "_confirm_transfer" in request.POST:
        assert request.user == obj.to_user
        assert obj.confirmed_date is None
        obj.confirmed_date = datetime.utcnow().replace(tzinfo=utc)
        obj.save()
    return super().response_change(request, obj)


class AllUploadView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        template = "transfer/all-uploads-to.html"
        context = {}
        return render(request, template, context)


class TransferView(LoginRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not hasattr(self, "transfer_form"):
            raise ValueError("`transfer_from` required")

        if not hasattr(self, "title"):
            raise ValueError("`title` required")

        self.form = self.transfer_form

        if not hasattr(self, "template_name"):
            self.template_name = "transfer/upload.html"
            self.form = CSVImportForm()

        if not hasattr(self, "context"):
            self.context = {}

    def get(self, request, *args, **kwargs):
        template = self.template_name
        context = {
            "form": self.form,
            "template_title": f"Upload a CSV file containing a list of stone IDs to transfer to {self.title}",
        }
        context.update(self.context)
        return render(request, template, context)

    def post(self, request, *args, **kwargs):
        form = self.transfer_form(user=request.user, data=request.POST, files=request.FILES)
        if not form.is_valid():
            return errors_page(request=request, title=f"{self.title} Stone Transfer", form=form)

        form.save()
        return redirect("/admin/ownerships/stonetransfer/")


class GoldwayTransferView(TransferView):
    transfer_form = GWStoneTransferForm
    title = "Goldway"


class GiaTransferView(TransferView):
    transfer_form = GiaStoneTransferForm
    title = "GIA"


class ExternalTransferView(TransferView):
    template_name = "transfer/external.html"
    transfer_form = ExternalStoneTransferForm
    title = "External"

    not_external = ("vault", "goldway", "gia")  # And some other ones
    try:
        users = [
            user for user in User.objects.all() if user.username not in ("vault", "goldway", "gia", "split", "admin")
        ]
    except OperationalError:
        users = {}
    context = {"users": users}

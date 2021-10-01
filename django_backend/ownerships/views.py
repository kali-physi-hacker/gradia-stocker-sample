from datetime import datetime

from django.utils.timezone import utc
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import CSVImportForm, GWStoneTransferForm

from grading.views import errors_page


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


class GoldwayTransferView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        template = "transfer/upload.html"
        context = {
            "form": CSVImportForm(),
            "template_title": "Upload a CSV file containing a list of stone IDs to transfer to Goldway",
        }
        return render(request, template, context)

    def post(self, request, *args, **kwargs):
        form = GWStoneTransferForm(user=request.user, data={}, files=request.FILES)
        if not form.is_valid():
            return errors_page(request=request, title="Goldway Stone Transfer", form=form)

        form.save()
        return redirect("/admin/ownerships/stonetransfer/")

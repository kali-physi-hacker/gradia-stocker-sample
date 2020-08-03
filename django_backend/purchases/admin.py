from django import forms
from django.contrib import admin

from grading.admin import ParcelAdmin as GradingParcelAdmin
from grading.admin import ParcelInline as GradingParcelInline
from grading.admin import ReceiptAdmin as GradingReceiptAdmin

from .models import AuthorizedPersonnel, Parcel, Receipt, Seller


def filter_out_gradia_stuff(list_of_strings):
    gradia_stuff = [
        "gradia_parcel_code",
        "finished_basic_grading",
        "current_location",
        "split_from",
        "split_into",
        "most_recent_transfer",
    ]

    return list(filter(lambda f: f not in gradia_stuff, list_of_strings.copy()))


class AuthorizedPersonnelInline(admin.StackedInline):
    model = AuthorizedPersonnel

    extra = 1


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    model = Seller

    inlines = [AuthorizedPersonnelInline]


class ParcelInline(GradingParcelInline):
    model = Parcel
    fields = filter_out_gradia_stuff(GradingParcelInline.fields)


@admin.register(Receipt)
class ReceiptAdmin(GradingReceiptAdmin):
    model = Receipt

    inlines = [ParcelInline]


class ParcelRejectionForm(forms.ModelForm):
    class Meta:
        model = Parcel
        fields = ["rejected_carats", "rejected_pieces", "total_price_paid"]

    def clean(self):
        if self.cleaned_data.get("rejected_carats") is None:
            raise forms.ValidationError("Can't leave rejected carats field blank")
        if self.cleaned_data.get("rejected_pieces") is None:
            raise forms.ValidationError("Can't leave rejected pieces field blank")
        if self.cleaned_data.get("total_price_paid") is None:
            raise forms.ValidationError("Can't leave total prices paid field blank")
        return self.cleaned_data


@admin.register(Parcel)
class ParcelRejectionAdmin(GradingParcelAdmin):
    model = Parcel
    form = ParcelRejectionForm

    readonly_fields = ["customer_parcel_code", "receipt", "total_carats", "total_pieces"]
    fields = filter_out_gradia_stuff(GradingParcelAdmin.readonly_fields) + [
        "rejected_carats",
        "rejected_pieces",
        "total_price_paid",
    ]

    search_fields = filter_out_gradia_stuff(GradingParcelAdmin.search_fields)
    list_filter = []
    list_display_links = []

    def get_list_display(self, request):
        return ["customer_parcel_code", "get_receipt_with_html_link", "total_carats", "total_pieces"]

    def has_change_permission(self, request, obj=None):
        return True

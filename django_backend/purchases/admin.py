from django import forms
from django.contrib import admin

from grading.admin import ParcelAdmin as GradingParcelAdmin
from grading.admin import ParcelInline as GradingParcelInline

from .models import AuthorizedPersonnel, Parcel, Receipt, Seller


class AuthorizedPersonnelInline(admin.StackedInline):
    model = AuthorizedPersonnel

    extra = 1


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    model = Seller

    inlines = [AuthorizedPersonnelInline]


class ParcelInline(GradingParcelInline):
    model = Parcel
    fields = list(filter(lambda f: f != "gradia_parcel_code", GradingParcelInline.fields.copy()))


@admin.register(Receipt)
class CreateReceiptAdmin(admin.ModelAdmin):
    model = Receipt

    readonly_fields = ["intake_by", "intake_date", "release_by", "release_date"]

    inlines = [ParcelInline]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        obj.intake_by = request.user
        obj.save()


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
    fields = GradingParcelAdmin.readonly_fields + ["rejected_carats", "rejected_pieces", "total_price_paid"]

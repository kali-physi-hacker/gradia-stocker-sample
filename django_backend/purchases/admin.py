from datetime import datetime

from django import forms
from django.contrib import admin
from django.http import HttpResponse

from .models import AuthorizedPersonnel, Parcel, Receipt, Seller


class AuthorizedPersonnelInline(admin.StackedInline):
    model = AuthorizedPersonnel

    extra = 1


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    model = Seller

    inlines = [AuthorizedPersonnelInline]


class CreateReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "Step 1. Create receipt for stone intake"


class ParcelInline(admin.TabularInline):
    model = Parcel
    fields = ["code", "total_carats", "total_pieces", "reference_price_per_carat"]

    extra = 1


@admin.register(CreateReceipt)
class CreateReceiptAdmin(admin.ModelAdmin):
    model = CreateReceipt

    readonly_fields = ["intake_by", "intake_date", "release_by", "release_date"]

    inlines = [ParcelInline]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.intake_by = request.user
        obj.save()


class ParcelRejection(Parcel):
    class Meta:
        proxy = True
        verbose_name = "Step 2. View parcel info and record rejection"


class ParcelRejectionForm(forms.ModelForm):
    class Meta:
        model = ParcelRejection
        fields = ["rejected_carats", "rejected_pieces", "total_price_paid"]

    def clean(self):
        if self.cleaned_data.get("rejected_carats") is None:
            raise forms.ValidationError("Can't leave rejected carats field blank")
        if self.cleaned_data.get("rejected_pieces") is None:
            raise forms.ValidationError("Can't leave rejected pieces field blank")
        if self.cleaned_data.get("total_price_paid") is None:
            raise forms.ValidationError("Can't leave total prices paid field blank")
        return self.cleaned_data


@admin.register(ParcelRejection)
class ParcelRejectionAdmin(admin.ModelAdmin):
    model = ParcelRejection
    form = ParcelRejectionForm

    readonly_fields = ["code", "total_carats", "total_pieces", "reference_price_per_carat"]
    fields = readonly_fields + ["rejected_carats", "rejected_pieces", "total_price_paid"]

    search_fields = ["code", "receipt__code", "receipt__entity__name"]
    list_display = ["__str__", "closed_out"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and not obj.closed_out():
            return True
        return False


class CloseOutReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "Step 3. View receipts and close out receipt on stone release"


@admin.register(CloseOutReceipt)
class CloseOutReceiptAdmin(admin.ModelAdmin):
    model = CloseOutReceipt

    list_filter = ["release_date", "intake_date"]
    list_display = ["__str__", "closed_out", "intake_date", "release_date"]
    search_fields = ["code", "entity__name"]

    readonly_fields = ["code", "entity", "intake_by", "intake_date", "release_by", "release_date"]

    change_form_template = "grading/admin_item_change_form_with_button.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["has_close_out_permission"] = self.has_change_permission(
            request, Receipt.objects.get(id=object_id)
        )
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):
        if "_close_out" in request.POST:
            if obj.closed_out():
                return HttpResponse("Error: This receipt has already been closed out")
            for parcel in obj.parcel_set.all():
                if not parcel.closed_out():
                    return HttpResponse(f"Error: Parcel {parcel} has not been closed out yet")
            obj.release_by = request.user
            obj.release_date = datetime.now()
            obj.save()
        return super().response_change(request, obj)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and not obj.closed_out():
            return True
        return False

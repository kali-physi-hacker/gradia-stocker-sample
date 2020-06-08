from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse

from ownerships.models import ParcelTransfer

from .models import Parcel, Receipt


class CreateReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "Step 1. Create receipt for stone intake"


class ParcelInline(admin.TabularInline):
    model = Parcel
    fields = ["name", "code", "total_carats", "total_pieces"]

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

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, Parcel):
                instance.save()
                ParcelTransfer.objects.create(
                    parcel=instance, from_user=request.user, to_user=User.objects.get(username="vault")
                )


class VerboseParcel(Parcel):
    class Meta:
        proxy = True
        verbose_name = "Step 2. View parcel info and return parcels to vault"


class ParcelOwnerFilter(admin.SimpleListFilter):
    title = "current owner"
    parameter_name = "owner"

    def lookups(self, request, model_admin):
        return (("me", "owned by me"), ("vault", "owned by the vault"), ("all", "all"))

    def queryset(self, request, queryset):
        if self.value() == "me":
            parcel = ParcelTransfer.get_current_holding(request.user)
            parcel_id = parcel.id if parcel else -1
            return queryset.filter(id=parcel_id)
        if self.value == "vault":
            parcels = ParcelTransfer.objects.filter(to_user__username="vault")
            parcel_ids = (p.id for p in parcels)
            return queryset.filter(id__in=parcel_ids)
        if self.value == "__all__":
            return queryset


@admin.register(VerboseParcel)
class VerboseParcelAdmin(admin.ModelAdmin):
    model = VerboseParcel

    readonly_fields = ["receipt", "name", "code", "total_carats", "total_pieces", "current_owner"]

    search_fields = ["name", "code", "receipt__code", "receipt__entity__name"]
    list_filter = [ParcelOwnerFilter]
    list_display = ["__str__", "current_owner"]

    change_form_template = "grading/admin_item_change_form_with_button.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        parcel = Parcel.objects.get(id=object_id)
        current_owner, confirmed = parcel.current_owner()
        if request.user == current_owner and confirmed:
            extra_context["can_return_to_vault"] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):
        if "_return_to_vault" in request.POST:
            try:
                ParcelTransfer.initiate_transfer(
                    obj, from_user=request.user, to_user=User.objects.get(username="vault")
                )
            except Exception as e:
                return HttpResponse(f"Error: {e}")
        return super().response_change(request, obj)

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj:
            current_owner, confirmed = obj.current_owner()
            if request.user == current_owner and confirmed:
                return True
        return True


class CloseOutReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "Step 3. View receipts and close out receipt on stone release"


@admin.register(CloseOutReceipt)
class CloseOutReceiptAdmin(admin.ModelAdmin):
    model = CloseOutReceipt

    list_filter = ["release_date", "intake_date"]

    search_fields = ["code", "entity__name"]

    readonly_fields = ["code", "entity", "intake_by", "intake_date", "release_by", "release_date"]

    list_display = ["__str__", "closed_out", "intake_date", "release_date"]
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

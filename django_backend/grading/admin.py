from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.http import HttpResponse

from ownerships.models import ParcelTransfer

from .models import Parcel, Receipt, SplitParcel, Stone


class CreateReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "Step 1. Create receipt for stone intake"


class ParcelInline(admin.TabularInline):
    model = Parcel
    fields = ["code", "total_carats", "total_pieces"]

    extra = 1

    def has_delete_permission(self, request, obj=None):
        return False


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
                    item=instance, from_user=request.user, to_user=User.objects.get(username="vault")
                )


class SplitParcelInline(admin.TabularInline):
    model = SplitParcel

    fields = ["total_carats", "total_pieces", "split_by", "split_date", "current_owner"]
    readonly_fields = fields

    extra = 0

    def has_add_permission(self, request, parenthing):
        return False

    def has_delete_permission(self, request, object):
        return False


class VerboseParcel(Parcel):
    class Meta:
        proxy = True
        verbose_name = "Step 2. View parcels, confirm received parcels, return parcels to vault"


class ParcelOwnerFilter(admin.SimpleListFilter):
    title = "current owner"
    parameter_name = "owner"
    default_value = "me"

    def lookups(self, request, model_admin):
        return (("me", "Owned by me"), ("vault", "Owned by the vault"), ("all", "All"))

    def choices(self, changelist):
        # override choices so that we don't have initial 'All'
        value = self.value() or self.default_value
        for lookup, title in self.lookup_choices:
            yield {
                "selected": value == str(lookup),
                "query_string": changelist.get_query_string({self.parameter_name: lookup}),
                "display": title,
            }

    def queryset(self, request, queryset):
        if self.value() is None or self.value() == "me":
            parcel = ParcelTransfer.get_current_holding(request.user)
            parcel_id = parcel.id if parcel else -1
            return queryset.filter(id=parcel_id)
        if self.value == "vault":
            parcels = ParcelTransfer.objects.filter(to_user__username="vault", expired=False)
            parcel_ids = (p.id for p in parcels)
            return queryset.filter(id__in=parcel_ids)
        if self.value == "__all__":
            return queryset


def confirm_parcel_or_return_to_vault(parcel):
    return "Go to Actions"


confirm_parcel_or_return_to_vault.allow_tags = True


@admin.register(VerboseParcel)
class VerboseParcelAdmin(admin.ModelAdmin):
    model = VerboseParcel
    inlines = [SplitParcelInline]

    readonly_fields = ["receipt", "code", "total_carats", "total_pieces", "current_owner"]

    search_fields = ["code", "receipt__code", "receipt__entity__name"]
    list_filter = [ParcelOwnerFilter]
    list_display = [
        "code",
        "receipt",
        "total_carats",
        "total_pieces",
        "current_owner",
        confirm_parcel_or_return_to_vault,
    ]
    list_display_links = [confirm_parcel_or_return_to_vault]

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


class ReadOnlyParcelInline(admin.TabularInline):
    model = Parcel
    readonly_fields = ["code", "total_carats", "total_pieces"]
    fields = ["code", "total_carats", "total_pieces"]

    extra = 0

    def has_add_permission(self, request, parent):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CloseOutReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "Step 3. View receipts, close out receipt on stone release"


@admin.register(CloseOutReceipt)
class CloseOutReceiptAdmin(admin.ModelAdmin):
    model = CloseOutReceipt

    list_filter = ["release_date", "intake_date"]

    search_fields = ["code", "entity__name"]

    readonly_fields = ["code", "entity", "intake_by", "intake_date", "release_by", "release_date"]

    list_display = ["__str__", "closed_out", "intake_date", "release_date"]
    change_form_template = "grading/admin_item_change_form_with_button.html"

    inlines = [ReadOnlyParcelInline]

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


@admin.register(SplitParcel)
class SplitParcelAdmin(admin.ModelAdmin):
    model = SplitParcel

    readonly_fields = ["split_by", "split_date"]
    fields = ["parcel", "split_parcel_code", "total_carats", "total_pieces"] + readonly_fields

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return True

    def save_model(self, request, obj, form, change):
        obj.split_by = request.user
        obj.save()


@admin.register(Stone)
class StoneAdmin(admin.ModelAdmin):
    model = Stone

    readonly_fields = ["data_entry_user", "stone_id"]
    fields = readonly_fields + [
        "grader_1",
        "grader_2",
        "grader_3",
        "sequence_number",
        "carats",
        "color",
        "grader_1_color",
        "grader_2_color",
        "grader_3_color",
        "clarity",
        "grader_1_clarity",
        "grader_2_clarity",
        "grader_3_clarity",
        "fluo",
        "culet",
        "inclusion_remarks",
        "grader_1_inclusion",
        "grader_2_inclusion",
        "grader_3_inclusion",
        "rejection_remarks",
    ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def save_model(self, request, obj, form, change):
        obj.data_entry_user = request.user
        obj.stone_id = "G124081208"
        obj.save()

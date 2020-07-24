from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import utc

from ownerships.models import VAULT_USERNAMES, ParcelTransfer, StoneTransfer

from .forms import StoneForm
from .models import Parcel, Receipt, Split, Stone


class StoneInline(admin.TabularInline):
    model = Stone

    readonly_fields = ["data_entry_user"]
    form = StoneForm

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    extra = 0
    max_number = 50


class ParcelInline(admin.TabularInline):
    model = Parcel

    fields = [
        "get_parcel_with_html_link",
        "gradia_parcel_code",
        "customer_parcel_code",
        "total_carats",
        "total_pieces",
        "reference_price_per_carat",
    ]
    readonly_fields = ["get_parcel_with_html_link"]

    extra = 0
    max_number = 10

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Split)
class SplitAdmin(admin.ModelAdmin):
    model = Split
    inlines = [ParcelInline, StoneInline]

    readonly_fields = ["split_by"]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        parcel = Parcel.objects.get(pk=request.POST["original_parcel"])
        # original parcel has already been sent to split
        parcel_owner = ParcelTransfer.most_recent_transfer(parcel).from_user
        split = Split.objects.get(original_parcel=parcel)
        for instance in instances:
            if isinstance(instance, Parcel):
                instance.receipt = parcel.receipt
                instance.split_from = split
                instance.save()
                ParcelTransfer.objects.create(
                    item=instance,
                    from_user=User.objects.get(username="split"),
                    to_user=parcel_owner,
                    confirmed_date=datetime.utcnow().replace(tzinfo=utc),
                )
            if isinstance(instance, Stone):
                instance.split_from = split
                instance.data_entry_user = request.user
                instance.save()
                StoneTransfer.objects.create(
                    item=instance,
                    from_user=User.objects.get(username="split"),
                    to_user=parcel_owner,
                    confirmed_date=datetime.utcnow().replace(tzinfo=utc),
                )

    def save_model(self, request, obj, form, change):
        obj.split_by = request.user
        obj.save()
        current_holder = obj.original_parcel.current_location()[0]
        ParcelTransfer.initiate_transfer(
            obj.original_parcel, from_user=current_holder, to_user=User.objects.get(username="split")
        )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ParcelOwnerFilter(admin.SimpleListFilter):
    title = "current owner"
    parameter_name = "owner"
    default_value = "me"

    def lookups(self, request, model_admin):
        return (("me", "With me"), ("vault", "With the vault"), ("goldway", "With Goldway"))

    def queryset(self, request, queryset):
        username_filter = self.value()
        if self.value() == "me":
            username_filter = request.user.username

        if username_filter:
            fresh_transfers = ParcelTransfer.objects.filter(to_user__username=username_filter, fresh=True)
            parcel_ids = (p.item.id for p in fresh_transfers)
            return queryset.filter(id__in=parcel_ids)

        ## self.value() == "__all__" or None
        return queryset


def make_parcel_actions(user):
    def actions(parcel):
        transfer = ParcelTransfer.most_recent_transfer(parcel)
        if transfer.fresh:
            if transfer.to_user == user:
                if transfer.in_transit():
                    return format_html(
                        f"<a href='{reverse('grading:confirm_received', args=[parcel.id])}'>Confirm Received</a>"
                    )
                else:
                    return format_html(
                        f"<a href='{reverse('grading:return_to_vault', args=[parcel.id])}'>Return to Vault</a>"
                    )
            if transfer.in_transit() and transfer.to_user.username == "vault" and user.username in VAULT_USERNAMES:
                return format_html(
                    f"<a href='{reverse('grading:confirm_received', args=[parcel.id])}'>Confirm Stones for Vault</a>"
                )
        return "-"

    return actions


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    model = Parcel

    readonly_fields = [
        "split_from",
        "gradia_parcel_code",
        "customer_parcel_code",
        "receipt",
        "total_carats",
        "total_pieces",
        "current_location",
        "most_recent_transfer",
    ]

    search_fields = ["gradia_parcel_code", "customer_parcel_code", "receipt__code", "receipt__entity__name"]
    list_filter = [ParcelOwnerFilter]
    list_display_links = ["gradia_parcel_code"]

    def get_list_display(self, request):
        return [
            "gradia_parcel_code",
            "customer_parcel_code",
            "get_receipt_with_html_link",
            "total_carats",
            "total_pieces",
            "finished_basic_grading",
            "current_location",
            make_parcel_actions(request.user),
        ]

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    model = Receipt

    list_filter = ["release_date", "intake_date"]

    search_fields = ["code", "entity__name"]

    readonly_fields = ["intake_by", "intake_date", "release_by", "release_date"]
    # readonly_fields = ["code", "entity", "intake_by", "intake_date", "release_by", "release_date"]

    inlines = [ParcelInline]

    def get_list_display(self, request):
        return ["__str__", "intake_date", "release_date", "closed_out", self.model.get_action_html_link]

    def has_add_permission(self, request, obj=None):
        return True

    def has_view_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.intake_by = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
            if isinstance(instance, Parcel):
                ParcelTransfer.objects.create(
                    item=instance, from_user=request.user, to_user=User.objects.get(username="vault")
                )


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

    def get_list_display(self, request):
        return [
            "stone_id",
            "current_location",
            "carats",
            "color",
            "clarity",
            "fluo",
            "culet",
            # make_parcel_actions(request.user),
        ]

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        obj.data_entry_user = request.user
        obj.stone_id = "G124081208"
        obj.save()

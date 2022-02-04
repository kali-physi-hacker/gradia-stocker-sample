from datetime import datetime
from os import read
import pandas as pd

from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.utils.timezone import utc
from django.http import HttpResponse
from django.shortcuts import redirect
from django.forms.models import BaseInlineFormSet
from django.forms import ValidationError

from ownerships.models import ParcelTransfer, StoneTransfer

from .forms import StoneForm
from .models import GiaVerification, GoldwayVerification, Parcel, Receipt, Split, Stone


class StoneInline(admin.TabularInline):
    model = Stone

    readonly_fields = ["data_entry_user"]
    form = StoneForm

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    extra = 0
    max_num = 50


class ParcelInlineFormset(BaseInlineFormSet):
    def clean(self):
        super(ParcelInlineFormset, self).clean()
        if len(self.forms) < 1:
            raise ValidationError("Requires at least one parcel")


class ParcelInline(admin.TabularInline):
    model = Parcel
    formset = ParcelInlineFormset

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
    max_num = 10

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Split)
class SplitAdmin(admin.ModelAdmin):
    model = Split
    inlines = [ParcelInline, StoneInline]

    readonly_fields = ["split_by"]

    change_list_template = "grading/split_change_list.html"

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
                    created_by=request.user,
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
                    created_by=request.user,
                    to_user=parcel_owner,
                    confirmed_date=datetime.utcnow().replace(tzinfo=utc),
                )

    def save_model(self, request, obj, form, change):
        obj.split_by = request.user
        obj.save()
        current_holder = obj.original_parcel.current_location()[0]
        ParcelTransfer.initiate_transfer(
            obj.original_parcel,
            from_user=current_holder,
            to_user=User.objects.get(username="split"),
            created_by=request.user,
        )

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class ItemOwnerFilter(admin.SimpleListFilter):
    title = "current owner"
    parameter_name = "owner"
    default_value = "me"
    transfer_model = None

    def lookups(self, request, model_admin):
        return (
            ("me", "With me"),
            ("vault", "With the vault"),
            ("goldway", "With Goldway"),
            ("gia", "With GIA"),
            ("include", "Including splits and exited"),
            ("customer_receipt_number", "Customer Receipt Number"),
        )

    def queryset(self, request, queryset):
        username_filter = self.value()

        if username_filter == "include":
            return queryset

        if username_filter == "me":
            username_filter = request.user.username

        if username_filter:
            fresh_transfers = self.transfer_model.objects.filter(to_user__username=username_filter, fresh=True)
        else:
            # the __all__ case where self.value() == None
            fresh_transfers = (
                self.transfer_model.objects.filter(fresh=True)
                .exclude(to_user__username="split")
                .exclude(to_user__username="exit")
            )
        parcel_ids = (p.item.id for p in fresh_transfers)
        return queryset.filter(id__in=parcel_ids)


class ParcelOwnerFilter(ItemOwnerFilter):
    transfer_model = ParcelTransfer


class StoneOwnerFilter(ItemOwnerFilter):
    transfer_model = StoneTransfer


def make_parcel_actions(user):
    def actions(parcel):
        return parcel.get_action_html_link_for_user(user)

    return actions


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    model = Parcel

    readonly_fields = [
        "split_from",
        "split_into",
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
            "split_from",
            "split_into",
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
                    item=instance,
                    from_user=request.user,
                    to_user=User.objects.get(username="vault"),
                    created_by=request.user,
                )


def parcel(stone):
    return stone.split_from.original_parcel.get_parcel_with_html_link()


@admin.register(Stone)
class StoneAdmin(admin.ModelAdmin):
    model = Stone

    list_filter = [StoneOwnerFilter]

    search_fields = ["split_from__original_parcel__receipt__code"]

    change_list_template = "grading/stone_data_upload.html"

    def get_list_display(self, request):
        return [
            "external_id",
            "customer_receipt_number",
            "current_location",
            "basic_carat",
            "basic_color_final",
            "basic_clarity_final",
            "basic_fluorescence_final",
            "basic_culet_final",
            "split_from",
        ]

    actions = [
        "transfer_to_goldway",
        "transfer_to_GIA",
        "transfer_to_vault",
        "confirm_received_stones",
        "download_external_ids",
        "download_basic_grading_template",  # generate id and girdle_min_grade
        "download_goldway_grading_template",
        "download_gia_grading_template",
        "download_adjust_goldway_csv",
        "download_master_reports",
        "download_to_GIA_csv",
        "download_adjust_GIA_csv",
        "download_to_basic_report_csv",
        "download_export_triple_report_to_lab",
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.groups.filter(name="vault_manager").exists():
            del actions["transfer_to_goldway"]
            del actions["transfer_to_GIA"]
        return actions

    def download_external_ids(self, request, queryset):
        file_path = Stone.objects.generate_external_id_csv(queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_external_ids.short_description = "Download External IDs"

    def download_basic_grading_template(self, request, queryset):
        file_path = Stone.objects.generate_basic_grading_template(request, queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_basic_grading_template.short_description = "Download Basic Grading CSV Template"

    def download_goldway_grading_template(self, request, queryset):
        file_path = Stone.objects.generate_goldway_grading_template(request, queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_goldway_grading_template.short_description = "Download Goldway Grading CSV Template"

    def download_gia_grading_template(self, request, queryset):
        file_path = Stone.objects.generate_gia_grading_template(request, queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_gia_grading_template.short_description = "Download GIA Grading CSV Template"

    def download_adjust_goldway_csv(self, request, queryset):
        file_path = Stone.objects.generate_adjust_goldway_csv(queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_adjust_goldway_csv.short_description = "Download Adjust Goldway CSV"

    def download_to_GIA_csv(self, request, queryset):
        file_path = Stone.objects.generate_to_GIA_csv(queryset)
        read_file = pd.read_csv(file_path)
        data_frame = pd.DataFrame(read_file)
        field = data_frame["nano_etch_inscription"].to_dict()[0]
        if pd.isna(field):
            messages.warning(request, "There is not enough data to download")
            return redirect(request.path)

        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_to_GIA_csv.short_description = "Download GIA CSV Transfer"

    def download_adjust_GIA_csv(self, request, queryset):
        file_path = Stone.objects.generate_adjust_GIA_csv(queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_adjust_GIA_csv.short_description = "Download Adjust GIA CSV"

    def download_to_basic_report_csv(self, request, queryset):
        file_path = Stone.objects.generate_basic_report_csv(queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_to_basic_report_csv.short_description = "Download Basic Report"

    def download_export_triple_report_to_lab(self, request, queryset):
        """
        Generates csv file representing stone data used as triple report in lab
        :param request:
        :param queryset:
        :return:
        """
        file_path = Stone.objects.generate_triple_report_csv(queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_export_triple_report_to_lab.short_description = "Download Triple Report"

    def download_master_reports(self, request, queryset):
        file_path = Stone.objects.generate_master_report_csv(queryset)
        with open(file_path, mode="r") as file:
            response = HttpResponse(file, content_type="text/csv")
            response["Content-Disposition"] = "attachment; filename=%s" % file_path
            return response

    download_master_reports.short_description = "Download Master Report"

    def transfer_to_goldway(self, request, queryset):
        vault = User.objects.get(username="vault")
        goldway = User.objects.get(username="goldway")

        for stone in queryset.all():
            StoneTransfer.can_create_transfer(item=stone, from_user=vault, to_user=goldway)

        verification = GoldwayVerification.objects.create()
        for stone in queryset.all():
            StoneTransfer.initiate_transfer(item=stone, from_user=vault, to_user=goldway, created_by=request.user)
            stone.goldway_verification = verification
            stone.save()

    transfer_to_goldway.short_description = "Transfer to Goldway"

    def transfer_to_GIA(self, request, queryset):
        vault = User.objects.get(username="vault")
        gia = User.objects.get(username="gia")

        for stone in queryset.all():
            StoneTransfer.can_create_transfer(item=stone, from_user=vault, to_user=gia)

        verification = GiaVerification.objects.create()
        for stone in queryset.all():
            StoneTransfer.initiate_transfer(item=stone, from_user=vault, to_user=gia, created_by=request.user)
            stone.gia_verification = verification
            stone.save()

    transfer_to_GIA.short_description = "Transfer to GIA"

    def transfer_to_vault(self, request, queryset):
        for stone in queryset.all():
            StoneTransfer.initiate_transfer(
                item=stone,
                from_user=User.objects.get(username=request.user.username),
                to_user=User.objects.get(username="vault"),
                created_by=request.user,
            )

    transfer_to_vault.short_description = "Transfer to Vault"

    def confirm_received_stones(self, request, queryset):
        for stone in queryset.all():
            StoneTransfer.confirm_received(item=stone)

    confirm_received_stones.short_description = "Confirm Received Stones"

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


@admin.register(GoldwayVerification)
class GoldwayVerificationAdmin(admin.ModelAdmin):
    model = GoldwayVerification

    list_display = ["gw_code", "purchase_order", "invoice_number", "started", "summary"]

    def gw_code(self, instance):
        return instance.code


@admin.register(GiaVerification)
class GiaVerificationAdmin(admin.ModelAdmin):
    model = GiaVerification
    list_display = ["receipt_number", "invoice_number", "started", "summary"]

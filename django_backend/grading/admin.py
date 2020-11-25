from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.timezone import utc

from ownerships.models import ParcelTransfer, StoneTransfer

from .forms import StoneForm
from .models import GiaVerification, GoldwayVerification, Parcel, Receipt, Split, Stone


class StoneInline(admin.TabularInline):
    model = Stone

    readonly_fields = ["grader"]
    form = StoneForm

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    extra = 0
    max_num = 50


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
        )

    def queryset(self, request, queryset):
        username_filter = self.value()

        if username_filter == "include":
            return queryset

        if username_filter == "me":
            username_filter = request.user.username

        if username_filter:
            fresh_transfers = self.transfer_model.objects.filter(
                to_user__username=username_filter, fresh=True
            )
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

    search_fields = [
        "gradia_parcel_code",
        "customer_parcel_code",
        "receipt__code",
        "receipt__entity__name",
    ]
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
        return [
            "__str__",
            "intake_date",
            "release_date",
            "closed_out",
            self.model.get_action_html_link,
        ]

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

    readonly_fields = ["grader", "date_created"]
    fields = readonly_fields + [
        "gradia_id",
        "receipt",
        "date_to_GW",
        "GW_returned_date",
        "goldway_AI_code",
        "date_to_GIA",
        "GIA_returned_date",
        "GIA_batch_code",
        "parcel",
        "post_GW_rejection",
        "post_GIA_rejection",
        "sample_stone",
        "shape_and_cutting",
        "diamond_description",
        "nano_etch_inscription",
        "basic_carat_1",
        "basic_carat_2",
        "basic_carat_3",
        "basic_final_carat",
        "GW_carat",
        "post_GW_final_carat",
        "GW_repolish_carat",
        "carat_weight",
        "basic_color_1",
        "basic_color_2",
        "basic_color_3",
        "basic_final_color",
        "GW_color",
        "post_GW_final_color",
        "color",
        "basic_clarity_1",
        "basic_clarity_2",
        "basic_clarity_3",
        "basic_final_clarity",
        "GW_clarity",
        "post_GW_final_clarity",
        "clarity",
        "remarks",
        "post_GW_remarks",
        "basic_fluorescence",
        "GW_fluo",
        "post_GW_fluo",
        "fluoresence",
        "basic_culet",
        "GW_culet",
        "post_GW_culet", 
        "culet", 
        "inclusions", 
        "basic_polish_1",
        "basic_polish_2", 
        "basic_polish_3",
        "polish", 
        "dia_minimum", 
        "diameter_max", 
        "height", 
        "girdle_min", 
        "girdle_max", 
        "girdle_grade", 
        "culet_size",
        "total_depth", 
        "total_depth_grade", 
        "sheryl_cut", 
        "sarine_cut", 
        "cut_grade_est_table", 
        "cut_grade", 
        "sheryl_symmetry", 
        "sarine_symmetry", 
        "symmetry_grade", 
        "comments",
        "roundness", 
        "roundness_grade", 
        "table_size", 
        "table_size_grade", 
        "crown_angle", 
        "crown_angle_grade", 
        "pavilion_angle", 
        "pavilion_angle_grade", 
        "star_length", 
        "star_length_grade", 
        "lower_half", 
        "lower_half_grade", 
        "girdle_thick", 
        "girdle_thick_grade", 
        "crown_height", 
        "crown_height_grade", 
        "pavilion_depth", 
        "pavilion_depth_grade", 
        "misalignment", 
        "misalignment_grade", 
        "table_edge_var", 
        "table_edge_var_grade",
        "table_off_center", 
        "table_off_center_grade", 
        "culet_off_center", 
        "culet_off_center_grade", 
        "table_off_culet", 
        "table_off_culet_grade",
        "star_angle", 
        "star_angle_grade", 
        "upper_half_angle", 
        "upper_half_angle_grade",
        "lower_half_angle",
        "lower_half_angle_grade",
    ]
    list_filter = [StoneOwnerFilter]


    def get_list_display(self, request):
        return [
            "gradia_id",
            "current_location",
            "carat_weight",
            "color",
            "clarity",
            "fluoresence",
            "culet",
            "parcel",
        ]

    actions = [
        "transfer_to_goldway",
        "transfer_to_GIA",
        "transfer_to_vault",
        "confirm_received_stones",
        "download_ids",
    ]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.groups.filter(name="vault_manager").exists():
            del actions["transfer_to_goldway"]
            del actions["transfer_to_GIA"]
        return actions

    def download_ids(self, request, queryset):
        from django.http import HttpResponse

        filename = (
            "Stone_id_" + str(datetime.utcnow().strftime("%d-%m-%Y_%H-%M-%S")) + ".txt"
        )
        file = open(filename, "w+")
        for stone in queryset.all():
            file.write(stone.stone_id + ",")
        file.close()

        f = open(filename, "r")
        response = HttpResponse(f, content_type="text/plain")
        response["Content-Disposition"] = "attachment; filename=%s.txt" % filename
        return response

    download_ids.short_description = "Download Diamond(s) External Nanotech IDs"

    def transfer_to_goldway(self, request, queryset):
        vault = User.objects.get(username="vault")
        goldway = User.objects.get(username="goldway")

        for stone in queryset.all():
            StoneTransfer.can_create_transfer(
                item=stone, from_user=vault, to_user=goldway
            )

        verification = GoldwayVerification.objects.create()
        for stone in queryset.all():
            StoneTransfer.initiate_transfer(
                item=stone, from_user=vault, to_user=goldway, created_by=request.user
            )
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
            StoneTransfer.initiate_transfer(
                item=stone, from_user=vault, to_user=gia, created_by=request.user
            )
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
        return True

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


@admin.register(GoldwayVerification)
class GoldwayVerificationAdmin(admin.ModelAdmin):
    model = GoldwayVerification
    list_display = ["purchase_order", "invoice_number", "started", "summary"]


@admin.register(GiaVerification)
class GiaVerificationAdmin(admin.ModelAdmin):
    model = GiaVerification
    list_display = ["receipt_number", "invoice_number", "started", "summary"]

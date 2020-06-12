from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User

from .models import ParcelTransfer, SplitParcelTransfer


class ParcelConfirmation(ParcelTransfer):
    class Meta:
        proxy = True
        verbose_name = "[tmp] Confirm carats and pieces in received parcel"


@admin.register(ParcelConfirmation)
class ParcelConfirmationAdmin(admin.ModelAdmin):
    model = ParcelConfirmation
    model_transfer = ParcelTransfer

    search_fields = ["item"]

    readonly_fields = ["item", "from_user", "initiated_date", "to_user", "confirmed_date", "remarks", "expired"]
    list_display = ["item", "from_user", "initiated_date", "to_user", "confirmed_date", "expired"]
    list_filter = ["expired", "from_user", "to_user", "initiated_date", "confirmed_date"]

    change_form_template = "grading/admin_item_change_form_with_button.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        transfer = self.model_transfer.objects.get(id=object_id)
        if transfer.to_user == request.user and transfer.confirmed_date is None:
            extra_context["can_confirm_transfer"] = True
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):
        if "_confirm_transfer" in request.POST:
            assert request.user == obj.to_user
            assert obj.confirmed_date is None
            obj.confirmed_date = datetime.now()
            obj.save()
        return super().response_change(request, obj)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and obj.to_user == request.user and obj.confirmed_date is None:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SplitParcelTransferConfirmation(SplitParcelTransfer):
    class Meta:
        proxy = True
        verbose_name = "[tmp] Confirm carats and pieces in received split parcel"


@admin.register(SplitParcelTransferConfirmation)
class ParcelTransferToVaultAdmin(admin.ModelAdmin):
    model = SplitParcelTransferConfirmation
    model_transfer = SplitParcelTransfer


class ParcelTransferFromVault(ParcelTransfer):
    class Meta:
        proxy = True
        verbose_name = "[admin] Initiate withdraw of parcels from vault"


@admin.register(ParcelTransferFromVault)
class ParcelTransferFromVaultAdmin(admin.ModelAdmin):
    model = ParcelTransferFromVault

    readonly_fields = ["from_user", "initiated_date", "confirmed_date", "expired"]
    fields = ["item", "from_user", "initiated_date", "to_user", "confirmed_date", "remarks", "expired"]
    list_display = ["item", "from_user", "initiated_date", "to_user", "confirmed_date", "expired"]
    list_filter = ["expired", "from_user", "to_user", "initiated_date", "confirmed_date"]

    def has_add_permission(self, request):
        if request.user.username in ["admin", "anthony", "gary"]:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.from_user = User.objects.get(username="vault")
        obj.save()


class SplitParcelTransferFromVault(SplitParcelTransfer):
    class Meta:
        proxy = True
        verbose_name = "[admin] Initiate withdraw of split parcels from vault"


@admin.register(SplitParcelTransferFromVault)
class SplitParcelTransferFromVaultAdmin(ParcelTransferFromVaultAdmin):
    def save_model(self, request, obj, form, change):
        obj.from_user = User.objects.get(username="vault")
        obj.save()

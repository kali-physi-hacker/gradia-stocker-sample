from django.contrib import admin
from django.contrib.auth.models import User

from .models import ParcelTransfer


class ParcelTransferFromVault(ParcelTransfer):
    class Meta:
        proxy = True
        verbose_name = "[admin] View parcel transfers and initiate withdraw from vault"


@admin.register(ParcelTransferFromVault)
class ParcelTransferFromVaultAdmin(admin.ModelAdmin):
    model = ParcelTransferFromVault

    readonly_fields = ["from_user", "initiated_date", "confirmed_date", "fresh"]
    fields = ["item"] + readonly_fields + ["remarks"]
    list_display = ["item"] + readonly_fields
    list_filter = ["fresh", "from_user", "to_user", "initiated_date", "confirmed_date"]

    def has_add_permission(self, request):
        if request.user.username in ["admin", "anthony", "gary"]:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        obj.from_user = User.objects.get(username="vault")
        obj.save()

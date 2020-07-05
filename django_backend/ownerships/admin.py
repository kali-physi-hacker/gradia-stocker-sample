from django.contrib import admin
from django.contrib.auth.models import User

from .models import VAULT_USERNAMES, ParcelTransfer


class ParcelTransferFromVault(ParcelTransfer):
    class Meta:
        proxy = True
        verbose_name = "[admin] View parcel transfers and initiate withdraw from vault"


@admin.register(ParcelTransferFromVault)
class ParcelTransferFromVaultAdmin(admin.ModelAdmin):
    model = ParcelTransferFromVault

    readonly_fields = ["from_user", "initiated_date", "confirmed_date", "fresh"]
    fields = ["item", "from_user", "initiated_date", "to_user", "confirmed_date", "remarks", "fresh"]
    list_display = fields
    list_filter = ["fresh", "from_user", "to_user", "initiated_date", "confirmed_date"]

    def has_add_permission(self, request):
        if request.user.username in VAULT_USERNAMES:
            return True
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        vault = User.objects.get(username="vault")
        created = ParcelTransfer.initiate_transfer(obj.item, vault, obj.to_user, obj.remarks)
        obj.from_user = vault
        obj.pk = created.pk

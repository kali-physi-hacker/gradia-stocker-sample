from django.contrib import admin
from django.contrib.auth.models import User

from .models import ParcelTransfer


@admin.register(ParcelTransfer)
class ParcelTransferAdmin(admin.ModelAdmin):
    model = ParcelTransfer

    readonly_fields = ["from_user", "initiated_date", "confirmed_date", "fresh"]
    fields = ["item", "from_user", "initiated_date", "to_user", "confirmed_date", "remarks", "fresh"]
    list_display = fields
    list_filter = ["fresh", "from_user", "to_user", "initiated_date", "confirmed_date"]

    def has_add_permission(self, request):
        if request.user.groups.filter(name="vault_manager").exists():
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

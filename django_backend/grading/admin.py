from datetime import datetime

from django.contrib import admin

from .models import Parcel, Receipt


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    model = Parcel

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CreateReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "1. create receipt for stone intake"


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

    def save_model(self, request, obj, form, change):
        obj.intake_by = request.user
        obj.save()


class CloseOutReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "2. close out receipt for stone release"


def close_out(modeladmin, request, queryset):
    queryset.update(release_by=request.user, release_date=datetime.now())


close_out.short_description = "Close out selected recipt"


@admin.register(CloseOutReceipt)
class CloseOutReceiptAdmin(admin.ModelAdmin):
    model = CloseOutReceipt
    actions = [close_out]

    list_filter = ["release_date"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

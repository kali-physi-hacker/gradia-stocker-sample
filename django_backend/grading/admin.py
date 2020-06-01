from datetime import datetime

from django.contrib import admin

from .models import Parcel, Receipt


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

    """
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            if isinstance(instance, Parcel):
                instance.intake_by = request.user
                instance.save()
            print(instance)
    """


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    model = Parcel

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CloseOutReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "2. close out receipt for stone release"


class ParcelOutInline(admin.StackedInline):
    model = Parcel
    fields = ["name", "code", "total_carats", "total_pieces"]
    readonly_fields = ["name", "code", "total_carats", "total_pieces"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CloseOutReceipt)
class CloseOutReceiptAdmin(admin.ModelAdmin):
    model = CloseOutReceipt
    readonly_fields = ["entity", "code", "intake_by", "intake_date", "release_by", "release_date"]

    inlines = [ParcelOutInline]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.release_by = request.user
        obj.release_date = datetime.now()
        obj.save()

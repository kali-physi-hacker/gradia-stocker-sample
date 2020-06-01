from datetime import datetime

from django.contrib import admin
from django.http import HttpResponse

from .models import Parcel, Receipt


class CreateReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "1. Create receipt for stone intake"


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

    def has_view_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.intake_by = request.user
        obj.save()


class ParcelView(Parcel):
    class Meta:
        proxy = True
        verbose_name = "2. View parcel info"


@admin.register(ParcelView)
class ParcelViewAdmin(admin.ModelAdmin):
    model = ParcelView

    readonly_fields = ["name", "code", "total_carats", "total_pieces"]

    search_fields = ["name", "code", "receipt__code", "receipt__entity__name"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class CloseOutReceipt(Receipt):
    class Meta:
        proxy = True
        verbose_name = "3. View receipts and close out receipt on stone release"


@admin.register(CloseOutReceipt)
class CloseOutReceiptAdmin(admin.ModelAdmin):
    model = CloseOutReceipt

    list_filter = ["release_date", "intake_date"]

    search_fields = ["code", "entity__name"]

    readonly_fields = ["code", "entity", "intake_by", "intake_date", "release_by", "release_date"]

    change_form_template = "grading/admin_item_change_form_with_button.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["has_change_permission"] = self.has_change_permission(
            request, Receipt.objects.get(id=object_id)
        )
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        if obj and not obj.closed_out():
            return True
        return False

    def response_change(self, request, obj):
        if "_close_out" in request.POST:
            if obj.closed_out():
                return HttpResponse("Error: This receipt has already been closed out")
            obj.release_by = request.user
            obj.release_date = datetime.now()
            obj.save()
        return super().response_change(request, obj)

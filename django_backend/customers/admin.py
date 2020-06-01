from datetime import datetime

from django.contrib import admin

from .models import AuthorizedPersonnel, Consignment, Entity, Parcel

# Register your models here.


class AuthorizedPersonnelInline(admin.StackedInline):
    model = AuthorizedPersonnel

    extra = 1


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    model = Entity

    inlines = [AuthorizedPersonnelInline]


class ConsignmentIn(Consignment):
    class Meta:
        proxy = True


class ParcelInline(admin.TabularInline):
    model = Parcel
    fields = ["name", "code", "total_carats", "total_pieces", "reference_price_per_carat"]

    extra = 1


@admin.register(ConsignmentIn)
class ConsignmentAdmin(admin.ModelAdmin):
    model = ConsignmentIn

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


class ConsignmentOut(Consignment):
    class Meta:
        proxy = True


class ParcelOutInline(admin.StackedInline):
    model = Parcel
    fields = [
        "name",
        "code",
        "total_carats",
        "total_pieces",
        "reference_price_per_carat",
        "rejected_carats",
        "rejected_pieces",
        "basic_graded_carats",
        "basic_graded_pieces",
        "triple_verified_carats",
        "triple_verified_pieces",
    ]
    readonly_fields = ["name", "code", "total_carats", "total_pieces", "reference_price_per_carat"]
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConsignmentOut)
class ConsignmentOutAdmin(admin.ModelAdmin):
    model = ConsignmentOut
    readonly_fields = ["entity", "receipt_number", "intake_by", "intake_date", "release_by", "release_date"]

    inlines = [ParcelOutInline]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.release_by = request.user
        obj.release_date = datetime.now()
        obj.save()

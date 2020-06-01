from django.contrib import admin

# Register your models here.
from .models import AuthorizedPersonnel, Seller


class AuthorizedPersonnelInline(admin.StackedInline):
    model = AuthorizedPersonnel

    extra = 1


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    model = Seller

    inlines = [AuthorizedPersonnelInline]

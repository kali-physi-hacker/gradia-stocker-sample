from django.contrib import admin

from .models import AuthorizedPersonnel, Entity

# Register your models here.


class AuthorizedPersonnelInline(admin.StackedInline):
    model = AuthorizedPersonnel

    extra = 1


@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    model = Entity

    inlines = [AuthorizedPersonnelInline]

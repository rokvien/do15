from django.contrib import admin
from .models import (
    Site,
    Workshop,
    EquipmentType,
    Characteristic,
    Equipment,
    EquipmentCharacteristicValue,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "created_at")
    search_fields = ("name", "address")
    ordering = ("name",)


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "site", "created_at")
    list_filter = ("site",)
    search_fields = ("name", "site__name")
    ordering = ("name",)


class CharacteristicInline(admin.TabularInline):
    model = Characteristic
    extra = 1


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    inlines = [CharacteristicInline]


class EquipmentCharacteristicValueInline(admin.TabularInline):
    model = EquipmentCharacteristicValue
    extra = 1


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "inventory_number", "equipment_type", "workshop", "parent", "created_at",)
    list_filter = ("equipment_type", "workshop", "workshop__site", "created_at",)
    search_fields = ("name", "inventory_number", "equipment_type__name", "workshop__name",)
    autocomplete_fields = ("equipment_type", "workshop", "parent",)
    inlines = [EquipmentCharacteristicValueInline]
    ordering = ("name",)
    list_select_related = ("equipment_type", "workshop", "parent",)

    def has_delete_permission(self, request, obj=None):
        return request.user.groups.filter(name="Admin").exists()


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "equipment_type", "value_type")
    list_filter = ("equipment_type", "value_type")
    search_fields = ("name", "equipment_type__name")


@admin.register(EquipmentCharacteristicValue)
class EquipmentCharacteristicValueAdmin(admin.ModelAdmin):
    list_display = ("id", "equipment", "characteristic", "value")
    list_filter = ("characteristic",)
    search_fields = (
        "equipment__name",
        "characteristic__name",
        "value",
    )





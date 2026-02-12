import django_filters
from .models import Equipment


class EquipmentFilter(django_filters.FilterSet):
    workshop = django_filters.NumberFilter(field_name="workshop_id")
    site = django_filters.NumberFilter(field_name="workshop__site_id")
    equipment_type = django_filters.NumberFilter(field_name="equipment_type_id")
    name = django_filters.CharFilter(lookup_expr="icontains")
    inventory_number = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Equipment
        fields = [
            "workshop",
            "site",
            "equipment_type",
            "name",
            "inventory_number",
        ]

# import django_filters
# from .models import Equipment
#
# class EquipmentFilter(django_filters.FilterSet):
#     name = django_filters.CharFilter(lookup_expr='icontains')
#     inventory_number = django_filters.CharFilter(lookup_expr='icontains')
#     equipment_type = django_filters.ModelChoiceFilter(queryset=Equipment.objects.all())
#     workshop = django_filters.ModelChoiceFilter(queryset=Equipment.objects.all())
#
#     class Meta:
#         model = Equipment
#         fields = ['name', 'inventory_number', 'equipment_type', 'workshop']

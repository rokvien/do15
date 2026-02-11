import django_filters
from .models import Equipment


class EquipmentHTMLFilter(django_filters.FilterSet):

    name = django_filters.CharFilter(lookup_expr="icontains", label="Название")
    inventory_number = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Инвентарный номер"
    )

    class Meta:
        model = Equipment
        fields = ["equipment_type", "workshop"]



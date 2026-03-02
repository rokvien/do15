from rest_framework import serializers
from .models import Site, Workshop, EquipmentType, Equipment


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'address']


class WorkshopSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source='site.name', read_only=True)

    class Meta:
        model = Workshop
        fields = ['id', 'name', 'site', 'site_name']


class EquipmentTypeSerializer(serializers.ModelSerializer):
    characteristics = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'characteristics']


class EquipmentSerializer(serializers.ModelSerializer):
    equipment_type = serializers.PrimaryKeyRelatedField(queryset=EquipmentType.objects.all())
    workshop = serializers.PrimaryKeyRelatedField(queryset=Workshop.objects.all())
    parent = serializers.PrimaryKeyRelatedField(queryset=Equipment.objects.all(), allow_null=True, required=False)
    equipment_type_name = serializers.CharField(source='equipment_type.name', read_only=True)
    workshop_name = serializers.CharField(source='workshop.name', read_only=True)
    site_name = serializers.CharField(source='workshop.site.name', read_only=True)

    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'inventory_number', 'equipment_type', 'equipment_type_name',
            'workshop', 'workshop_name', 'site_name', 'parent', 'created_at'
        ]

from rest_framework import serializers
from .models import Site, Workshop, EquipmentType, Equipment


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ['id', 'name', 'address']


class WorkshopSerializer(serializers.ModelSerializer):
    site = serializers.StringRelatedField()

    class Meta:
        model = Workshop
        fields = ['id', 'name', 'site']


class EquipmentTypeSerializer(serializers.ModelSerializer):
    characteristics = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = EquipmentType
        fields = ['id', 'name', 'characteristics']


class EquipmentSerializer(serializers.ModelSerializer):
    equipment_type = serializers.StringRelatedField()
    workshop = serializers.StringRelatedField()
    site = serializers.SerializerMethodField()
    parent = serializers.StringRelatedField()

    class Meta:
        model = Equipment
        fields = ['id', 'name', 'inventory_number', 'equipment_type', 'workshop', 'site', 'parent', 'created_at']

    def get_site(self, obj):
        if obj.workshop and obj.workshop.site:
            return obj.workshop.site.name
        return None

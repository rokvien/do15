from rest_framework import serializers
from .models import (
    Site,
    Workshop,
    EquipmentType,
    Characteristic,
    Equipment,
    EquipmentCharacteristicValue,
)


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = "__all__"


class WorkshopSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source="site.name", read_only=True)

    class Meta:
        model = Workshop
        fields = "__all__"


class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = "__all__"


class EquipmentTypeSerializer(serializers.ModelSerializer):
    characteristics = CharacteristicSerializer(many=True, read_only=True)

    class Meta:
        model = EquipmentType
        fields = "__all__"


class EquipmentCharacteristicValueSerializer(serializers.ModelSerializer):
    characteristic_name = serializers.CharField(source="characteristic.name", read_only=True)
    characteristic = serializers.PrimaryKeyRelatedField(queryset=Characteristic.objects.all())

    class Meta:
        model = EquipmentCharacteristicValue
        fields = ["id", "characteristic", "characteristic_name", "value"]


class EquipmentSerializer(serializers.ModelSerializer):
    characteristic_values = EquipmentCharacteristicValueSerializer(many=True, required=False)

    class Meta:
        model = Equipment
        fields = ["id", "name", "inventory_number", "equipment_type", "workshop", "parent", "passport_scan", "characteristic_values"]

    def create(self, validated_data):
        char_data = validated_data.pop("characteristic_values", [])
        equipment = Equipment.objects.create(**validated_data)
        for item in char_data:
            EquipmentCharacteristicValue.objects.create(equipment=equipment, characteristic=item["characteristic"], value=item["value"])
        return equipment

    def update(self, instance, validated_data):
        char_data = validated_data.pop("characteristic_values", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if char_data is not None:
            instance.characteristic_values.all().delete()
            for item in char_data:
                EquipmentCharacteristicValue.objects.create(equipment=instance, characteristic=item["characteristic"], value=item["value"])
        return instance

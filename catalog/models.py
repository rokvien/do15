from django.db import models
from django.core.validators import MinLengthValidator


class Site(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"

    def __str__(self):
        return self.name


class Workshop(models.Model):
    name = models.CharField(
        max_length=255,
        db_index=True
    )
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="workshops"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("name", "site")
        ordering = ["name"]
        verbose_name = "Цех"
        verbose_name_plural = "Цеха"

    def __str__(self):
        return f"{self.name} ({self.site.name})"


class EquipmentType(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудования"

    def __str__(self):
        return self.name


class Characteristic(models.Model):

    VALUE_TYPE_STRING = "string"
    VALUE_TYPE_NUMBER = "number"
    VALUE_TYPE_DATE = "date"
    VALUE_TYPE_BOOLEAN = "boolean"

    VALUE_TYPE_CHOICES = [
        (VALUE_TYPE_STRING, "Строка"),
        (VALUE_TYPE_NUMBER, "Число"),
        (VALUE_TYPE_DATE, "Дата"),
        (VALUE_TYPE_BOOLEAN, "Логическое"),
    ]

    name = models.CharField(max_length=255)
    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.CASCADE,
        related_name="characteristics"
    )
    value_type = models.CharField(
        max_length=20,
        choices=VALUE_TYPE_CHOICES
    )

    class Meta:
        unique_together = ("name", "equipment_type")
        ordering = ["name"]
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

    def __str__(self):
        return f"{self.name} ({self.equipment_type.name})"


class Equipment(models.Model):
    name = models.CharField(
        max_length=255,
        db_index=True
    )

    inventory_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )

    equipment_type = models.ForeignKey(
        EquipmentType,
        on_delete=models.PROTECT,
        related_name="equipments"
    )

    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.PROTECT,
        related_name="equipments"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children"
    )

    passport_scan = models.FileField(
        upload_to="passports/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"

    def __str__(self):
        return f"{self.name} ({self.inventory_number})"


class EquipmentCharacteristicValue(models.Model):
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="characteristic_values"
    )

    characteristic = models.ForeignKey(
        Characteristic,
        on_delete=models.CASCADE,
        related_name="values"
    )

    value = models.TextField()

    class Meta:
        unique_together = ("equipment", "characteristic")
        verbose_name = "Значение характеристики"
        verbose_name_plural = "Значения характеристик"

    def __str__(self):
        return f"{self.equipment.name} - {self.characteristic.name}: {self.value}"



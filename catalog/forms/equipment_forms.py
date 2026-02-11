from django import forms
from catalog.models import Equipment


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'inventory_number', 'equipment_type', 'workshop', 'passport_scan']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'inventory_number': forms.TextInput(attrs={'class': 'form-control'}),
            'equipment_type': forms.Select(attrs={'class': 'form-select'}),
            'workshop': forms.Select(attrs={'class': 'form-select'}),
            'passport_scan': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }



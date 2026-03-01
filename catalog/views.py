from drf_spectacular.utils import extend_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.throttling import UserRateThrottle

from .models import Site, Workshop, EquipmentType, Equipment
from .serializers import (SiteSerializer, WorkshopSerializer, EquipmentTypeSerializer, EquipmentSerializer)
from .permissions import RolesPermissions
from .filters import EquipmentFilter


class SiteViewSet(ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [RolesPermissions]
    throttle_classes = [UserRateThrottle]


class WorkshopViewSet(ModelViewSet):
    queryset = Workshop.objects.select_related("site")
    serializer_class = WorkshopSerializer
    permission_classes = [RolesPermissions]
    throttle_classes = [UserRateThrottle]


class EquipmentTypeViewSet(ModelViewSet):
    queryset = EquipmentType.objects.prefetch_related("characteristics")
    serializer_class = EquipmentTypeSerializer
    permission_classes = [RolesPermissions]
    throttle_classes = [UserRateThrottle]


@extend_schema(description="Equipment management API with role-based access")
class EquipmentViewSet(ModelViewSet):
    queryset = Equipment.objects.select_related(
        "equipment_type", "workshop", "workshop__site", "parent"
    ).prefetch_related("characteristic_values__characteristic")
    serializer_class = EquipmentSerializer
    filterset_class = EquipmentFilter
    search_fields = ["name", "inventory_number"]
    ordering_fields = ["name", "created_at"]
    permission_classes = [RolesPermissions]
    throttle_classes = [UserRateThrottle]

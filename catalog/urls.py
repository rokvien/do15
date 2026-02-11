from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SiteViewSet,
    WorkshopViewSet,
    EquipmentTypeViewSet,
    EquipmentViewSet,
)
from .views import (
    EquipmentListView,
    EquipmentDetailView,
    EquipmentCreateView,
    EquipmentUpdateView,
    EquipmentDeleteView,
)

router = DefaultRouter()

router.register("sites", SiteViewSet)
router.register("workshops", WorkshopViewSet)
router.register("equipment-types", EquipmentTypeViewSet)
router.register("equipment", EquipmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("catalog/", EquipmentListView.as_view(), name="equipment_list"),
    path("catalog/<int:pk>/", EquipmentDetailView.as_view(), name="equipment_detail"),
    path("catalog/create/", EquipmentCreateView.as_view(), name="equipment_create"),
    path("catalog/<int:pk>/edit/", EquipmentUpdateView.as_view(), name="equipment_update"),
    path("catalog/<int:pk>/delete/", EquipmentDeleteView.as_view(), name="equipment_delete"),
]



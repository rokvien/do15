from django.urls import path, include
from rest_framework.routers import DefaultRouter

from catalog.views import SiteViewSet, WorkshopViewSet, EquipmentTypeViewSet, EquipmentViewSet

router = DefaultRouter()
router.register("sites", SiteViewSet)
router.register("workshops", WorkshopViewSet)
router.register("equipment-types", EquipmentTypeViewSet)
router.register("equipment", EquipmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

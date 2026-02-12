from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import ModelViewSet

from .forms.equipment_forms import EquipmentForm
from .models import *
from .serializers import *
from .filters import EquipmentFilter
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .html_filters import EquipmentHTMLFilter
from catalog.permissions import RoleBasedPermission
from .models import Equipment


class RoleRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        if user.groups.filter(name="Admin").exists():
            return True
        if user.groups.filter(name="Manager").exists():
            if isinstance(self, DeleteView):
                return False
            return True
        if user.groups.filter(name="Viewer").exists():
            return self.request.method == "GET"
        return False


class SiteViewSet(ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteSerializer


class WorkshopViewSet(ModelViewSet):
    queryset = Workshop.objects.select_related("site")
    serializer_class = WorkshopSerializer


class EquipmentTypeViewSet(ModelViewSet):
    queryset = EquipmentType.objects.prefetch_related("characteristics")
    serializer_class = EquipmentTypeSerializer


class EquipmentViewSet(ModelViewSet):
    queryset = Equipment.objects.select_related(
        "equipment_type",
        "workshop",
        "workshop__site",
        "parent",
    ).prefetch_related(
        "characteristic_values__characteristic"
    )

    serializer_class = EquipmentSerializer
    filterset_class = EquipmentFilter
    search_fields = ["name", "inventory_number"]
    ordering_fields = ["name", "created_at"]
    permission_classes = [RoleBasedPermission]
    throttle_classes = [UserRateThrottle]


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = "equipment/list.html"
    context_object_name = "equipments"
    paginate_by = 2

    def get_queryset(self):
        queryset = Equipment.objects.select_related("equipment_type", "workshop", "workshop__site",)
        self.filterset = EquipmentHTMLFilter(self.request.GET, queryset=queryset)
        qs = self.filterset.qs
        sort = self.request.GET.get("sort")
        if sort == "inventory_number":
            qs = qs.order_by("inventory_number")
        elif sort == "-inventory_number":
            qs = qs.order_by("-inventory_number")
        else:
            qs = qs.order_by("name")
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filterset
        return context


# class EquipmentListView(LoginRequiredMixin, ListView):
#     model = Equipment
#     template_name = "equipment/list.html"
#     context_object_name = "equipments"
#     paginate_by = 2
#
#     def get_queryset(self):
#         queryset = Equipment.objects.select_related(
#             "equipment_type",
#             "workshop",
#             "workshop__site",
#             "sort",
#         ).all()
#
#         self.filterset = EquipmentHTMLFilter(
#             self.request.GET,
#             queryset=queryset
#         )
#
#         return self.filterset.qs
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["filter"] = self.filterset
#         return context


class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = "equipment/detail.html"
    context_object_name = "equipment"


class EquipmentCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    model = Equipment
    fields = ["name", "inventory_number", "equipment_type", "workshop", "parent", "passport_scan"]
    template_name = "equipment/form.html"
    success_url = reverse_lazy("equipment_list")


class EquipmentUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    model = Equipment
    fields = ["name", "inventory_number", "equipment_type", "workshop", "parent", "passport_scan"]
    template_name = "equipment/form.html"
    success_url = reverse_lazy("equipment_list")


class EquipmentDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    model = Equipment
    template_name = "equipment/delete.html"
    success_url = reverse_lazy("equipment_list")

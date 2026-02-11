import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User, Group
from catalog.models import Site, Workshop, EquipmentType, Equipment, Characteristic
from catalog.permissions import RoleBasedPermission

# =====================================
# Fixtures
# =====================================

@pytest.fixture(scope="session", autouse=True)
def create_roles(django_db_setup, django_db_blocker):
    """Создаём группы ролей в БД: Admin, Manager, Viewer"""
    with django_db_blocker.unblock():
        Group.objects.get_or_create(name="Admin")
        Group.objects.get_or_create(name="Manager")
        Group.objects.get_or_create(name="Viewer")


@pytest.fixture
def admin_user(db):
    """Пользователь с ролью Admin"""
    user = User.objects.create_user(username="admin", password="password")
    group = Group.objects.get(name="Admin")
    user.groups.add(group)
    return user


@pytest.fixture
def manager_user(db):
    """Пользователь с ролью Manager"""
    user = User.objects.create_user(username="manager", password="password")
    group = Group.objects.get(name="Manager")
    user.groups.add(group)
    return user


@pytest.fixture
def viewer_user(db):
    """Пользователь с ролью Viewer"""
    user = User.objects.create_user(username="viewer", password="password")
    group = Group.objects.get(name="Viewer")
    user.groups.add(group)
    return user


@pytest.fixture
def equipment_data(db):
    """Создаём базовое оборудование для тестов"""
    site = Site.objects.create(name="Site1")
    workshop = Workshop.objects.create(name="Workshop1", site=site)
    eq_type = EquipmentType.objects.create(name="Pump")
    equipment = Equipment.objects.create(
        name="Pump1",
        inventory_number="INV001",
        equipment_type=eq_type,
        workshop=workshop
    )
    return equipment


# =====================================
# Disable throttling for tests
# =====================================

@pytest.fixture(autouse=True)
def disable_throttling(monkeypatch):
    """Отключаем троттлинг DRF для тестов"""
    from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
    monkeypatch.setattr(UserRateThrottle, 'allow_request', lambda self, request, view: True)
    monkeypatch.setattr(AnonRateThrottle, 'allow_request', lambda self, request, view: True)


# =====================================
# Tests: Authentication
# =====================================

@pytest.mark.django_db
def test_api_list_requires_auth():
    """Невозможно получить список оборудования без аутентификации"""
    client = APIClient()
    response = client.get("/api/equipment/")
    assert response.status_code == 401


# =====================================
# Tests: Roles and permissions
# =====================================

@pytest.mark.django_db
def test_viewer_can_only_get(viewer_user, equipment_data):
    """Viewer может только GET, запрещены POST, PUT, DELETE"""
    client = APIClient()
    client.force_authenticate(user=viewer_user)

    # GET — разрешено
    response = client.get(f"/api/equipment/{equipment_data.id}/")
    assert response.status_code == 200

    # POST — запрещено
    response = client.post("/api/equipment/", {
        "name": "Pump2",
        "inventory_number": "INV002",
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")
    assert response.status_code in [403, 401]

    # PUT — запрещено
    response = client.put(f"/api/equipment/{equipment_data.id}/", {
        "name": "Pump1 Updated",
        "inventory_number": equipment_data.inventory_number,
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")
    assert response.status_code in [403, 401]

    # DELETE — запрещено
    response = client.delete(f"/api/equipment/{equipment_data.id}/")
    assert response.status_code in [403, 401]


@pytest.mark.django_db
def test_manager_can_crud_but_not_delete(manager_user, equipment_data):
    """Manager может создавать и редактировать, но не удалять"""
    client = APIClient()
    client.force_authenticate(user=manager_user)

    # POST — разрешено
    response = client.post("/api/equipment/", {
        "name": "Pump2",
        "inventory_number": "INV002",
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")
    assert response.status_code == 201

    # PUT — разрешено
    response = client.put(f"/api/equipment/{equipment_data.id}/", {
        "name": "Pump1 Updated",
        "inventory_number": equipment_data.inventory_number,
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")
    assert response.status_code == 200

    # DELETE — запрещено
    response = client.delete(f"/api/equipment/{equipment_data.id}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_crud(admin_user, equipment_data):
    """Admin имеет полный доступ: create, read, update, delete"""
    client = APIClient()
    client.force_authenticate(user=admin_user)

    # POST
    response = client.post("/api/equipment/", {
        "name": "Pump2",
        "inventory_number": "INV002",
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")
    assert response.status_code == 201

    # PUT
    response = client.put(f"/api/equipment/{equipment_data.id}/", {
        "name": "Pump1 Updated",
        "inventory_number": equipment_data.inventory_number,
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")
    assert response.status_code == 200

    # DELETE
    response = client.delete(f"/api/equipment/{equipment_data.id}/")
    assert response.status_code == 204


# =====================================
# Tests: Filters, search, ordering, pagination
# =====================================

@pytest.mark.django_db
def test_equipment_list_filters(admin_user, db):
    """Проверяем фильтры, поиск, сортировку и пагинацию"""
    client = APIClient()
    client.force_authenticate(user=admin_user)

    # Создаём несколько объектов
    site = Site.objects.create(name="Site2")
    workshop = Workshop.objects.create(name="Workshop2", site=site)
    eq_type = EquipmentType.objects.create(name="Valve")
    for i in range(5):
        Equipment.objects.create(
            name=f"Valve{i}",
            inventory_number=f"INV{i+100}",
            equipment_type=eq_type,
            workshop=workshop
        )

    # Пагинация
    response = client.get("/api/equipment/")
    assert response.status_code == 200
    assert "results" in response.data
    assert len(response.data["results"]) <= 2  # PAGE_SIZE = 2

    # Поиск
    response = client.get("/api/equipment/?search=Valve3")
    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["name"] == "Valve3"

    # Ordering
    response = client.get("/api/equipment/?ordering=-name")
    assert response.status_code == 200
    names = [item["name"] for item in response.data["results"]]
    assert names == sorted(names, reverse=True)[:2]


# =====================================
# Tests: Equipment with characteristics
# =====================================

@pytest.mark.django_db
def test_equipment_with_characteristics(admin_user, db):
    """Создание оборудования с характеристиками и обновление"""
    client = APIClient()
    client.force_authenticate(user=admin_user)


    site = Site.objects.create(name="Site3")
    workshop = Workshop.objects.create(name="Workshop3", site=site)
    eq_type = EquipmentType.objects.create(name="Motor")
    char_speed = Characteristic.objects.create(name="Speed", equipment_type=eq_type, value_type="number")
    char_voltage = Characteristic.objects.create(name="Voltage", equipment_type=eq_type, value_type="number")

    # Создание оборудования с характеристиками
    response = client.post("/api/equipment/", {
        "name": "Motor1",
        "inventory_number": "INV500",
        "equipment_type": eq_type.id,
        "workshop": workshop.id,
        "characteristic_values": [
            {"characteristic": char_speed.id, "value": "1500"},
            {"characteristic": char_voltage.id, "value": "220"}
        ]
    }, format="json")
    assert response.status_code == 201
    data = response.data
    assert len(data["characteristic_values"]) == 2

    # Обновление характеристик
    equipment_id = data["id"]
    response = client.put(f"/api/equipment/{equipment_id}/", {
        "name": "Motor1 Updated",
        "inventory_number": "INV500",
        "equipment_type": eq_type.id,
        "workshop": workshop.id,
        "characteristic_values": [
            {"characteristic": char_speed.id, "value": "1600"},
        ]
    }, format="json")
    assert response.status_code == 200
    assert len(response.data["characteristic_values"]) == 1
    assert response.data["characteristic_values"][0]["value"] == "1600"
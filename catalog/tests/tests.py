import pytest
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from django.conf import settings

from catalog.models import Site, Workshop, EquipmentType, Equipment


# =========================================================
# FIXTURES
# =========================================================

@pytest.fixture(scope="session", autouse=True)
def create_roles(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        Group.objects.get_or_create(name="Admin")
        Group.objects.get_or_create(name="Manager")
        Group.objects.get_or_create(name="Viewer")


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    user = User.objects.create_user("admin", password="pass")
    user.groups.add(Group.objects.get(name="Admin"))
    return user


@pytest.fixture
def manager_user(db):
    user = User.objects.create_user("manager", password="pass")
    user.groups.add(Group.objects.get(name="Manager"))
    return user


@pytest.fixture
def viewer_user(db):
    user = User.objects.create_user("viewer", password="pass")
    user.groups.add(Group.objects.get(name="Viewer"))
    return user


@pytest.fixture
def equipment_data(db):
    site = Site.objects.create(name="Площадка 1")
    workshop = Workshop.objects.create(name="Цех 1", site=site)
    eq_type = EquipmentType.objects.create(name="Ручной инструмент")

    equipment = Equipment.objects.create(
        name="Молоток1",
        inventory_number="М001",
        equipment_type=eq_type,
        workshop=workshop
    )

    return equipment


# =========================================================
# JWT TESTS
# =========================================================

@pytest.mark.django_db
def test_jwt_token_obtain(api_client):
    User.objects.create_user(username="тест", password="пароль123")

    response = api_client.post("/api/token/", {
        "username": "тест",
        "password": "пароль123"
    })

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_protected_endpoint_requires_auth(api_client):
    response = api_client.get("/api/equipment/")
    assert response.status_code == 401


# =========================================================
# PERMISSIONS TESTS
# =========================================================

@pytest.mark.django_db
def test_viewer_can_get(api_client, viewer_user, equipment_data):
    api_client.force_authenticate(viewer_user)
    response = api_client.get("/api/equipment/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_viewer_cannot_post(api_client, viewer_user):
    api_client.force_authenticate(viewer_user)
    response = api_client.post("/api/equipment/", {})
    assert response.status_code == 403


@pytest.mark.django_db
def test_manager_can_post(api_client, manager_user, equipment_data):
    api_client.force_authenticate(manager_user)

    response = api_client.post("/api/equipment/", {
        "name": "Молоток2",
        "inventory_number": "М002",
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")

    assert response.status_code == 201


@pytest.mark.django_db
def test_manager_cannot_delete(api_client, manager_user, equipment_data):
    api_client.force_authenticate(manager_user)
    response = api_client.delete(f"/api/equipment/{equipment_data.id}/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_admin_can_delete(api_client, admin_user, equipment_data):
    api_client.force_authenticate(admin_user)
    response = api_client.delete(f"/api/equipment/{equipment_data.id}/")
    assert response.status_code == 204


# =========================================================
# CRUD TESTS
# =========================================================

@pytest.mark.django_db
def test_create_equipment(api_client, admin_user, equipment_data):
    api_client.force_authenticate(admin_user)

    response = api_client.post("/api/equipment/", {
        "name": "Дрель1",
        "inventory_number": "Д001",
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")

    assert response.status_code == 201
    assert response.data["name"] == "Дрель1"


@pytest.mark.django_db
def test_update_equipment(api_client, admin_user, equipment_data):
    api_client.force_authenticate(admin_user)

    response = api_client.put(f"/api/equipment/{equipment_data.id}/", {
        "name": "МолотокОбновленный",
        "inventory_number": "М001",
        "equipment_type": equipment_data.equipment_type.id,
        "workshop": equipment_data.workshop.id,
        "characteristic_values": []
    }, format="json")

    assert response.status_code == 200
    assert response.data["name"] == "МолотокОбновленный"


@pytest.mark.django_db
def test_list_equipment(api_client, admin_user, equipment_data):
    api_client.force_authenticate(admin_user)
    response = api_client.get("/api/equipment/")
    assert response.status_code == 200
    assert "results" in response.data


# =========================================================
# FILTER TESTS
# =========================================================

@pytest.mark.django_db
def test_filter_by_equipment_type(api_client, admin_user, equipment_data):
    api_client.force_authenticate(admin_user)

    response = api_client.get(
        f"/api/equipment/?equipment_type={equipment_data.equipment_type.id}"
    )

    assert response.status_code == 200
    assert response.data["results"][0]["equipment_type"] == equipment_data.equipment_type.id


@pytest.mark.django_db
def test_search_by_name(api_client, admin_user, equipment_data):
    api_client.force_authenticate(admin_user)

    response = api_client.get("/api/equipment/?search=Молоток")

    assert response.status_code == 200
    assert len(response.data["results"]) >= 1


@pytest.mark.django_db
def test_ordering_desc(api_client, admin_user, equipment_data):
    api_client.force_authenticate(admin_user)

    Equipment.objects.create(
        name="Дрель1",
        inventory_number="Д001",
        equipment_type=equipment_data.equipment_type,
        workshop=equipment_data.workshop
    )

    response = api_client.get("/api/equipment/?ordering=-name")

    assert response.status_code == 200
    names = [item["name"] for item in response.data["results"]]
    assert names == sorted(names, reverse=True)


# =========================================================
# PAGINATION TEST
# =========================================================

@pytest.mark.django_db
def test_pagination(api_client, admin_user, equipment_data):
    api_client.force_authenticate(admin_user)

    for i in range(10):
        Equipment.objects.create(
            name=f"Станок{i}",
            inventory_number=f"С{i:03d}",
            equipment_type=equipment_data.equipment_type,
            workshop=equipment_data.workshop
        )

    response = api_client.get("/api/equipment/")

    assert response.status_code == 200
    assert len(response.data["results"]) <= settings.REST_FRAMEWORK["PAGE_SIZE"]


# =========================================================
# THROTTLING TEST
# =========================================================

@pytest.mark.django_db
def test_throttling_limit(api_client, admin_user, equipment_data, settings):
    settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
        "user": "2/min"
    }

    api_client.force_authenticate(admin_user)

    api_client.get("/api/equipment/")
    api_client.get("/api/equipment/")
    response = api_client.get("/api/equipment/")

    assert response.status_code == 429
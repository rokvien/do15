from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Equipment


class Command(BaseCommand):
    help = "Создание ролей и назначение прав"

    def handle(self, *args, **kwargs):

        # Создание групп
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        viewer_group, _ = Group.objects.get_or_create(name="Viewer")

        # Получаем права для Equipment
        content_type = ContentType.objects.get_for_model(Equipment)
        permissions = Permission.objects.filter(content_type=content_type)

        for permission in permissions:
            if permission.codename.startswith("view_"):
                viewer_group.permissions.add(permission)
                manager_group.permissions.add(permission)
                admin_group.permissions.add(permission)

            if permission.codename.startswith("add_"):
                manager_group.permissions.add(permission)
                admin_group.permissions.add(permission)

            if permission.codename.startswith("change_"):
                manager_group.permissions.add(permission)
                admin_group.permissions.add(permission)

            if permission.codename.startswith("delete_"):
                admin_group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS("Роли успешно созданы"))



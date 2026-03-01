from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Equipment


class Command(BaseCommand):
    help = "создание ролей и назначение прав"

    def handle(self, *args, **kwargs):
        roles = ["Admin", "Manager", "Viewer"]
        groups = {name: Group.objects.get_or_create(name=name)[0] for name in roles}
        content_type = ContentType.objects.get_for_model(Equipment)
        permissions = Permission.objects.filter(content_type=content_type)

        for perm in permissions:
            if perm.codename.startswith("view_"):
                for g in ["Viewer", "Manager", "Admin"]:
                    groups[g].permissions.add(perm)
            if perm.codename.startswith("add_"):
                for g in ["Manager", "Admin"]:
                    groups[g].permissions.add(perm)
            if perm.codename.startswith("change_"):
                for g in ["Manager", "Admin"]:
                    groups[g].permissions.add(perm)
            if perm.codename.startswith("delete_"):
                groups["Admin"].permissions.add(perm)

        self.stdout.write(self.style.SUCCESS("роли успешно созданы"))


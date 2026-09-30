from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from movies.models import Movie


class Command(BaseCommand):
    help = 'Crea el superusuario, el grupo «editores» y un usuario editor de prueba.'

    def handle(self, *args, **options):
        # 1) Superusuario
        admin_user, created = User.objects.get_or_create(
            username="admin", defaults={"email": "admin@lab07.com"},
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        if created:
            admin_user.set_password("AdminLab07#2026")
        admin_user.save()

        # 2) Grupo «editores»: añadir/cambiar películas, sin permiso de borrado
        group, _ = Group.objects.get_or_create(name="editores")
        ct = ContentType.objects.get_for_model(Movie)
        for codename in ("add_movie", "change_movie", "view_movie"):
            group.permissions.add(
                Permission.objects.get(content_type=ct, codename=codename)
            )

        # 3) Usuario dentro del grupo
        editor, created = User.objects.get_or_create(
            username="editor", defaults={"email": "editor@lab07.com"},
        )
        editor.is_staff = True
        editor.is_superuser = False
        if created:
            editor.set_password("EditorLab07#2026")
        editor.groups.add(group)
        editor.save()

        self.stdout.write(self.style.SUCCESS(
            'Usuarios listos: superusuario «admin» y editor «editor» '
            'dentro del grupo «editores».'
        ))

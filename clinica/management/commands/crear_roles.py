from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = "Crea los grupos de roles (Veterinario y Recepcion) y asigna sus permisos."

    def handle(self, *args, **options):
        grupo_vet, _ = Group.objects.get_or_create(name='Veterinario')
        codigos_vet = [
            'view_tutor', 'view_mascota', 'view_veterinario',
            'view_citamedica', 'add_citamedica', 'change_citamedica',
            'view_fichaclinica', 'add_fichaclinica', 'change_fichaclinica',
            'view_recordatoriopreventivo', 'add_recordatoriopreventivo', 'change_recordatoriopreventivo',
        ]
        grupo_vet.permissions.set(Permission.objects.filter(content_type__app_label='clinica', codename__in=codigos_vet))

        grupo_rec, _ = Group.objects.get_or_create(name='Recepcion')
        codigos_rec = [
            'view_tutor', 'add_tutor', 'change_tutor', 'delete_tutor',
            'view_mascota', 'add_mascota', 'change_mascota', 'delete_mascota',
            'view_veterinario',
            'view_citamedica', 'add_citamedica', 'change_citamedica', 'delete_citamedica',
            'view_recordatoriopreventivo', 'add_recordatoriopreventivo', 'change_recordatoriopreventivo',
        ]
        grupo_rec.permissions.set(Permission.objects.filter(content_type__app_label='clinica', codename__in=codigos_rec))

        self.stdout.write(self.style.SUCCESS("Roles 'Veterinario' y 'Recepcion' configurados exitosamente."))
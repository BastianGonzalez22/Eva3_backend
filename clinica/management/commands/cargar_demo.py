from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import date, timedelta
from clinica.models import Tutor, Mascota, Veterinario, CitaMedica, FichaClinica, RecordatorioPreventivo

class Command(BaseCommand):
    help = "Carga usuarios iniciales y datos demo con RUTs válidos Módulo 11."

    def handle(self, *args, **options):
        call_command('crear_roles')

        admin_user, _ = User.objects.get_or_create(username='admin', defaults={'first_name': 'Admin', 'is_staff': True, 'is_superuser': True})
        admin_user.set_password('Admin2026!')
        admin_user.save()

        vet_user, _ = User.objects.get_or_create(username='veterinario', defaults={'first_name': 'Dra. Camila'})
        vet_user.set_password('Vet2026!')
        vet_user.save()
        vet_user.groups.set([Group.objects.get(name='Veterinario')])

        rec_user, _ = User.objects.get_or_create(username='recepcion', defaults={'first_name': 'Recepción'})
        rec_user.set_password('Rec2026!')
        rec_user.save()
        rec_user.groups.set([Group.objects.get(name='Recepcion')])

        t1, _ = Tutor.objects.get_or_create(rut='11111111-1', defaults={'nombre_completo': 'Carlos Morales', 'telefono': '+56987654321', 'email': 'c@email.cl', 'direccion': 'Temuco'})
        t2, _ = Tutor.objects.get_or_create(rut='22222222-2', defaults={'nombre_completo': 'Valentina Herrera', 'telefono': '+56912345678', 'email': 'v@email.cl', 'direccion': 'Temuco'})

        m1, _ = Mascota.objects.get_or_create(nombre='Thor', tutor=t1, defaults={'especie': 'CANINO', 'raza': 'Pastor', 'sexo': 'M', 'fecha_nacimiento': date(2022, 5, 14), 'peso_kg': 28.5})
        m2, _ = Mascota.objects.get_or_create(nombre='Bangi', tutor=t2, defaults={'especie': 'FELINO', 'raza': 'Común', 'sexo': 'H', 'fecha_nacimiento': date(2023, 8, 20), 'peso_kg': 4.2})

        v1, _ = Veterinario.objects.get_or_create(rut='12345678-5', defaults={'nombre_completo': 'Camila Soto', 'especialidad': 'General', 'email': 'soto@petcare.cl', 'telefono': '+56955551111', 'activo': True})
        v2, _ = Veterinario.objects.get_or_create(rut='15432198-5', defaults={'nombre_completo': 'Javier Méndez', 'especialidad': 'Cirugía', 'email': 'mendez@petcare.cl', 'telefono': '+56955552222', 'activo': True})

        hoy = timezone.now().date()
        CitaMedica.objects.get_or_create(veterinario=v1, fecha=hoy, bloque_horario='10:00', defaults={'mascota': m1, 'motivo': 'Control anual', 'estado': 'PROGRAMADA'})

        if not FichaClinica.objects.filter(mascota=m2).exists():
            FichaClinica.objects.create(
                mascota=m2, veterinario=v1,
                anamnesis='Control sano.', diagnostico='Sana.', tratamiento='Ninguno.',
                requiere_vacuna_control=True, nombre_control_futuro='Vacuna Anual'
            )

        RecordatorioPreventivo.objects.get_or_create(mascota=m1, tipo='DESPARASITACION', descripcion='Antiparasitario', defaults={'fecha_programada': hoy - timedelta(days=2), 'estado': 'PENDIENTE'})

        self.stdout.write(self.style.SUCCESS("Base de datos poblada correctamente con usuarios y datos demo."))
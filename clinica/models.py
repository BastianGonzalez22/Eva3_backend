import re
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

# Validador oficial del dígito verificador del RUT Chileno (Algoritmo Módulo 11)
def validar_rut_chileno(valor):
    if not valor:
        raise ValidationError("El RUT es obligatorio.")
    limpio = re.sub(r'[^0-9kK]', '', str(valor)).upper()
    if len(limpio) < 8 or len(limpio) > 9:
        raise ValidationError("El RUT ingresado no es válido.")
    
    cuerpo, dv_ingresado = limpio[:-1], limpio[-1]
    if not cuerpo.isdigit():
        raise ValidationError("El cuerpo del RUT solo puede contener números.")

    suma = 0
    multiplo = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1
    
    resto = 11 - (suma % 11)
    dv_esperado = '0' if resto == 11 else ('K' if resto == 10 else str(resto))

    if dv_ingresado != dv_esperado:
        raise ValidationError(f"RUT inválido (el dígito verificador correcto es -{dv_esperado}).")

def formatear_rut(valor):
    limpio = re.sub(r'[^0-9kK]', '', str(valor)).upper()
    return f"{limpio[:-1]}-{limpio[-1]}" if len(limpio) >= 2 else valor


class Tutor(models.Model):
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut_chileno], verbose_name="RUT")
    nombre_completo = models.CharField(max_length=150, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo Electrónico")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tutor"
        verbose_name_plural = "Tutores"
        ordering = ['nombre_completo']

    def clean(self):
        if self.rut:
            validar_rut_chileno(self.rut)
            self.rut = formatear_rut(self.rut)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"


class Mascota(models.Model):
    ESPECIES = [
        ('CANINO', 'Canino (Perro)'),
        ('FELINO', 'Felino (Gato)'),
        ('AVE', 'Ave'),
        ('EXOTICO', 'Exótico'),
    ]
    SEXO_CHOICES = [('M', 'Macho'), ('H', 'Hembra')]

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='mascotas', verbose_name="Tutor Responsable")
    nombre = models.CharField(max_length=100, verbose_name="Nombre de la Mascota")
    especie = models.CharField(max_length=20, choices=ESPECIES, default='CANINO')
    raza = models.CharField(max_length=100, verbose_name="Raza")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='M')
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento")
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso (Kg)")

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
        ordering = ['nombre']

    def clean(self):
        if self.fecha_nacimiento and self.fecha_nacimiento > timezone.now().date():
            raise ValidationError({'fecha_nacimiento': "La fecha de nacimiento no puede ser futura."})
        if self.peso_kg is not None and self.peso_kg <= 0:
            raise ValidationError({'peso_kg': "El peso debe ser mayor a 0."})

    def __str__(self):
        return f"{self.nombre} - {self.get_especie_display()} (Tutor: {self.tutor.nombre_completo})"


class Veterinario(models.Model):
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut_chileno], verbose_name="RUT")
    nombre_completo = models.CharField(max_length=150, verbose_name="Nombre del Profesional")
    especialidad = models.CharField(max_length=100, verbose_name="Especialidad Médica")
    email = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    activo = models.BooleanField(default=True, verbose_name="Disponible para Agenda")

    class Meta:
        verbose_name = "Veterinario"
        verbose_name_plural = "Veterinarios"
        ordering = ['nombre_completo']

    def clean(self):
        if self.rut:
            validar_rut_chileno(self.rut)
            self.rut = formatear_rut(self.rut)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dr(a). {self.nombre_completo} ({self.especialidad})"

class HorarioProfesional(models.Model):
    DIAS = [
        (0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), (3, 'Jueves'),
        (4, 'Viernes'), (5, 'Sábado'), (6, 'Domingo'),
    ]
    veterinario = models.ForeignKey(Veterinario, on_delete=models.CASCADE, related_name='horarios', verbose_name="Veterinario")
    dia_semana = models.PositiveSmallIntegerField(choices=DIAS, verbose_name="Día de la Semana")
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Término")

    class Meta:
        verbose_name = "Horario de Atención"
        verbose_name_plural = "Horarios de Atención"
        ordering = ['veterinario', 'dia_semana', 'hora_inicio']

    def clean(self):
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError("La hora de término debe ser posterior a la hora de inicio.")

    def __str__(self):
        return f"{self.veterinario.nombre_completo}: {self.get_dia_semana_display()} {self.hora_inicio:%H:%M}-{self.hora_fin:%H:%M}"


def bloque_en_horario(veterinario_id, fecha, bloque):
    """True si el veterinario atiende ese día y el bloque cae dentro de alguno de sus horarios."""
    from datetime import datetime
    hora = datetime.strptime(bloque, '%H:%M').time()
    return HorarioProfesional.objects.filter(
        veterinario_id=veterinario_id,
        dia_semana=fecha.weekday(),
        hora_inicio__lte=hora,
        hora_fin__gt=hora,
    ).exists()


class CitaMedica(models.Model):
    ESTADOS = [
        ('PROGRAMADA', 'Programada'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    BLOQUES_HORARIOS = [
        ('09:00', '09:00 - 09:45'),
        ('10:00', '10:00 - 10:45'),
        ('11:00', '11:00 - 11:45'),
        ('12:00', '12:00 - 12:45'),
        ('15:00', '15:00 - 15:45'),
        ('16:00', '16:00 - 16:45'),
        ('17:00', '17:00 - 17:45'),
    ]
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='citas')
    veterinario = models.ForeignKey(Veterinario, on_delete=models.CASCADE, related_name='citas')
    fecha = models.DateField(verbose_name="Fecha de la Cita")
    bloque_horario = models.CharField(max_length=5, choices=BLOQUES_HORARIOS, verbose_name="Bloque Horario")
    motivo = models.CharField(max_length=255, verbose_name="Motivo de Consulta")
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PROGRAMADA')
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"
        ordering = ['-fecha', 'bloque_horario']

    def clean(self):
        if not self.veterinario_id:
            return
        if not self.veterinario.activo:
            raise ValidationError("El profesional seleccionado no se encuentra activo para agendar citas.")

        if self.estado != 'CANCELADA':
            # No permitir agendar en el pasado (solo al crear o al cambiar fecha/bloque)
            cambio = True
            if self.pk:
                orig = CitaMedica.objects.filter(pk=self.pk).values('fecha', 'bloque_horario').first()
                cambio = orig is None or orig['fecha'] != self.fecha or orig['bloque_horario'] != self.bloque_horario
            if cambio and self.fecha and self.fecha < timezone.now().date():
                raise ValidationError("No se puede agendar una cita en una fecha pasada.")
            if cambio and self.fecha and self.bloque_horario and not bloque_en_horario(self.veterinario_id, self.fecha, self.bloque_horario):
                raise ValidationError(
                    f"El Dr(a). {self.veterinario.nombre_completo} no atiende ese día u horario. Revise su disponibilidad."
                )

            solapamiento = CitaMedica.objects.filter(
                veterinario_id=self.veterinario_id,
                fecha=self.fecha,
                bloque_horario=self.bloque_horario
            ).exclude(estado='CANCELADA').exclude(pk=self.pk)

            if solapamiento.exists():
                raise ValidationError(
                    f"Conflicto de agenda: El Dr(a). {self.veterinario.nombre_completo} ya tiene cita el {self.fecha} a las {self.bloque_horario}."
                )
            
            # Una mascota no puede tener dos citas activas en la misma fecha y bloque (aunque sea con otro veterinario)
            if self.mascota_id:
                mascota_ocupada = CitaMedica.objects.filter(
                    mascota_id=self.mascota_id,
                    fecha=self.fecha,
                    bloque_horario=self.bloque_horario
                ).exclude(estado='CANCELADA').exclude(pk=self.pk)

                if mascota_ocupada.exists():
                    raise ValidationError(
                        f"La mascota {self.mascota.nombre} ya tiene una cita el {self.fecha} a las {self.bloque_horario}."
                    )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.fecha} {self.bloque_horario} | {self.mascota.nombre} con {self.veterinario.nombre_completo}"


class FichaClinica(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='fichas_clinicas')
    veterinario = models.ForeignKey(Veterinario, on_delete=models.SET_NULL, null=True, related_name='fichas_emitidas')
    cita = models.OneToOneField(CitaMedica, on_delete=models.SET_NULL, null=True, blank=True, related_name='ficha_clinica')
    fecha_atencion = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Atención")
    anamnesis = models.TextField(verbose_name="Anamnesis / Síntomas")
    diagnostico = models.TextField(verbose_name="Diagnóstico Clínico")
    tratamiento = models.TextField(verbose_name="Tratamiento Indicado")
    receta_medica = models.TextField(blank=True, verbose_name="Receta Médica")
    examenes_solicitados = models.TextField(blank=True, verbose_name="Exámenes Solicitados / Resultados")
    requiere_vacuna_control = models.BooleanField(default=False, verbose_name="Generar Recordatorio Automático a 30 días")
    nombre_control_futuro = models.CharField(max_length=150, blank=True, verbose_name="Detalle de Próxima Vacuna/Control")

    class Meta:
        verbose_name = "Ficha Clínica"
        verbose_name_plural = "Fichas Clínicas"
        ordering = ['-fecha_atencion']

    def clean(self):
        if self.cita_id and self.mascota_id and self.cita.mascota_id != self.mascota_id:
            raise ValidationError("La cita seleccionada pertenece a otra mascota.")

    def save(self, *args, **kwargs):
        es_nueva = self.pk is None
        super().save(*args, **kwargs)
        if self.cita and self.cita.estado == 'PROGRAMADA':
            self.cita.estado = 'COMPLETADA'
            self.cita.save()
        if es_nueva and self.requiere_vacuna_control:
            RecordatorioPreventivo.objects.create(
                mascota=self.mascota,
                tipo='VACUNA',
                descripcion=self.nombre_control_futuro or f"Control post-atención: {self.diagnostico[:40]}",
                fecha_programada=timezone.now().date() + timedelta(days=30),
                estado='PENDIENTE'
            )

    def __str__(self):
        return f"Ficha #{self.id} - {self.mascota.nombre} ({self.fecha_atencion.strftime('%d/%m/%Y')})"


class RecordatorioPreventivo(models.Model):
    TIPOS = [
        ('VACUNA', 'Vacunación'),
        ('DESPARASITACION', 'Desparasitación'),
        ('CONTROL', 'Control Periódico'),
    ]
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('NOTIFICADO', 'Notificado al Tutor'),
        ('REALIZADO', 'Aplicado / Realizado'),
    ]
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='recordatorios')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='VACUNA')
    descripcion = models.CharField(max_length=200, verbose_name="Vacuna o Control")
    fecha_programada = models.DateField(verbose_name="Fecha Programada")
    estado = models.CharField(max_length=15, choices=ESTADOS, default='PENDIENTE')
    observaciones = models.TextField(blank=True, verbose_name="Notas Adicionales")

    class Meta:
        verbose_name = "Recordatorio Preventivo"
        verbose_name_plural = "Recordatorios Preventivos"
        ordering = ['fecha_programada']

    @property
    def nivel_alerta(self):
        hoy = timezone.now().date()
        if self.estado == 'REALIZADO':
            return 'COMPLETADO'
        if self.fecha_programada < hoy:
            return 'ATRASADO'
        elif self.fecha_programada <= hoy + timedelta(days=7):
            return 'PROXIMO'
        return 'AL_DIA'

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.descripcion} - {self.mascota.nombre} ({self.fecha_programada})"
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Tutor, Mascota, Veterinario, CitaMedica, FichaClinica, RecordatorioPreventivo

# Serializador de Tutores con conteo de mascotas asociadas
class TutorSerializer(serializers.ModelSerializer):
    total_mascotas = serializers.IntegerField(source='mascotas.count', read_only=True)

    class Meta:
        model = Tutor
        fields = '__all__'


# Serializador de Mascotas incluyendo datos de lectura del Tutor
class MascotaSerializer(serializers.ModelSerializer):
    tutor_nombre = serializers.CharField(source='tutor.nombre_completo', read_only=True)
    tutor_rut = serializers.CharField(source='tutor.rut', read_only=True)
    especie_display = serializers.CharField(source='get_especie_display', read_only=True)

    class Meta:
        model = Mascota
        fields = '__all__'


# Serializador de Profesionales Veterinarios
class VeterinarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veterinario
        fields = '__all__'


# Serializador de Citas Médicas: conecta la validación anti-solapamiento del modelo con la API
class CitaMedicaSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    tutor_nombre = serializers.CharField(source='mascota.tutor.nombre_completo', read_only=True)
    veterinario_nombre = serializers.CharField(source='veterinario.nombre_completo', read_only=True)
    bloque_display = serializers.CharField(source='get_bloque_horario_display', read_only=True)

    class Meta:
        model = CitaMedica
        fields = '__all__'

    def validate(self, data):
        instancia = CitaMedica(**data)
        if self.instance:
            instancia.pk = self.instance.pk
        try:
            instancia.clean() # Ejecuta la validación de choques de horario
        except DjangoValidationError as e:
            raise serializers.ValidationError({'detalle_agenda': e.messages})
        return data


# Serializador de Fichas Clínicas con formato de fecha legible
class FichaClinicaSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    tutor_nombre = serializers.CharField(source='mascota.tutor.nombre_completo', read_only=True)
    veterinario_nombre = serializers.CharField(source='veterinario.nombre_completo', read_only=True)
    fecha_formateada = serializers.DateTimeField(source='fecha_atencion', format='%d/%m/%Y %H:%M', read_only=True)

    class Meta:
        model = FichaClinica
        fields = '__all__'


# Serializador de Recordatorios Preventivos incluyendo el nivel de alerta calculado
class RecordatorioPreventivoSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source='mascota.nombre', read_only=True)
    tutor_nombre = serializers.CharField(source='mascota.tutor.nombre_completo', read_only=True)
    tutor_telefono = serializers.CharField(source='mascota.tutor.telefono', read_only=True)
    tutor_email = serializers.CharField(source='mascota.tutor.email', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    nivel_alerta = serializers.ReadOnlyField()

    class Meta:
        model = RecordatorioPreventivo
        fields = '__all__'
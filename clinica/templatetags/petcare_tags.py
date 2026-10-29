from django import template
from django.utils import timezone
from clinica.models import Mascota, CitaMedica, RecordatorioPreventivo

register = template.Library()

@register.simple_tag
def obtener_metricas_admin():
    hoy = timezone.now().date()
    return {
        'citas_hoy': CitaMedica.objects.filter(fecha=hoy, estado='PROGRAMADA').count(),
        'recordatorios_atrasados': RecordatorioPreventivo.objects.filter(
            fecha_programada__lt=hoy
        ).exclude(estado='REALIZADO').count(),
        'total_mascotas': Mascota.objects.count(),
    }
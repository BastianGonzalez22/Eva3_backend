from django.contrib import admin
from django.utils.html import format_html
from .models import Tutor, Mascota, Veterinario, CitaMedica, FichaClinica, RecordatorioPreventivo

# Criterio 2: Personalización de títulos del administrador de Django
admin.site.site_header = "PetCare - Administración Clínica Veterinaria"
admin.site.site_title = "Panel Administrativo PetCare"
admin.site.index_title = "Gestión de Operaciones Clínicas, Agenda y Fichas Médicas"

# Permite ver y agregar mascotas dentro de la misma vista del Tutor
class MascotaInline(admin.TabularInline):
    model = Mascota
    extra = 1

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre_completo', 'telefono', 'email', 'cantidad_mascotas', 'creado_en')
    search_fields = ('rut', 'nombre_completo', 'email', 'telefono')
    list_filter = ('creado_en',)
    inlines = [MascotaInline]

    def cantidad_mascotas(self, obj):
        return obj.mascotas.count()
    cantidad_mascotas.short_description = "N° Mascotas"

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especie', 'raza', 'sexo', 'peso_kg', 'tutor_info')
    list_filter = ('especie', 'sexo')
    search_fields = ('nombre', 'raza', 'tutor__nombre_completo', 'tutor__rut')

    def tutor_info(self, obj):
        return f"{obj.tutor.nombre_completo} ({obj.tutor.telefono})"
    tutor_info.short_description = "Tutor y Contacto"

@admin.register(Veterinario)
class VeterinarioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre_completo', 'especialidad', 'email', 'telefono', 'estado_badge')
    list_filter = ('especialidad', 'activo')
    search_fields = ('rut', 'nombre_completo', 'especialidad')

    # Muestra etiqueta verde o roja según disponibilidad del veterinario
    def estado_badge(self, obj):
        color = "#198754" if obj.activo else "#dc3545"
        texto = "Disponible" if obj.activo else "Inactivo"
        return format_html('<span style="background:{}; color:white; padding:3px 8px; border-radius:10px;">{}</span>', color, texto)
    estado_badge.short_description = "Estado"

@admin.register(CitaMedica)
class CitaMedicaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'bloque_horario', 'mascota', 'veterinario', 'motivo', 'estado_coloreado')
    list_filter = ('estado', 'fecha', 'veterinario', 'bloque_horario')
    search_fields = ('mascota__nombre', 'mascota__tutor__nombre_completo', 'veterinario__nombre_completo', 'motivo')
    date_hierarchy = 'fecha'

    def estado_coloreado(self, obj):
        colores = {'PROGRAMADA': '#0d6efd', 'COMPLETADA': '#198754', 'CANCELADA': '#6c757d'}
        return format_html(
            '<span style="background:{}; color:white; padding:3px 8px; border-radius:8px; font-weight:bold;">{}</span>',
            colores.get(obj.estado, '#000'), obj.get_estado_display()
        )
    estado_coloreado.short_description = "Estado Cita"

@admin.register(FichaClinica)
class FichaClinicaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_atencion', 'mascota', 'veterinario', 'diagnostico_corto', 'requiere_vacuna_control')
    list_filter = ('fecha_atencion', 'veterinario', 'requiere_vacuna_control')
    search_fields = ('mascota__nombre', 'diagnostico', 'tratamiento', 'receta_medica')
    date_hierarchy = 'fecha_atencion'

    def diagnostico_corto(self, obj):
        return obj.diagnostico[:50] + "..." if len(obj.diagnostico) > 50 else obj.diagnostico
    diagnostico_corto.short_description = "Diagnóstico"

@admin.register(RecordatorioPreventivo)
class RecordatorioPreventivoAdmin(admin.ModelAdmin):
    list_display = ('fecha_programada', 'mascota', 'tutor_contacto', 'tipo', 'descripcion', 'estado', 'alerta_visual')
    list_filter = ('tipo', 'estado', 'fecha_programada')
    search_fields = ('mascota__nombre', 'mascota__tutor__nombre_completo', 'descripcion')
    actions = ['marcar_como_notificado', 'marcar_como_realizado']

    def tutor_contacto(self, obj):
        return f"{obj.mascota.tutor.nombre_completo} ({obj.mascota.tutor.email})"
    tutor_contacto.short_description = "Tutor"

    # Semáforo visual según fecha de vencimiento de la vacuna o control
    def alerta_visual(self, obj):
        alerta = obj.nivel_alerta
        mapa = {
            'ATRASADO': ('#dc3545', 'VENCIDO / ATRASADO'),
            'PROXIMO': ('#ffc107', 'PRÓXIMO (<= 7 días)'),
            'AL_DIA': ('#0dcaf0', 'PROGRAMADO'),
            'COMPLETADO': ('#198754', 'COMPLETADO'),
        }
        color, texto = mapa.get(alerta, ('#6c757d', alerta))
        return format_html('<span style="background:{}; color:#000; padding:3px 8px; border-radius:6px; font-weight:bold;">{}</span>', color, texto)
    alerta_visual.short_description = "Semáforo Preventivo"

    # Acciones masivas para actualizar estados desde el listado
    @admin.action(description="Marcar seleccionados como Notificados al Tutor")
    def marcar_como_notificado(self, request, queryset):
        queryset.update(estado='NOTIFICADO')

    @admin.action(description="Marcar seleccionados como Aplicados/Realizados")
    def marcar_como_realizado(self, request, queryset):
        queryset.update(estado='REALIZADO')
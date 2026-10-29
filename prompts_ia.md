---

### 11. `prompts_ia.md`
```markdown
# Registro de Apoyo de Herramientas de Inteligencia Artificial (`prompts_ia.md`)

* **Estudiante:** Bastián Marcelo González Moya
* **Asignatura:** Desarrollo Backend - Evaluación Parcial N°3
* **Proyecto:** Proyecto 1 - Sistema de Gestión de Citas y Fichas Médicas para Veterinaria (PetCare)

---

## 1. Modelado de Datos, Regla Anti-Solapamiento y Validación de RUT
* **Consulta realizada:** *"Diseñar los modelos en Django para el caso PetCare (Tutor, Mascota, Veterinario, CitaMedica, FichaClinica y RecordatorioPreventivo) conectados a PostgreSQL, incluyendo validación de RUT chileno con algoritmo Módulo 11 y bloqueo de solapamiento de horarios por médico."*
* **Apoyo recibido:** Estructura de los 6 modelos del dominio, función `validar_rut_chileno` con cálculo Módulo 11, validación en el método `clean()` de `CitaMedica` y creación automática de recordatorio a 30 días en `FichaClinica.save()`.
* **Qué verifiqué yo:** Comprobé la creación de las tablas en PostgreSQL mediante `pgAdmin 4`, probé el rechazo de RUTs con dígito verificador incorrecto y verifiqué que el sistema impida agendar dos citas al mismo médico en la misma fecha y bloque horario.

---

## 2. Seguridad por Roles, Sesiones y Permisos en Django REST Framework
* **Consulta realizada:** *"Implementar roles Veterinario y Recepción con grupos de Django, aplicando permisos tanto en las vistas web como en los ViewSets de la API REST, ocultando enlaces del menú según el rol y cambiando el cierre de sesión a petición POST con CSRF."*
* **Apoyo recibido:** Clase `StrictDjangoModelPermissions` que exige el permiso `view_` en peticiones `GET`, comando `crear_roles`, decoradores `@permission_required` en `clinica/views.py`, directivas `{% if perms.clinica... %}` en `base.html` y formulario `POST` para `/logout/`.
* **Qué verifiqué yo:** Inicié sesión con la cuenta `recepcion` (`Rec2026!`) y comprobé que no aparece el módulo de Fichas Clínicas en el menú lateral y que al intentar entrar por URL a `/fichas/` o `/api/fichas/` el servidor bloquea el acceso con código `403 Forbidden`.

---

## 3. Personalización del Django Admin con Templates y Enmascaramiento Asíncrono
* **Consulta realizada:** *"Personalizar el panel de Django Admin con templates propios (base_site.html e index.html) que muestren tarjetas de resumen calculadas con un template tag, y construir las vistas frontend consumiendo la API con Fetch."*
* **Apoyo recibido:** Creación del template tag `obtener_metricas_admin` en `clinica/templatetags/petcare_tags.py`, plantillas `templates/admin/base_site.html` y `templates/admin/index.html`, y grilla dinámica de disponibilidad horaria en `agenda.html`.
* **Qué verifiqué yo:** Verifiqué que el panel `/admin/` muestre en la parte superior las tarjetas con las citas programadas del día, recordatorios atrasados y total de mascotas, manteniendo los estilos activos con `WhiteNoise`.

---

## 4. Revisión técnica y corrección de errores (Claude)
* **Consulta realizada:** *"Revisa mi proyecto contra la rúbrica de la EVA 3 y dime qué falta."*
* **Apoyo recibido:** Revisión del código con una lista de pendientes por criterio. Detectó que `cargar_demo` fallaba por un RUT con dígito verificador incorrecto y que los `permission_classes = [IsAuthenticated]` de cada ViewSet anulaban los permisos por rol de la API.
* **Qué verifiqué yo:** Corregí el RUT del demo, eliminé las líneas `permission_classes` de `views.py` y comprobé con la cuenta `recepcion` que `/api/fichas/` responde 403.

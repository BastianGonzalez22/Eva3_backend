# PetCare - Sistema de Gestión de Citas y Fichas Médicas para Veterinaria

* **Estudiante:** Bastián Marcelo González Moya (`bastian.gonzalez84@inacapmail.cl`)
* **Asignatura:** Desarrollo Backend - Evaluación Parcial N°3
* **Docente:** Marcelo Alvarado Aravena
* **Proyecto Asignado:** Proyecto 1 - Clínica Veterinaria PetCare

---

## Acceso en Vivo - Instancia AWS EC2
> **IP Pública / DNS AWS EC2:** `http://<COLOCAR_IP_PUBLICA_EC2_AQUI>:8000/`
* **Aplicación Web Principal:** `http://<COLOCAR_IP_PUBLICA_EC2_AQUI>:8000/`
* **Panel Administrativo (Django Admin):** `http://<COLOCAR_IP_PUBLICA_EC2_AQUI>:8000/admin/`
* **API REST (Django REST Framework):** `http://<COLOCAR_IP_PUBLICA_EC2_AQUI>:8000/api/`

---

## Descripción del Sistema y Arquitectura Frontend
El sistema **PetCare** centraliza la operación de la clínica veterinaria resolviendo el solapamiento de citas, la pérdida de fichas médicas en papel y la falta de seguimiento de esquemas de vacunación.

El frontend está construido mediante **enmascaramiento asíncrono que consume la API** de Django REST Framework (`fetch` + `X-CSRFToken` sobre sesiones autenticadas), organizado en vistas modulares con herencia de plantillas (`base.html`).

---

## Roles, Usuarios y Permisos de Seguridad
El registro público se encuentra deshabilitado por seguridad. Los accesos se controlan mediante grupos de Django y `StrictDjangoModelPermissions` tanto en las vistas web (`@permission_required`) como en los 6 `ModelViewSet` de la API:

| Rol | Usuario Demo | Contraseña | Permisos Asignados |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `Admin2026!` | Superusuario con acceso total a la plataforma y al panel Django Admin. |
| **Veterinario** | `veterinario` | `Vet2026!` | Visualiza pacientes/tutores y gestiona citas, fichas médicas clínicas y recordatorios. |
| **Recepción** | `recepcion` | `Rec2026!` | Gestiona tutores, mascotas, citas y recordatorios. **No tiene permiso para ver ni editar fichas clínicas** (enlace oculto en menú y bloqueo `403` en vista y API). |

---

## Reglas de Negocio Implementadas
1. **Validación de RUT Chileno (Módulo 11):** Validación matemática del dígito verificador y normalización de formato en `Tutor` y `Veterinario` tanto a nivel de modelo como en serializadores DRF.
2. **Control Anti-Solapamiento Horario:** Un veterinario no puede tener dos citas activas en la misma fecha y bloque horario, validando además que el profesional se encuentre activo.
3. **Automatización de Recordatorios y Cierre de Cita:** Al emitir una `FichaClinica`, la cita vinculada pasa automáticamente a estado `COMPLETADA` y, si se indica control futuro, se crea automáticamente un `RecordatorioPreventivo` a 30 días.

---

## Instrucciones de Ejecución Local con PostgreSQL
1. Clonar el repositorio y crear el entorno virtual:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
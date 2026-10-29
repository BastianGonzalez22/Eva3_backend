from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tutor, Mascota, Veterinario, CitaMedica, FichaClinica, RecordatorioPreventivo
from .serializers import (
    TutorSerializer, MascotaSerializer, VeterinarioSerializer,
    CitaMedicaSerializer, FichaClinicaSerializer, RecordatorioPreventivoSerializer
)
from .permissions import StrictDjangoModelPermissions

# --- AUTENTICACIÓN Y CIERRE DE SESIÓN POR POST ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario, password=clave)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            error = "Credenciales inválidas. Verifique su usuario y contraseña."
    return render(request, 'login.html', {'error': error})

@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')


# --- VISTAS WEB PROTEGIDAS CON PERMISSION_REQUIRED SEGÚN EL ROL ---

@login_required
def inicio_view(request):
    return render(request, 'inicio.html', {'menu': 'inicio', 'titulo': 'Resumen Operativo de la Clínica'})

@login_required
@permission_required('clinica.view_tutor', raise_exception=True)
def tutores_view(request):
    return render(request, 'tutores.html', {'menu': 'tutores', 'titulo': 'Directorio y Administración de Tutores'})

@login_required
@permission_required('clinica.view_mascota', raise_exception=True)
def mascotas_view(request):
    return render(request, 'mascotas.html', {'menu': 'mascotas', 'titulo': 'Registro Clínico de Mascotas (Pacientes)'})

@login_required
@permission_required('clinica.view_veterinario', raise_exception=True)
def veterinarios_view(request):
    return render(request, 'veterinarios.html', {'menu': 'veterinarios', 'titulo': 'Equipo Médico Veterinario y Disponibilidad'})

@login_required
@permission_required('clinica.view_citamedica', raise_exception=True)
def agenda_view(request):
    return render(request, 'agenda.html', {'menu': 'agenda', 'titulo': 'Calendario Veterinario Dinámico y Disponibilidad'})

@login_required
@permission_required('clinica.view_fichaclinica', raise_exception=True)
def fichas_view(request):
    return render(request, 'fichas.html', {'menu': 'fichas', 'titulo': 'Historial de Fichas Médicas Clínicas y Recetas'})

@login_required
@permission_required('clinica.view_recordatoriopreventivo', raise_exception=True)
def recordatorios_view(request):
    return render(request, 'recordatorios.html', {'menu': 'recordatorios', 'titulo': 'Módulo de Vacunación y Controles Preventivos'})


# --- VIEWSETS DE LA API REST CON PERMISOS DE MODELO POR ROL ---

class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.all()
    serializer_class = TutorSerializer
    permission_classes = [StrictDjangoModelPermissions]


class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.select_related('tutor').all()
    serializer_class = MascotaSerializer
    permission_classes = [StrictDjangoModelPermissions]


class VeterinarioViewSet(viewsets.ModelViewSet):
    queryset = Veterinario.objects.all()
    serializer_class = VeterinarioSerializer
    permission_classes = [StrictDjangoModelPermissions]


class CitaMedicaViewSet(viewsets.ModelViewSet):
    queryset = CitaMedica.objects.select_related('mascota', 'mascota__tutor', 'veterinario').all()
    serializer_class = CitaMedicaSerializer
    permission_classes = [StrictDjangoModelPermissions]

    @action(detail=False, methods=['get'])
    def disponibilidad(self, request):
        vet_id = request.query_params.get('veterinario_id')
        fecha = request.query_params.get('fecha')
        if not vet_id or not fecha:
            return Response({'error': 'Debe indicar veterinario_id y fecha'}, status=status.HTTP_400_BAD_REQUEST)

        ocupados = CitaMedica.objects.filter(
            veterinario_id=vet_id,
            fecha=fecha
        ).exclude(estado='CANCELADA').values_list('bloque_horario', flat=True)

        bloques = [
            {'codigo': codigo, 'etiqueta': etiqueta, 'disponible': codigo not in ocupados}
            for codigo, etiqueta in CitaMedica.BLOQUES_HORARIOS
        ]
        return Response(bloques)


class FichaClinicaViewSet(viewsets.ModelViewSet):
    queryset = FichaClinica.objects.select_related('mascota', 'mascota__tutor', 'veterinario').all()
    serializer_class = FichaClinicaSerializer
    permission_classes = [StrictDjangoModelPermissions]


class RecordatorioPreventivoViewSet(viewsets.ModelViewSet):
    queryset = RecordatorioPreventivo.objects.select_related('mascota', 'mascota__tutor').all()
    serializer_class = RecordatorioPreventivoSerializer
    permission_classes = [StrictDjangoModelPermissions]
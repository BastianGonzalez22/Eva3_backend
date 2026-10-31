from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from clinica.views import (
    login_view, logout_view,
    inicio_view, tutores_view, mascotas_view, veterinarios_view,
    agenda_view, fichas_view, recordatorios_view,
    TutorViewSet, MascotaViewSet, VeterinarioViewSet,
    CitaMedicaViewSet, FichaClinicaViewSet, RecordatorioPreventivoViewSet
)

# Configuración de la documentación Swagger
schema_view = get_schema_view(
   openapi.Info(
      title="PetCare API",
      default_version='v1',
      description="Documentación interactiva de la API de PetCare",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'tutores', TutorViewSet)
router.register(r'mascotas', MascotaViewSet)
router.register(r'veterinarios', VeterinarioViewSet)
router.register(r'citas', CitaMedicaViewSet)
router.register(r'fichas', FichaClinicaViewSet)
router.register(r'recordatorios', RecordatorioPreventivoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Vistas separadas por sección
    path('', inicio_view, name='inicio'),
    path('tutores/', tutores_view, name='tutores'),
    path('mascotas/', mascotas_view, name='mascotas'),
    path('veterinarios/', veterinarios_view, name='veterinarios'),
    path('agenda/', agenda_view, name='agenda'),
    path('fichas/', fichas_view, name='fichas'),
    path('recordatorios/', recordatorios_view, name='recordatorios'),

    # Endpoints de la API REST (DRF)
    path('api/', include(router.urls)),

    # Ruta para la interfaz visual de Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
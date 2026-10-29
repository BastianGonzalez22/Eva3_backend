from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from clinica.views import (
    login_view, logout_view,
    inicio_view, tutores_view, mascotas_view, veterinarios_view,
    agenda_view, fichas_view, recordatorios_view,
    TutorViewSet, MascotaViewSet, VeterinarioViewSet,
    CitaMedicaViewSet, FichaClinicaViewSet, RecordatorioPreventivoViewSet
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
    
    # Vistas separadas por sección (sin ruta /registro/)
    path('', inicio_view, name='inicio'),
    path('tutores/', tutores_view, name='tutores'),
    path('mascotas/', mascotas_view, name='mascotas'),
    path('veterinarios/', veterinarios_view, name='veterinarios'),
    path('agenda/', agenda_view, name='agenda'),
    path('fichas/', fichas_view, name='fichas'),
    path('recordatorios/', recordatorios_view, name='recordatorios'),

    # Endpoints de la API REST (DRF)
    path('api/', include(router.urls)),
]
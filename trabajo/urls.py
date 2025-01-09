from django.contrib import admin
from django.urls import path
from main import views
#Imagenes
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.inicio),
    path('populate/', views.populate),
    path('brawlers/', views.lista_brawlers),
    path('clases/', views.lista_clases),
    path('brawlers/brawler/<str:nombre_brawler>/', views.detalle_brawler),
    path('rarezas/', views.lista_rarezas),
    path('poderes/', views.lista_poderes),
    path('gadgets/', views.lista_gadgets),
    path('admin/',admin.site.urls),
#Whoosh
    path('buscar_brawler_nombre/', views.buscar_brawler_nombre, name='buscar_brawler_nombre'),
#SR
    path('filtro_avanzado/', views.filtro_avanzado, name='filtro_avanzado'),
    path('comparar_brawlers/', views.comparar_brawlers, name='comparar_brawlers'),

    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

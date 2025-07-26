from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexView, name='index'),
    path('statistical-analysis/<str:fileName>/', views.runStatisticalView, name='statisticalAnalysis'),
    path('proyeccion-3d/', views.runProyeccion3DView, name='proyeccion3D'),
    path('sample-data/', views.sampleDataView, name='sampleData'),
    path('visualizacion-3d/', views.dataFile3DView, name='dataFile3D'),
]
from django.urls import path
from . import views

urlpatterns = [
   path('', views.home, name='home'),
   path('salva_modifiche/', views.calcola_somma, name='salva_modifiche'),
   path('genera-report/', views.generate_preview_with_text_overlay, name='genera_report'),
  path('download-pdf/', views.download_pdf_with_text_overlay, name='download_pdf'),
]
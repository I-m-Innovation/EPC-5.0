from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('download-pdf/', views.download_pdf_with_text_overlay, name='download_pdf_with_text_overlay'),
]
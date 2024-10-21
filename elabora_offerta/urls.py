from django.urls import path

urlpatterns = [
    path("", views.index),
    path("download-pdf", views.download_pdf)
]
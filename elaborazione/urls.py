from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('', views.salva_modifiche, name='salva_modifiche'),
    # path('', views.aggiungi_rata, name='aggiungi_rata'),
]

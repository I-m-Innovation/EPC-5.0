from django.shortcuts import render
from .functions import pdf_editor
from django.http import FileResponse


# Create your views here.

def index(request):
    # la view deve gestire la richiesta descritta in index.html:
    # copia il template, lo rinomina e lo apre in un nuovo tab
    # tramite API di google: https://developers.google.com/drive/api/quickstart/python?hl=it
    pass

def download_pdf(request):
    # questa funzione dovrà essere chiamata dall'url '/download-pdf' per
    #   1. preparare il file pdf
    pdf = pdf_editor()
    
    #   2. servirlo al client che lo ha chiesto
    response = FileResponse(open(file_name, 'rb'), as_attachment=True, filename=file_name)

    # suggerimento: prova a vedere FilResponse di Django
    pass

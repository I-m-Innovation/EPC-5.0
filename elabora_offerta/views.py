from django.shortcuts import render
from .functions import pdf_editor


# Create your views here.

def index(request):
    # la view deve gestire la richiesta descritta in index.html
    pass

def download_pdf(request):
    # questa funzione dovrà essere chiamata dall'url '/download-pdf' per
    #   1. preparare il file pdf

    pdf = pdf_editor()
    #   2. servirlo al client che lo ha chiesto
    pass

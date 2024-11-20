from django.shortcuts import render, redirect
from django.views import View
from .forms import InserisciCliente
from slugify import slugify
from .models import Offerta
import pandas as pd
import platform
from django.contrib.auth import authenticate, login, logout
from datetime import datetime

os_platform = platform.system()
pdfkit_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf"

if os_platform == "Linux":
    pdfkit_path = "/usr/bin/wkhtmltopdf"
elif os_platform == "Darwin":
    pdfkit_path = "/usr/local/bin/wkhtmltopdf"

url = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"


def logout_view(request):
    logout(request)
    return redirect('login') # Replace 'login' with the name of your login page URL


def login_view(request):
    if request.method == 'POST':
        try:
            url = 'offerte'
        except Exception as err:
            url = 'offerte'

        if request.POST['username']:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(url)  # Replace 'home' with the name of your home page URL
            else:
                return render(request, 'registration/login.html', {'error': 'Invalid credentials.'})
        else:
            print("else")
            return redirect(url)
    else:
        try:
            url = request.GET['url']
        except Exception as err:
            url=''
            # print(url)
        data = {"url": url}

        return render(request, 'registration/login.html', data)


def pulsanti(request, slug):
    offerta = Offerta.objects.get(slug=slug)
    offerta.consumi_cliente = request.POST.get('consumi_annui_cliente')
    data = {}

    return redirect("pulsante")


def calcola_aliquota(risparmio_energetico, spesa_totale):
    if risparmio_energetico == 0.05:
        if spesa_totale < 2.5e6:
            aliquota = 0.35
        elif 2.5e6 <= spesa_totale < 10e6:
            aliquota = 0.15
        else:
            aliquota = 0.05

    elif risparmio_energetico == 0.10:
        if spesa_totale < 2.5e6:
            aliquota = 0.40
        elif 2.5e6 <= spesa_totale < 10e6:
            aliquota = 0.10
        else:
            aliquota = 0.05

    else:
        if spesa_totale < 2.5e6:
            aliquota = 0.45
        elif 2.5e6 <= spesa_totale < 10e6:
            aliquota = 0.25
        else:
            aliquota = 0.15

    return aliquota


def calcola_risparmio(produzione_annua_val, perdita, tariffa_energia):
    risparmio = []
    indexes = []
    for i in range(10):
        indexes.append(i + 1)
        if produzione_annua_val != "INSERIRE DATI IMPIANTO":
            # print(produzione_annua_val)
            produzione = float(produzione_annua_val) * pow(1 - perdita, i)
            risparmio.append(produzione * tariffa_energia/1000)
            totale_risparmio = sum(risparmio)
        else:
            produzione = "INSERIRE DATI IMPIANTO"
            risparmio.append(produzione)
            totale_risparmio = "INSERIRE DATI IMPIANTO"

    return risparmio


def leggi_valore(stringa):
    stringa = stringa.replace("€","").replace("kWh", "").replace("kW", "").replace("/p", "").replace(" ", "")

    if "," in stringa and "." in stringa:
        valore = float(stringa.replace(".", "").replace(",", ".")) if stringa.replace(".", "").replace(",", ".")!=''  else 0
    else:
        valore = float(stringa.replace(",", ".")) if stringa.replace(".", "").replace(",", ".")!=''  else 0
    return valore


def salva_modifiche(request):
    risparmi_bolletta = None
    slug = request.META["HTTP_REFERER"].replace('http://localhost:8000/offerte/','')
    offerta = Offerta.objects.get(slug=slug)
    offerta.date = datetime.now()
    consumi_cliente = request.POST['consumi_annui_cliente'].replace("kWh", "").replace(".", "").replace(",", ".")
    # print(request.POST['consumi_annui_cliente'])
    offerta.consumi_cliente = leggi_valore(request.POST['consumi_annui_cliente']) if request.POST[
        'consumi_annui_cliente'] else 0

    offerta.costi_energia_cliente = leggi_valore(request.POST['costi_energia_cliente']) if request.POST[
                                                                                               'costi_energia_cliente'] != "" else 0
    # offerta.costi_energia_cliente = float(costi_energia_cliente) if costi_energia_cliente !="" else 0

    offerta.tariffa_energia_cliente = 1000 * offerta.costi_energia_cliente / offerta.consumi_cliente if offerta.consumi_cliente != 0 else 0
    offerta.costo_fv = leggi_valore(request.POST['costo_fv']) if request.POST[
                                                                     'costo_fv'] != "Inserire dato da Ingegneria" and \
                                                                 request.POST['costo_fv'] != "" else 0

    # offerta.costo_fv = float(request.POST['costo_fv'].replace("€", "").replace(",", ".")) if request.POST['costo_fv'] != "Inserire dato da Ingegneria" and request.POST['costo_fv'] != "" else 0
    offerta.costo_storage = leggi_valore(request.POST['costo_storage']) if request.POST[
                                                                               'costo_storage'] != "Inserire dato da Ingegneria" else 0
    offerta.costo_trainante = leggi_valore(request.POST['costo_trainante']) if (
                request.POST['costo_trainante'] != "Inserire dato da Cliente"
                and request.POST['costo_trainante'] != "") else 0

    offerta.costo_totale = offerta.costo_fv + offerta.costo_storage + offerta.costo_trainante
    offerta.potenza_installata = leggi_valore(request.POST['potenza_installata']) if request.POST[
                                                                                         'potenza_installata'] != "Inserire dato da Ingegneria" else 0
    offerta.storage_installato = leggi_valore(request.POST['storage_installato']) if request.POST[
                                                                                         'storage_installato'] != "Inserire dato da Ingegneria" else 0
    offerta.producibilità_specifica = leggi_valore(request.POST['producibilità_specifica']) if request.POST[
        'producibilità_specifica'] else 0
    offerta.produzione_annua = offerta.producibilità_specifica * offerta.potenza_installata if offerta.producibilità_specifica > 0 and offerta.potenza_installata else 0

    offerta.tipologia_moduli = leggi_valore(request.POST['tipologia_moduli'])
    # print(offerta.tipologia_moduli)
    offerta.risparmio_energetico_trainante = leggi_valore(request.POST['risparmio_energetico_trainante']) / 100 if \
    request.POST['risparmio_energetico_trainante'] != "" else 0

    offerta.aliquota = calcola_aliquota(offerta.risparmio_energetico_trainante, offerta.costo_totale)

    offerta.crediti_fv = offerta.tipologia_moduli * offerta.aliquota * offerta.costo_fv if offerta.costo_fv else 0

    offerta.crediti_storage = offerta.tipologia_moduli * offerta.aliquota * min(offerta.costo_storage,
                                                                                offerta.storage_installato * 900)
    offerta.crediti_trainante = offerta.aliquota * offerta.costo_trainante
    offerta.crediti_totale = offerta.crediti_fv + offerta.crediti_storage + offerta.crediti_trainante

    risparmi_bolletta = calcola_risparmio(offerta.produzione_annua, 0.005, offerta.tariffa_energia_cliente)
    offerta.risparmi_bolletta = risparmi_bolletta
    # offerta.risparmi_bolletta = [] if offerta.risparmi_bolletta =="[]" else offerta.risparmi_bolletta
    offerta.risparmio_bolletta_primo_anno = risparmi_bolletta[0]
    offerta.risparmio_totale_primo_anno = offerta.risparmio_bolletta_primo_anno + offerta.crediti_totale
    # print(request.POST['importo_leasing'])
    offerta.importo_leasing = leggi_valore(request.POST['importo_leasing']) if request.POST['importo_leasing'].replace(
        "€", "").replace(".", "").replace(",", ".") else 0
    offerta.anticipo_leasing = leggi_valore(request.POST['anticipo_leasing']) if request.POST[
        'anticipo_leasing'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.prima_rata = leggi_valore(request.POST['prima_rata']) if request.POST['prima_rata'].replace("€",
                                                                                                        "").replace(".",
                                                                                                                    "").replace(
        ",", ".") else 0
    offerta.leasing_primo_anno = offerta.anticipo_leasing + offerta.prima_rata
    offerta.delta_leasing_primo_anno = offerta.risparmio_totale_primo_anno - offerta.leasing_primo_anno
    offerta.leasing_secondo_anno = leggi_valore(request.POST['leasing_secondo_anno']) if request.POST[
        'leasing_secondo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.delta_leasing_secondo_anno = - offerta.leasing_secondo_anno + risparmi_bolletta[1]
    offerta.leasing_terzo_anno = leggi_valore(request.POST['leasing_terzo_anno']) if request.POST[
        'leasing_terzo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0

    offerta.delta_leasing_terzo_anno = - offerta.leasing_terzo_anno + risparmi_bolletta[2]
    offerta.leasing_quarto_anno = leggi_valore(request.POST['leasing_quarto_anno']) if request.POST[
        'leasing_quarto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.delta_leasing_quarto_anno = - offerta.leasing_quarto_anno + risparmi_bolletta[3]
    offerta.leasing_quinto_anno = leggi_valore(request.POST['leasing_quinto_anno']) if request.POST[
        'leasing_quinto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.delta_leasing_quinto_anno = - offerta.leasing_quinto_anno + risparmi_bolletta[4]
    offerta.leasing_sesto_anno = leggi_valore(request.POST['leasing_sesto_anno']) if request.POST[
        'leasing_sesto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.delta_leasing_sesto_anno = - offerta.leasing_sesto_anno + risparmi_bolletta[5]
    offerta.leasing_settimo_anno = leggi_valore(request.POST['leasing_settimo_anno']) if request.POST[
        'leasing_settimo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.delta_leasing_settimo_anno = - offerta.leasing_settimo_anno + risparmi_bolletta[6]
    offerta.leasing_ottavo_anno = leggi_valore(request.POST['leasing_ottavo_anno']) if request.POST[
        'leasing_ottavo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.delta_leasing_ottavo_anno = - offerta.leasing_ottavo_anno + risparmi_bolletta[7]
    offerta.leasing_nono_anno = leggi_valore(request.POST['leasing_nono_anno']) if request.POST[
        'leasing_nono_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.delta_leasing_nono_anno = - offerta.leasing_nono_anno + risparmi_bolletta[8]
    offerta.leasing_decimo_anno = leggi_valore(request.POST['leasing_decimo_anno']) if request.POST[
        'leasing_decimo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
    offerta.delta_leasing_decimo_anno = - offerta.leasing_decimo_anno + risparmi_bolletta[9]

    offerta.delta_leasing_totale = offerta.risparmio_dieci_anni - offerta.importo_leasing if offerta.risparmio_dieci_anni else 0
    offerta.totale_check = (offerta.leasing_primo_anno + offerta.leasing_secondo_anno + offerta.leasing_terzo_anno +
                            offerta.leasing_quarto_anno + offerta.leasing_quinto_anno + offerta.leasing_sesto_anno +
                            offerta.leasing_settimo_anno + offerta.leasing_ottavo_anno + offerta.leasing_nono_anno
                            + offerta.leasing_decimo_anno)

    offerta.delta_totale_check = offerta.risparmio_dieci_anni - offerta.totale_check if offerta.risparmio_dieci_anni else 0
    print(offerta.leasing_secondo_anno)
    offerta.save()

    return redirect(offerta_view)


def offerta_view(request, slug):
    risparmi_bolletta = None
    offerta = Offerta.objects.get(slug=slug)
    # print(offerta.user)

    if offerta.user == request.user.username:
        if "salva_modifiche" in request.POST:
            offerta.date = datetime.now()
            consumi_cliente = request.POST['consumi_annui_cliente'].replace("kWh", "").replace(".", "").replace(",", ".")
            # print(request.POST['consumi_annui_cliente'])
            offerta.consumi_cliente = leggi_valore(request.POST['consumi_annui_cliente']) if request.POST['consumi_annui_cliente'] else 0

            offerta.costi_energia_cliente = leggi_valore(request.POST['costi_energia_cliente']) if request.POST['costi_energia_cliente'] != "" else 0
            # offerta.costi_energia_cliente = float(costi_energia_cliente) if costi_energia_cliente !="" else 0

            offerta.tariffa_energia_cliente = 1000 * offerta.costi_energia_cliente / offerta.consumi_cliente if offerta.consumi_cliente !=0 else 0
            offerta.costo_fv = leggi_valore(request.POST['costo_fv'])if request.POST['costo_fv'] != "Inserire dato da Ingegneria" and request.POST['costo_fv'] != "" else 0

            # offerta.costo_fv = float(request.POST['costo_fv'].replace("€", "").replace(",", ".")) if request.POST['costo_fv'] != "Inserire dato da Ingegneria" and request.POST['costo_fv'] != "" else 0
            offerta.costo_storage = leggi_valore(request.POST['costo_storage']) if request.POST['costo_storage'] != "Inserire dato da Ingegneria" else 0
            offerta.costo_trainante = leggi_valore(request.POST['costo_trainante']) if (request.POST['costo_trainante'] != "Inserire dato da Cliente"
                                                                 and request.POST['costo_trainante'] != "") else 0

            offerta.costo_totale = offerta.costo_fv + offerta.costo_storage + offerta.costo_trainante
            offerta.potenza_installata = leggi_valore(request.POST['potenza_installata']) if request.POST['potenza_installata']!= "Inserire dato da Ingegneria" else 0
            offerta.storage_installato = leggi_valore(request.POST['storage_installato']) if request.POST['storage_installato'] != "Inserire dato da Ingegneria" else 0
            offerta.producibilità_specifica = leggi_valore(request.POST['producibilità_specifica']) if request.POST['producibilità_specifica'] else 0
            offerta.produzione_annua = offerta.producibilità_specifica * offerta.potenza_installata if offerta.producibilità_specifica > 0 and offerta.potenza_installata else 0

            offerta.tipologia_moduli = leggi_valore(request.POST['tipologia_moduli'])
            # print(offerta.tipologia_moduli)
            offerta.risparmio_energetico_trainante = leggi_valore(request.POST['risparmio_energetico_trainante'])/100 if request.POST['risparmio_energetico_trainante'] != "" else 0

            offerta.aliquota = calcola_aliquota(offerta.risparmio_energetico_trainante, offerta.costo_totale)

            offerta.crediti_fv = offerta.tipologia_moduli * offerta.aliquota * offerta.costo_fv if offerta.costo_fv else 0

            offerta.crediti_storage = offerta.tipologia_moduli * offerta.aliquota * min(offerta.costo_storage, offerta.storage_installato *900)
            offerta.crediti_trainante = offerta.aliquota * offerta.costo_trainante
            offerta.crediti_totale = offerta.crediti_fv + offerta.crediti_storage + offerta.crediti_trainante

            risparmi_bolletta = calcola_risparmio(offerta.produzione_annua, 0.005, offerta.tariffa_energia_cliente)
            offerta.risparmi_bolletta = risparmi_bolletta
            # offerta.risparmi_bolletta = [] if offerta.risparmi_bolletta =="[]" else offerta.risparmi_bolletta
            offerta.risparmio_bolletta_primo_anno = risparmi_bolletta[0]
            offerta.risparmio_totale_primo_anno = offerta.risparmio_bolletta_primo_anno + offerta.crediti_totale
            # print(request.POST['importo_leasing'])
            offerta.importo_leasing = leggi_valore(request.POST['importo_leasing']) if request.POST['importo_leasing'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.anticipo_leasing = leggi_valore(request.POST['anticipo_leasing']) if request.POST['anticipo_leasing'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.prima_rata = leggi_valore(request.POST['prima_rata']) if request.POST['prima_rata'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.leasing_primo_anno = offerta.anticipo_leasing + offerta.prima_rata
            offerta.delta_leasing_primo_anno = offerta.risparmio_totale_primo_anno - offerta.leasing_primo_anno
            offerta.leasing_secondo_anno = leggi_valore(request.POST['leasing_secondo_anno']) if request.POST['leasing_secondo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.delta_leasing_secondo_anno = - offerta.leasing_secondo_anno + risparmi_bolletta[1]
            offerta.leasing_terzo_anno = leggi_valore(request.POST['leasing_terzo_anno']) if request.POST['leasing_terzo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0

            offerta.delta_leasing_terzo_anno = - offerta.leasing_terzo_anno + risparmi_bolletta[2]
            offerta.leasing_quarto_anno = leggi_valore(request.POST['leasing_quarto_anno']) if request.POST[
                'leasing_quarto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.delta_leasing_quarto_anno = - offerta.leasing_quarto_anno + risparmi_bolletta[3]
            offerta.leasing_quinto_anno = leggi_valore(request.POST['leasing_quinto_anno']) if request.POST[
                'leasing_quinto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.delta_leasing_quinto_anno = - offerta.leasing_quinto_anno + risparmi_bolletta[4]
            offerta.leasing_sesto_anno = leggi_valore(request.POST['leasing_sesto_anno']) if request.POST[
                'leasing_sesto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.delta_leasing_sesto_anno = - offerta.leasing_sesto_anno + risparmi_bolletta[5]
            offerta.leasing_settimo_anno = leggi_valore(request.POST['leasing_settimo_anno']) if request.POST[
                'leasing_settimo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.delta_leasing_settimo_anno = - offerta.leasing_settimo_anno + risparmi_bolletta[6]
            offerta.leasing_ottavo_anno = leggi_valore(request.POST['leasing_ottavo_anno']) if request.POST[
                'leasing_ottavo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.delta_leasing_ottavo_anno = - offerta.leasing_ottavo_anno + risparmi_bolletta[7]
            offerta.leasing_nono_anno = leggi_valore(request.POST['leasing_nono_anno']) if request.POST[
                'leasing_nono_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.delta_leasing_nono_anno = - offerta.leasing_nono_anno + risparmi_bolletta[8]
            offerta.leasing_decimo_anno = leggi_valore(request.POST['leasing_decimo_anno']) if request.POST[
                'leasing_decimo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
            offerta.delta_leasing_decimo_anno = - offerta.leasing_decimo_anno + risparmi_bolletta[9]

            offerta.delta_leasing_totale = offerta.risparmio_dieci_anni - offerta.importo_leasing if offerta.risparmio_dieci_anni else 0
            offerta.totale_check = (offerta.leasing_primo_anno+offerta.leasing_secondo_anno + offerta.leasing_terzo_anno +
                                    offerta.leasing_quarto_anno + offerta.leasing_quinto_anno + offerta.leasing_sesto_anno +
                                    offerta.leasing_settimo_anno + offerta.leasing_ottavo_anno + offerta.leasing_nono_anno
                                    + offerta.leasing_decimo_anno)

            offerta.delta_totale_check = offerta.risparmio_dieci_anni - offerta.totale_check if offerta.risparmio_dieci_anni else 0
            offerta.bilancio_dieci_anni = offerta.risparmio_dieci_anni - offerta.importo_leasing if offerta.risparmio_dieci_anni else 0

            offerta.save()
        elif "scarica_pdf" in request.POST:
            print("figa")
        else:
            offerta = Offerta.objects.get(slug=slug)
            # print(offerta.risparmi_bolletta)

        if risparmi_bolletta:
            risparmi_bolletta = [float(i) for i in risparmi_bolletta]

            indexes = [int(number) for number in range(1, 11)]
            # print(risparmi_bolletta)
            altri_risparmi_df = pd.DataFrame(zip(indexes[0:], risparmi_bolletta[0:]), columns=["index", "valore"])
            # print(risparmi_bolletta)
            # print(offerta.crediti_totale)

            offerta.risparmio_dieci_anni = offerta.crediti_totale + sum(risparmi_bolletta) if risparmi_bolletta else 0

            risparmio_string = []
            for risparmio in altri_risparmi_df.itertuples():
                risparmio_string.append(f"{round(risparmio.valore):,} €".replace(",", "."))
                altri_risparmi_df_string = pd.DataFrame(zip(indexes[1:], risparmio_string[1:]), columns=["index", "valore"])
        else:
            altri_risparmi_df = []
            altri_risparmi_df_string = []

        # print(altri_risparmi_df_string)

        offerta.save()
        print(offerta.date)
        leasing_list = [
            f"{round(offerta.leasing_primo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                      ",") if offerta.leasing_primo_anno else '',
            f"{round(offerta.leasing_secondo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                      ",") if offerta.leasing_secondo_anno else '',
            f"{round(offerta.leasing_terzo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                        ",") if offerta.leasing_terzo_anno else '',
            f"{round(offerta.leasing_quarto_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                      ",") if offerta.leasing_quarto_anno else '',
            f"{round(offerta.leasing_quinto_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                       ",") if offerta.leasing_quinto_anno else '',
            f"{round(offerta.leasing_sesto_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                       ",") if offerta.leasing_sesto_anno else '',
            f"{round(offerta.leasing_settimo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                      ",") if offerta.leasing_settimo_anno else '',
            f"{round(offerta.leasing_ottavo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                        ",") if offerta.leasing_ottavo_anno else '',
            f"{round(offerta.leasing_nono_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                       ",") if offerta.leasing_nono_anno else '',
            f"{round(offerta.leasing_decimo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                     ",") if offerta.leasing_decimo_anno else '',
        ]

        delta_leasing_list = [
            f"{round(offerta.delta_leasing_primo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                      ",") if offerta.delta_leasing_primo_anno else '€',
            f"{round(offerta.delta_leasing_secondo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                        ",") if offerta.delta_leasing_secondo_anno else '€',
            f"{round(offerta.delta_leasing_terzo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                      ",") if offerta.delta_leasing_terzo_anno else '€',
            f"{round(offerta.delta_leasing_quarto_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                       ",") if offerta.delta_leasing_quarto_anno else '€',
            f"{round(offerta.delta_leasing_quinto_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                       ",") if offerta.delta_leasing_quinto_anno else '€',
            f"{round(offerta.delta_leasing_sesto_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                      ",") if offerta.delta_leasing_sesto_anno else '€',
            f"{round(offerta.delta_leasing_settimo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                        ",") if offerta.delta_leasing_settimo_anno else '€',
            f"{round(offerta.delta_leasing_ottavo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                       ",") if offerta.delta_leasing_ottavo_anno else '€',
            f"{round(offerta.delta_leasing_nono_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                     ",") if offerta.delta_leasing_nono_anno else '€',
            f"{round(offerta.delta_leasing_decimo_anno, 2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                       ",") if offerta.delta_leasing_decimo_anno else '€',
        ]
        indexes = [int(number) for number in range(1, 11)]
        print(indexes)
        index_anno = ['secondo', 'terzo', 'quarto', 'quinto', 'sesto', 'settimo', 'ottavo', 'nono', 'decimo']
        leasing_tab = pd.DataFrame(zip(indexes[1:], index_anno, leasing_list[1:], delta_leasing_list[1:]), columns=["index", "index_anno", "valore","delta"])


        data = {
            'nome_cliente': offerta.nome_cliente,
            'partita_iva': offerta.partita_iva,
            'consumi_annui_cliente': f"{round(offerta.consumi_cliente,2):,} kWh".replace(',',';').replace('.',',').replace(';','.') if offerta.consumi_cliente > 0 else 'kWh',
            'costi_energia_cliente': f"{round(offerta.costi_energia_cliente, 2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.costi_energia_cliente else '€',
            'tariffa_energia_cliente': f"{round(offerta.tariffa_energia_cliente, 2):,} €/MWh".replace(',',';').replace('.',',').replace(';','.') if offerta.costi_energia_cliente else '',
            'costo_fv': f"{round(offerta.costo_fv, 2):,} €".replace(',',';').replace(',',';').replace('.',',').replace(';','.') if offerta.costo_fv else '',
            'costo_storage': f"{round(offerta.costo_storage,2):,} €".replace(',',';').replace(',',';').replace('.',',').replace(';','.') if offerta.costo_storage else '',
            'costo_trainante': f"{round(offerta.costo_trainante,2):,} €".replace(',',';').replace(',',';').replace('.',',').replace(';','.') if offerta.costo_trainante else '',
            'costo_totale': f"{round(offerta.costo_totale,2):,} €".replace(',',';').replace(',',';').replace('.',',').replace(';','.') if offerta.costo_totale else '',
            'potenza_installata': f"{round(offerta.potenza_installata,2):,} kW".replace(',',';').replace('.',',').replace(';','.') if offerta.potenza_installata else '',
            'storage_installato': f"{round(offerta.storage_installato,2):,} kWh".replace(',',';').replace('.',',').replace(';','.') if offerta.storage_installato else '',
            'producibilità_specifica': f"{round(offerta.producibilità_specifica, 2):,} kWh/kWp".replace(',', ';').replace('.', ',').replace(';', '.') if offerta.producibilità_specifica else '',
            'produzione_annua': f"{round(offerta.produzione_annua):,} kWh".replace(',', '.') if offerta.produzione_annua else '',
            'crediti_fv': f"{round(offerta.crediti_fv, 2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.crediti_fv else '€',
            'crediti_storage': f"{round(offerta.crediti_storage,2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.crediti_storage else '€',
            'crediti_trainante': f"{round(offerta.crediti_trainante,2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.crediti_trainante else '€',
            'crediti_totale': f"{round(offerta.crediti_totale,2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.crediti_totale else '€',
            'risparmio_energetico_trainante': offerta.risparmio_energetico_trainante if offerta.risparmio_energetico_trainante else '%',
            'aliquota': f"{round(100*offerta.aliquota)} %",
            'risparmio_bolletta_primo_anno': f"{round(offerta.risparmio_bolletta_primo_anno, 2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.risparmio_bolletta_primo_anno else '€',
            'risparmio_totale_primo_anno': f"{round(offerta.risparmio_totale_primo_anno, 2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.risparmio_totale_primo_anno else '€',
            'risparmi_bolletta': altri_risparmi_df_string,
            'risparmio_dieci_anni': f"{round(offerta.risparmio_dieci_anni, 2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.risparmio_dieci_anni else '€',
            'importo_leasing': f"{round(offerta.importo_leasing, 2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.importo_leasing else '€',
            'anticipo_leasing': f"{round(offerta.anticipo_leasing,2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.importo_leasing else '€',
            'prima_rata': f"{round(offerta.prima_rata,2):,} €".replace(',',';').replace('.',',').replace(';','.') if offerta.prima_rata else '€',
            'leasing_primo_anno': f"{round(offerta.leasing_primo_anno,2):,} €".replace(".",";").replace(",",".").replace(";",",") if offerta.leasing_primo_anno else '€',
            'delta_leasing_primo_anno': f"{round(offerta.delta_leasing_primo_anno,2):,} €".replace(".", ";").replace(",",".").replace(";",",") if offerta.leasing_primo_anno else '€',
            'leasing_secondo_anno': f"{round(offerta.leasing_secondo_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                  ",") if offerta.leasing_secondo_anno else '€',
            'delta_leasing_secondo_anno': f"{round(offerta.delta_leasing_secondo_anno,2):,} €".replace(".", ";").replace(",",
                                                                                                            ".").replace(
                ";", ",") if offerta.delta_leasing_secondo_anno else '€',
            'leasing_terzo_anno': f"{round(offerta.leasing_terzo_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                      ",") if offerta.leasing_terzo_anno else '€',
            'delta_leasing_terzo_anno': f"{round(offerta.delta_leasing_terzo_anno,2):,} €".replace(".", ";").replace(",",
                                                                                                                ".").replace(
                ";", ",") if offerta.delta_leasing_terzo_anno else '€',
            'leasing_quarto_anno': f"{round(offerta.leasing_quarto_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                  ",") if offerta.leasing_quarto_anno else '€',
            'delta_leasing_quarto_anno': f"{round(offerta.delta_leasing_quarto_anno,2):,} €".replace(".", ";").replace(",",
                                                                                                            ".").replace(
                ";", ",") if offerta.delta_leasing_quarto_anno else '€',
            'leasing_quinto_anno': f"{round(offerta.leasing_quinto_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                    ",") if offerta.leasing_quinto_anno else '€',
            'delta_leasing_quinto_anno': f"{round(offerta.delta_leasing_quinto_anno,2):,} €".replace(".", ";").replace(",",
                                                                                                              ".").replace(
                ";", ",") if offerta.delta_leasing_quinto_anno else '€',
            'leasing_sesto_anno': f"{round(offerta.leasing_sesto_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                    ",") if offerta.leasing_sesto_anno else '€',
            'delta_leasing_sesto_anno': f"{round(offerta.delta_leasing_sesto_anno,2):,} €".replace(".", ";").replace(",",
                                                                                                              ".").replace(
                ";", ",") if offerta.delta_leasing_sesto_anno else '€',
            'leasing_settimo_anno': f"{round(offerta.leasing_settimo_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                  ",") if offerta.leasing_settimo_anno else '€',
            'delta_leasing_settimo_anno': f"{round(offerta.delta_leasing_settimo_anno,2):,} €".replace(".", ";").replace(",",
                                                                                                            ".").replace(
                ";", ",") if offerta.delta_leasing_settimo_anno else '€',
            'leasing_ottavo_anno': f"{round(offerta.leasing_ottavo_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                      ",") if offerta.leasing_ottavo_anno else '€',
            'delta_leasing_ottavo_anno': f"{round(offerta.delta_leasing_ottavo_anno,2):,} €".replace(".", ";").replace(",",
                                                                                                                ".").replace(
                ";", ",") if offerta.delta_leasing_ottavo_anno else '€',
            'leasing_nono_anno': f"{round(offerta.leasing_nono_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                    ",") if offerta.leasing_nono_anno else '€',
            'delta_leasing_nono_anno': f"{round(offerta.delta_leasing_nono_anno,2):,} €".replace(".", ";").replace(",", ".").replace(
                ";", ",") if offerta.delta_leasing_nono_anno else '€',
            'leasing_decimo_anno': f"{round(offerta.leasing_decimo_anno,2):,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                ",") if offerta.leasing_decimo_anno else '€',
            'delta_leasing_decimo_anno': f"{round(offerta.delta_leasing_decimo_anno,2):,} €".replace(".", ";").replace(",",
                                                                                                          ".").replace(
                ";", ",") if offerta.delta_leasing_decimo_anno else '€',
            'totale_check': f"{round(offerta.totale_check,2):,} €".replace(".", ";").replace(",",
                                                                                                          ".").replace(
                ";", ",") if offerta.delta_totale_check else '€',
            'delta_totale_check': f"{round(offerta.delta_totale_check, 2):,} €".replace(".", ";").replace(",",
                                                                                              ".").replace(
                ";", ",") if offerta.delta_totale_check else '€',
            'tipologia_pannelli': str(offerta.tipologia_moduli),
            'date': offerta.date.strftime("%d/%m/%Y %H:%M") if offerta.date else "",
            'leasing_tab': leasing_tab,
            'bilancio_dieci_anni': offerta.bilancio_dieci_anni if offerta.bilancio_dieci_anni else 0
        }

        return render(request, "EPC_5_0_v02/offerta_v01.html", context=data)
    else:
        data = {
            "url": slug
        }
        print(slug)
        return render(request, "registration/login.html", context=data)


def inizializza_offerta(request):
    slug = slugify(request.POST['client_name'])
    offerta = Offerta(slug=slugify(slug))
    offerta.nome_cliente = request.POST['client_name']
    offerta.partita_iva = request.POST['partita_iva']
    offerta.user = request.user
    try:
        offerta.save()
        return slug
    except Exception as err:
        print(err)

        return 'err'


# Create your views here.
class IndexView(View):
    def get(self, request, client_initial="", p_iva_initial="", message=""):
        form = InserisciCliente()

        form.initial["client_name"] = client_initial
        form.initial["partita_iva"] = p_iva_initial

        return render(request, "EPC_5_0_v02/index.html", {
            "form": form,
            "message": message,
            "url": f"{slugify(client_initial)}"
        })

    def post(self, request):
        form = InserisciCliente(request.POST)
        if form.is_valid():
            slug = inizializza_offerta(request)
            client_name = request.POST["client_name"]
            p_iva = request.POST["partita_iva"]
            message = "Cliente già esistente."
            if slug == 'err':
                return IndexView.get(self, request, client_name, p_iva, message)
            else:
                return redirect(f"offerte/{slug}")


def offerte(request):
    offerte = Offerta.objects.filter(user=request.user.username).order_by('-date')

    return render(request, "EPC_5_0_v02/offerte.html", {
        "offerte": offerte
    })

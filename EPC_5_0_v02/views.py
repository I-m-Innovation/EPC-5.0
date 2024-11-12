from django.shortcuts import render, redirect
from django.views import View
from .forms import InserisciCliente
from django.http import HttpResponseRedirect
from slugify import slugify
from .models import Offerta
import pandas as pd


def pulsanti(request, slug):
    # print(slug)
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
            risparmio.append(produzione * tariffa_energia)
            totale_risparmio = sum(risparmio)
        else:
            produzione = "INSERIRE DATI IMPIANTO"
            risparmio.append(produzione)
            totale_risparmio = "INSERIRE DATI IMPIANTO"

    return risparmio


def offerta_view(request, slug):

    if "salva_modifiche" in request.POST:
        offerta = Offerta.objects.get(slug=slug)
        consumi_cliente = request.POST['consumi_annui_cliente'].replace("kWh", "").replace(".", "").replace(",", ".")
        offerta.consumi_cliente = float(consumi_cliente) if consumi_cliente !="" else 0

        costi_energia_cliente = request.POST['costi_energia_cliente'].replace("€", "").replace(".", "").replace(",", ".")
        offerta.costi_energia_cliente = float(costi_energia_cliente) if costi_energia_cliente !="" else 0

        offerta.tariffa_energia_cliente = 1000 * offerta.consumi_cliente / offerta.costi_energia_cliente if offerta.costi_energia_cliente !=0 else 0
        offerta.costo_fv = float(request.POST['costo_fv'].replace("€", "").replace(".", "").
                                        replace(",", ".")) if request.POST['costo_fv'] != "Inserire dato da Ingegneria" and request.POST['costo_fv'] != "" else 0
        offerta.costo_storage = float(request.POST['costo_storage'].replace("€", "").replace(".", "").
                                        replace(",", ".")) if request.POST['costo_storage'] != "Inserire dato da Ingegneria" else 0
        offerta.costo_trainante = float(request.POST['costo_trainante'].replace("€", "").replace(".", "").
                                      replace(",", ".")) if (request.POST['costo_trainante'] != "Inserire dato da Cliente"
                                                             and request.POST['costo_trainante'] != "") else 0

        offerta.costo_totale = offerta.costo_fv + offerta.costo_storage + offerta.costo_trainante
        offerta.potenza_installata = float(request.POST['potenza_installata'].replace("kW", "").replace(".", "").
                                        replace(",", ".")) if request.POST['potenza_installata']!= "Inserire dato da Ingegneria" else 0
        offerta.storage_installato = float(request.POST['storage_installato'].replace("kWh", "").replace(".", "").
                                           replace(",", ".")) if request.POST[
                                                                     'storage_installato'] != "Inserire dato da Ingegneria" else 0
        offerta.producibilità_specifica = float(request.POST['producibilità_specifica'].replace("kWh/kWp", "").replace(".", "").
                                           replace(",", ".")) if request.POST[
                                                                     'producibilità_specifica'] != "Inserire dato da Ingegneria" else 0

        offerta.produzione_annua = offerta.producibilità_specifica*offerta.potenza_installata if offerta.producibilità_specifica>0 and offerta.potenza_installata else 0

        offerta.tipologia_moduli = float(request.POST['tipologia_moduli'])
        offerta.risparmio_energetico_trainante = request.POST['risparmio_energetico_trainante']
        offerta.aliquota = calcola_aliquota(offerta.risparmio_energetico_trainante, offerta.costo_totale)

        offerta.crediti_fv = offerta.tipologia_moduli * offerta.aliquota * offerta.costo_fv if offerta.costo_fv else 0

        offerta.crediti_storage = offerta.tipologia_moduli * offerta.aliquota * min(offerta.costo_storage, offerta.storage_installato *900)
        offerta.crediti_trainante = offerta.aliquota * offerta.costo_trainante
        print(offerta.crediti_trainante)
        offerta.crediti_totale = offerta.crediti_fv + offerta.crediti_storage + offerta.crediti_trainante

        risparmi_bolletta = calcola_risparmio(offerta.produzione_annua, 0.005, offerta.tariffa_energia_cliente)
        offerta.risparmi_bolletta = risparmi_bolletta
        # offerta.risparmi_bolletta = [] if offerta.risparmi_bolletta =="[]" else offerta.risparmi_bolletta
        offerta.risparmio_bolletta_primo_anno = risparmi_bolletta[0]
        offerta.risparmio_totale_primo_anno = offerta.risparmio_bolletta_primo_anno + offerta.crediti_totale
        # print(request.POST['importo_leasing'])
        offerta.importo_leasing = float(request.POST['importo_leasing'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST['importo_leasing'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.anticipo_leasing = float(request.POST['anticipo_leasing'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST['anticipo_leasing'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.prima_rata = float(request.POST['prima_rata'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST['prima_rata'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.leasing_primo_anno =  offerta.anticipo_leasing + offerta.prima_rata
        offerta.delta_leasing_primo_anno = offerta.risparmio_totale_primo_anno - offerta.leasing_primo_anno
        offerta.leasing_secondo_anno = float(request.POST['leasing_secondo_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST['leasing_secondo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.delta_leasing_secondo_anno = offerta.leasing_secondo_anno - risparmi_bolletta[1]
        offerta.leasing_terzo_anno = float(
            request.POST['leasing_terzo_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST['leasing_terzo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0

        offerta.delta_leasing_terzo_anno = offerta.leasing_terzo_anno - risparmi_bolletta[2]
        offerta.leasing_quarto_anno = float(
            request.POST['leasing_quarto_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST[
            'leasing_quarto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.delta_leasing_quarto_anno = offerta.leasing_quarto_anno - risparmi_bolletta[3]
        offerta.leasing_quinto_anno = float(
            request.POST['leasing_quinto_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST[
            'leasing_quinto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.delta_leasing_quinto_anno = offerta.leasing_quinto_anno - risparmi_bolletta[4]
        offerta.leasing_sesto_anno = float(
            request.POST['leasing_sesto_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST[
            'leasing_sesto_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.delta_leasing_sesto_anno = offerta.leasing_sesto_anno - risparmi_bolletta[5]
        offerta.leasing_settimo_anno = float(
            request.POST['leasing_settimo_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST[
            'leasing_settimo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.delta_leasing_settimo_anno = offerta.leasing_settimo_anno - risparmi_bolletta[6]
        offerta.leasing_ottavo_anno = float(
            request.POST['leasing_ottavo_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST[
            'leasing_ottavo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.delta_leasing_ottavo_anno = offerta.leasing_ottavo_anno - risparmi_bolletta[7]
        offerta.leasing_nono_anno = float(
            request.POST['leasing_nono_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST[
            'leasing_nono_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.leasing_nono_anno = offerta.leasing_nono_anno - risparmi_bolletta[8]
        offerta.leasing_decimo_anno = float(
            request.POST['leasing_decimo_anno'].replace("€", "").replace(".", "").replace(",", ".")) if request.POST[
            'leasing_decimo_anno'].replace("€", "").replace(".", "").replace(",", ".") else 0
        offerta.leasing_decimo_anno = offerta.leasing_decimo_anno - risparmi_bolletta[9]




        offerta.save()
    else:
        offerta = Offerta.objects.get(slug=slug)

        # print(offerta.risparmi_bolletta)
        risparmi_bolletta = offerta.risparmi_bolletta.replace("[", "").replace("]", "").split(",") if offerta.risparmi_bolletta else None

    if risparmi_bolletta:
        risparmi_bolletta = [float(i) for i in risparmi_bolletta]

        indexes = [int(number) for number in range(1, 11)]
        altri_risparmi_df = pd.DataFrame(zip(indexes[1:], risparmi_bolletta[1:]), columns=["index", "valore"])

        offerta.risparmio_dieci_anni = sum(risparmi_bolletta)
    else:
        altri_risparmi_df = []

    print(offerta.delta_leasing_secondo_anno)

    data = {
        'consumi_annui_cliente': f"{round(offerta.consumi_cliente):,} kWh".replace(',', '.') if offerta.consumi_cliente > 0 else 'kWh',
        'costi_energia_cliente': f"{round(offerta.costi_energia_cliente)} €".replace(',', '.') if offerta.costi_energia_cliente else '€',
        'tariffa_energia_cliente': f"{offerta.tariffa_energia_cliente} €/MWh" if offerta.costi_energia_cliente else 'Inserire dati cliente',
        'costo_fv': f"{round(offerta.costo_fv)} €" if offerta.costo_fv else 'Inserire dato da Ingegneria',
        'costo_storage': f"{round(offerta.costo_storage)} €" if offerta.costo_storage else 'Inserire dato da Ingegneria',
        'costo_trainante': f"{round(offerta.costo_trainante)} €" if offerta.costo_trainante else 'Inserire dato da Cliente',
        'costo_totale': f"{round(offerta.costo_totale)} €" if offerta.costo_totale else 'Inserire dato da Cliente',
        'potenza_installata': f"{offerta.potenza_installata:,} kW".replace('.', ';').replace(',', '.').replace(';', ',') if offerta.potenza_installata else 'Inserire dato da Ingegneria',
        'storage_installato': f"{offerta.storage_installato:,} kWh".replace('.', ',').replace(',', '.') if offerta.storage_installato else 'Inserire dato da Ingegneria',
        'producibilità_specifica': f"{round(offerta.producibilità_specifica):,} kWh/kWp".replace(',', '.') if offerta.producibilità_specifica else 'Inserire dato da Ingegneria',
        'produzione_annua': f"{round(offerta.produzione_annua):,} kWh".replace(',', '.') if offerta.produzione_annua else 'Inserire dato da Ingegneria',
        'crediti_fv': f"{round(offerta.crediti_fv)} €".replace(',', '.') if offerta.crediti_fv else '€',
        'crediti_storage': f"{round(offerta.crediti_storage)} €".replace(',', '.') if offerta.crediti_storage else '€',
        'crediti_trainante': f"{round(offerta.crediti_trainante)} €".replace(',', '.') if offerta.crediti_trainante else '€',
        'crediti_totale': f"{round(offerta.crediti_totale)} €".replace(',','.') if offerta.crediti_totale else '€',
        'aliquota': f"{round(100*offerta.aliquota)} %",
        'risparmio_bolletta_primo_anno': offerta.risparmio_bolletta_primo_anno,
        'risparmio_totale_primo_anno': offerta.risparmio_totale_primo_anno,
        'risparmi_bolletta': altri_risparmi_df,
        'risparmio_dieci_anni': f"{offerta.risparmio_dieci_anni} €" if offerta.risparmio_dieci_anni else '€',
        'importo_leasing': f"{round(offerta.importo_leasing)} €" if offerta.importo_leasing else '€',
        'anticipo_leasing': f"{offerta.anticipo_leasing} €" if offerta.importo_leasing else '€',
        'prima_rata': f"{offerta.prima_rata:,} €".replace(".",";").replace(",",".").replace(";",",") if offerta.prima_rata else '€',
        'leasing_primo_anno': f"{offerta.leasing_primo_anno:,} €".replace(".",";").replace(",",".").replace(";",",") if offerta.leasing_primo_anno else '€',
        'delta_leasing_primo_anno': f"{offerta.delta_leasing_primo_anno:,} €".replace(".",";").replace(",",".").replace(";",",") if offerta.leasing_primo_anno else '€',
        'leasing_secondo_anno': f"{offerta.leasing_secondo_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                              ",") if offerta.leasing_secondo_anno else '€',
        'delta_leasing_secondo_anno': f"{offerta.delta_leasing_secondo_anno:,} €".replace(".", ";").replace(",",
                                                                                                        ".").replace(
            ";", ",") if offerta.delta_leasing_secondo_anno else '€',
        'leasing_terzo_anno': f"{offerta.leasing_terzo_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                  ",") if offerta.leasing_terzo_anno else '€',
        'delta_leasing_terzo_anno': f"{offerta.delta_leasing_terzo_anno:,} €".replace(".", ";").replace(",",
                                                                                                            ".").replace(
            ";", ",") if offerta.delta_leasing_terzo_anno else '€',
        'leasing_quarto_anno': f"{offerta.leasing_quarto_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                              ",") if offerta.leasing_quarto_anno else '€',
        'delta_leasing_quarto_anno': f"{offerta.delta_leasing_quarto_anno:,} €".replace(".", ";").replace(",",
                                                                                                        ".").replace(
            ";", ",") if offerta.delta_leasing_quarto_anno else '€',
        'leasing_quinto_anno': f"{offerta.leasing_quinto_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                ",") if offerta.leasing_quinto_anno else '€',
        'delta_leasing_quinto_anno': f"{offerta.delta_leasing_quinto_anno:,} €".replace(".", ";").replace(",",
                                                                                                          ".").replace(
            ";", ",") if offerta.delta_leasing_quinto_anno else '€',
        'leasing_sesto_anno': f"{offerta.leasing_sesto_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                ",") if offerta.leasing_sesto_anno else '€',
        'delta_leasing_sesto_anno': f"{offerta.delta_leasing_sesto_anno:,} €".replace(".", ";").replace(",",
                                                                                                          ".").replace(
            ";", ",") if offerta.delta_leasing_sesto_anno else '€',
        'leasing_settimo_anno': f"{offerta.leasing_settimo_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                              ",") if offerta.leasing_settimo_anno else '€',
        'delta_leasing_settimo_anno': f"{offerta.delta_leasing_settimo_anno:,} €".replace(".", ";").replace(",",
                                                                                                        ".").replace(
            ";", ",") if offerta.delta_leasing_settimo_anno else '€',
        'leasing_ottavo_anno': f"{offerta.leasing_ottavo_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                  ",") if offerta.leasing_ottavo_anno else '€',
        'delta_leasing_ottavo_anno': f"{offerta.delta_leasing_ottavo_anno:,} €".replace(".", ";").replace(",",
                                                                                                            ".").replace(
            ";", ",") if offerta.delta_leasing_ottavo_anno else '€',
        'leasing_nono_anno': f"{offerta.leasing_nono_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                                ",") if offerta.leasing_nono_anno else '€',
        'delta_leasing_nono_anno': f"{offerta.delta_leasing_nono_anno:,} €".replace(".", ";").replace(",",
                                                                                                          ".").replace(
            ";", ",") if offerta.delta_leasing_nono_anno else '€',
        'leasing_decimo_anno': f"{offerta.leasing_decimo_anno:,} €".replace(".", ";").replace(",", ".").replace(";",
                                                                                                            ",") if offerta.leasing_decimo_anno else '€',
        'delta_leasing_decimo_anno': f"{offerta.delta_leasing_decimo_anno:,} €".replace(".", ";").replace(",",
                                                                                                      ".").replace(
            ";", ",") if offerta.delta_leasing_decimo_anno else '€',

    }

    return render(request, "EPC_5_0_v02/offerta.html", context=data)


def inizializza_offerta(request):
    slug = slugify(request.POST['client_name'])
    offerta = Offerta(slug=slugify(slug))
    offerta.save()

    return slug


# Create your views here.
class IndexView(View):
    def get(self, request):
        form = InserisciCliente()

        return render(request, "EPC_5_0_v02/index.html", {
            "form": form
        })

    def post(self, request):
        form = InserisciCliente(request.POST)
        if form.is_valid():
            slug = inizializza_offerta(request)
            return redirect(f"/{slug}")
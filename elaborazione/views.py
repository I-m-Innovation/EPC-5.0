from django.shortcuts import render, redirect
from .models import Impianto
from decimal import Decimal, InvalidOperation
import pandas as pd
#questa è la versione corrente


def index(request):
    # Lettura del CSV e ricerca di impianto coperto
    CSV_PATH = "Cartel3.csv"
    df = pd.read_csv(CSV_PATH)

    if request.method == 'GET':

        data = {
        'costo_impianto': '',
        'storage': '',
        'credito_contributo': '',
        'bene_trainante2': '',
        'costo_totale_impianto': '',
        'credito_fiscale_5_0': '',
        'creditoFiscale': '',
        'consumi_annui': '',
        'produzione_annua': '',
        'risparmio_primo_annuo': '',
        'tipologia_pannelli': '',
        'costi_annui': '',
        'Bolletta_primo_annuo': '',
        'potenza_installata': '',
        'aliquota_concessa': '',
        'producibilità': '',

        # Dizionari con il decadimento della produzione e il risparmio energetico per ogni anno
        'decadimento_annuale': '',
        'risparmio_annuo': '',
        'error_message': '',
        }

    else:
        # riquadro blu
        costo_impianto = request.POST.get('costo_impianto', '')
        costo_impianto_val = costo_impianto.replace('€', '').replace('.', '').replace(',', '.') if costo_impianto else 0
        costo_impianto_val = float(costo_impianto_val)
        costo_storage_blu = request.POST.get('storage_blu', '')
        costo_storage_blu_val = costo_storage_blu.replace('€', '').replace('.', '').replace(',', '.') if costo_storage_blu else 0
        costo_storage_blu_val = float(costo_storage_blu_val)
        bene_trainante_blu = request.POST.get('bene_trainante_blu', '')
        bene_trainante_blu_val = bene_trainante_blu.replace('€', '').replace('.', '').replace(',', '.') if bene_trainante_blu else 0
        bene_trainante_blu_val = float(bene_trainante_blu_val) if bene_trainante_blu_val else 0
        costo_impianto_e_storage = costo_impianto_val + costo_storage_blu_val

        potenza_installata = request.POST.get('potenza_installata', '')
        potenza_installata_val = potenza_installata.replace('kW', '').replace(',', '.').replace(' ','') if potenza_installata else ''

        if potenza_installata_val != '':
            potenza_installata_val = float(potenza_installata_val)

        storage_installato = request.POST.get('storage_installato', '')
        storage_installato_val = storage_installato.replace('kWh', '').replace(',', '.') if storage_installato else 0
        storage_installato_val = float(storage_installato_val)
        producbilit = request.POST.get('producbilit', '')
        producbilità_val = producbilit.replace('kWh/kWp', '').replace(',', '.').replace(' ','') if producbilit else ''
        if producbilità_val != '':
            producbilità_val = float(producbilità_val)

        if producbilità_val != "" and potenza_installata_val != "":
            produzione_annua = producbilità_val * potenza_installata_val
        else:
            produzione_annua = "INSERIRE DATI IMPIANTO"

        tipologia_pannelli = request.POST.get('tipologia_pannelli', '')
        tipologia_pannelli_val = float(tipologia_pannelli)

        if producbilità_val != "" and potenza_installata_val != "":
            produzione_annua_val = producbilità_val * potenza_installata_val
        else:
            produzione_annua_val = "INSERIRE DATI IMPIANTO"
        # produzione_annua_val = produzione_annua.replace('kWh', '').replace(',', '.')\

        # riquadro rosso
        if potenza_installata_val != '':
            impianto_coperto_row = df[df['min'] <= float(potenza_installata_val)].iloc[-1:]
            impianto_coperto_value = impianto_coperto_row['copertura'].values[0]
            contributo_impianto = min(impianto_coperto_value * potenza_installata_val, costo_impianto_val)

        else:
            contributo_impianto = ''

        risparmio_energetico_trainante = int(request.POST.get('risparmio_energetico_trainante', '')) / 100

        spesa_totale = costo_impianto_e_storage + bene_trainante_blu_val

        if risparmio_energetico_trainante == 0.05:
            if spesa_totale < 2.5e6:
                aliquota = 0.35
            elif 2.5e6 <= spesa_totale < 10e6:
                aliquota = 0.15
            else:
                aliquota = 0.05

        elif risparmio_energetico_trainante == 0.10:
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

        if contributo_impianto != '':
            contributo_impianto_val = tipologia_pannelli_val*aliquota * contributo_impianto
            contributo_impianto_str = format_euro(contributo_impianto_val) if contributo_impianto_val else '',
            contributo_impianto_str = contributo_impianto_str[0]
        else:
            contributo_impianto_val = "INSERIRE DATI IMPIANTO"
            contributo_impianto_str = "INSERIRE DATI IMPIANTO"

        contributo_storage_val = tipologia_pannelli_val*aliquota*min(storage_installato_val * 900, costo_storage_blu_val)

        if storage_installato_val == 0:
            contributo_storage_str = "STORAGE NON INSTALLATO"
        else:
            contributo_storage_str = format_euro(contributo_storage_val) if contributo_storage_val else '',
            contributo_storage_str = contributo_storage_str[0]

        contributo_trainante_val = aliquota * bene_trainante_blu_val
        contributo_trainante_str = format_euro(contributo_trainante_val) if contributo_trainante_val else '',

        if contributo_impianto_val!= "INSERIRE DATI IMPIANTO":
            credito_maturato_val = contributo_impianto_val + contributo_storage_val + contributo_trainante_val
            credito_maturato = format_euro(contributo_impianto_val + contributo_storage_val + contributo_trainante_val)
        else:
            credito_maturato = "INSERIRE DATI IMPIANTO"

        # riquadro verde
        consumo_annuo = request.POST.get('consumi_annui', '')
        consumo_annuo = consumo_annuo.replace('kWh', '').replace('.', '').replace(',', '.') if consumo_annuo else 0
        consumo_annuo_val = float(consumo_annuo) if consumo_annuo else 0
        bolletta_annua = request.POST.get('costi_annui', '')
        bolletta_annua = bolletta_annua.replace('€', '').replace('.', '').replace(',', '.') if bolletta_annua else 0
        bolletta_annua_val = float(bolletta_annua) if bolletta_annua else 0

        tariffa_energia = bolletta_annua_val / consumo_annuo_val if consumo_annuo_val != 0 else 0
        if produzione_annua_val != "INSERIRE DATI IMPIANTO":
            bolletta_primo_anno = format_euro((consumo_annuo_val - produzione_annua_val) * tariffa_energia)
        else:
            bolletta_primo_anno = "INSERIRE DATI IMPIANTO"
        # print(aliquota)

        risparmio = []
        perdita = 0.005

        indexes = []

        for i in range(9):
            indexes.append(i+1)
            if produzione_annua_val != "INSERIRE DATI IMPIANTO":
                produzione = produzione_annua_val * pow(1-perdita, i)
                risparmio.append(produzione*tariffa_energia)
                totale_risparmio = sum(risparmio)
            else:
                produzione = "INSERIRE DATI IMPIANTO"
                risparmio.append(produzione)
                totale_risparmio = "INSERIRE DATI IMPIANTO"

        risparmio_string = []
        for risparmio_num in risparmio:

            if risparmio_num != "INSERIRE DATI IMPIANTO":
                risparmio_string.append(format_euro(risparmio_num))
            else:
                risparmio_string.append("INSERIRE DATI IMPIANTO")

        risparmio_list = pd.DataFrame({"index": indexes, "risparmio": risparmio_string})
        if risparmio[0] != "INSERIRE DATI IMPIANTO":
            primo_risparmio = risparmio[0]+credito_maturato_val
            totale_risparmio += primo_risparmio
            primo_risparmio = format_euro(primo_risparmio)
            totale_risparmio = format_euro(totale_risparmio)
        else:
            primo_risparmio = "INSERIRE DATI IMPIANTO"

        data = {
            'costo_impianto': format_euro(costo_impianto_val) if costo_impianto else '',
            'costo_storage_blu': format_euro(costo_storage_blu_val) if costo_storage_blu else '',
            'bene_trainante_blu': format_euro(bene_trainante_blu_val) if bene_trainante_blu else '',
            'costo_totale_impianto': format_euro(costo_impianto_e_storage+bene_trainante_blu_val) if costo_impianto_e_storage else '',
            'potenza_installata': f"{potenza_installata_val} kW",
            'storage_installato': f"{storage_installato_val} kWh",
            'producibilit': f"{producbilità_val} kWh/kWp",
            'produzione_annua': f"{produzione_annua_val} kWh",
            'tipologia_pannelli': tipologia_pannelli,
            'contributo_impianto': contributo_impianto_str,
            'contributo_storage': contributo_storage_str,
            'bene_trainante_rosso': contributo_trainante_str[0] if contributo_trainante_str else '',
            'credito_maturato': credito_maturato,
            "aliquota": f"{round(aliquota*100)} %",
            "bolletta_primo_anno": format_euro(risparmio[0]),
            "consumi_annui": f"{consumo_annuo} kWh",
            "costi_annui": format_euro(bolletta_annua_val),
            "risparmi_primo": primo_risparmio,
            "risparmi_altri": risparmio_list.iloc[1:],
            "totale_risparmiato": totale_risparmio,
            "risparmio_energetico_trainante": risparmio_energetico_trainante,
            "tariffa_corrente": str(round(tariffa_energia*100, 1)) + " €/MWh"
        }

    return render(request, 'index.html', data)



# Funzione per formattare i valori come valuta in euro
def format_euro(value):
    return f"{value:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.')

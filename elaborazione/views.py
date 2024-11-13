from django.shortcuts import render
from .models import Impianto
from decimal import Decimal, InvalidOperation
import pandas as pd
#questa è la versione corrente
def home(request):
    return render(request, 'index.html')

# Percorsi ai CSV
CSV_PATH = "Cartel3.csv"
ALIQUOTA_CSV_PATH = "aliqutoconcessa.csv"

# Carica il CSV delle aliquote concessa
aliquota_df = pd.read_csv(ALIQUOTA_CSV_PATH)

# Funzione per formattare i valori come valuta in euro
def format_euro(value):
    return f"{value:,.2f} €".replace(',', 'X').replace('.', ',').replace('X', '.')

# Funzione per determinare la fascia di copertura
def determine_fascia_copertura(copertura_impianto_euro):
    if copertura_impianto_euro <= Decimal('2500000'):
        return "Valore_2.5M"
    elif copertura_impianto_euro <= Decimal('10000000'):
        return "Valore_10M"
    elif copertura_impianto_euro <= Decimal('50000000'):
        return "Valore_50M"
    else:
        raise ValueError("Copertura impianto superiore a 50.000.000 € non gestita.")

# Funzione per calcolare l'aliquota concessa in percentuale
def calculate_aliquota_concessa_percentuale(potenza_installata, taglia_impianto_coperto, risparmio_energetico_percentuale):
    # Calcola la copertura impianto in euro
    copertura_impianto_euro = potenza_installata * taglia_impianto_coperto
    
    # Determina la fascia di copertura
    try:
        fascia_copertura = determine_fascia_copertura(copertura_impianto_euro)
    except ValueError as e:
        return f"Errore: {e}"
    
    # Seleziona la riga corrispondente al risparmio energetico
    if risparmio_energetico_percentuale == 5:
        aliquota_row = aliquota_df.iloc[0]  # Prima riga per 5%
    elif risparmio_energetico_percentuale == 10:
        aliquota_row = aliquota_df.iloc[1]  # Seconda riga per 10%
    elif risparmio_energetico_percentuale == 15:
        aliquota_row = aliquota_df.iloc[2]  # Terza riga per 15%
    else:
        return "Percentuale di risparmio energetico non valida. Scegli tra 5, 10 o 15."
    
    # Estrai l'aliquota concessa in percentuale dalla fascia di copertura
    try:
        aliquota_percentuale_str = aliquota_row[fascia_copertura]
        aliquota_percentuale = Decimal(aliquota_percentuale_str.replace('%', '').replace(',', '.')) / 100
    except (InvalidOperation, KeyError) as e:
        return f"Errore nella conversione dell'aliquota percentuale: {e}"
    
    return aliquota_percentuale

def calcola_somma(request):
    print("Session data after saving in calcola_somma:", request.session.items())

    # Variabili iniziali
    costo_impianto = ''
    storage = ''
    credito_contributo = '0 €'
    bene_trainante2 = ''
    costo_totale_impianto = '0 €'
    credito_fiscale_5_0 = '0 €'
    consumi_annui = ''
    produzione_annua = '0 kWh/kWp'
    tipologia_pannelli = '1.0'
    costi_annui = ''
    potenza_installata = ''
    aliquota_concessa = '0%'
    Bolletta_primo_annuo = '0 €'
    risparmio_primo_annuo = '0 €'
    decadimento_annuale = {}
    risparmio_annuo = {}
    error_message = None

    # Inizializzazione valori decimali
    costo_impianto_val = Decimal('0')
    storage_val = Decimal('0')
    credito_contributo_val = Decimal('0')
    bene_trainante2_val = Decimal('0')
    consumi_annui_val = Decimal('0')
    produzione_annua_val = Decimal('0')
    costi_annui_val = Decimal('0')
    potenza_installata_val = Decimal('0')
    aliquota_concessa_val = Decimal('0')
    Bolletta_val = Decimal('0')
    
    
    if request.method == 'POST':
        
        
        
        calcolo_solo = request.POST.get('calcolo_solo') == 'True'
        costo_impianto = request.POST.get('costo_impianto', '')
        storage = request.POST.get('storage', '')
        bene_trainante2 = request.POST.get('bene_trainante2', '')
        consumi_annui = request.POST.get('consumiAnnui', '')
        produzione_annua = request.POST.get('produzione_annua', '0')
        tipologia_pannelli = request.POST.get('tipologia_pannelli', '1.0')
        costi_annui = request.POST.get('costiAnnui', '')
        potenza_installata = request.POST.get('potenza_installata', '0')
        risparmio_energetico_percentuale = int(request.POST.get('risparmio_energetico', '0'))
        # Nota: Ho cambiato 'aliquota_concessa' in 'risparmio_energetico' per chiarezza

        try:
            # Conversione dei valori
            costo_impianto_val = Decimal(costo_impianto.replace('€', '').replace('.', '').replace(',', '.')) if costo_impianto else Decimal('0')
            storage_val = Decimal(storage.replace('€', '').replace('.', '').replace(',', '.')) if storage else Decimal('0')
            bene_trainante2_val = Decimal(bene_trainante2.replace('€', '').replace('.', '').replace(',', '.')) if bene_trainante2 else Decimal('0')
            consumi_annui_val = Decimal(consumi_annui.replace('€', '').replace('.', '').replace(',', '.')) if consumi_annui else Decimal('0')
            produzione_annua_val = Decimal(produzione_annua.replace('kWh/kWp', '').replace(',', '.')) if produzione_annua else Decimal('0')
            costi_annui_val = Decimal(costi_annui.replace('€', '').replace('.', '').replace(',', '.')) if costi_annui else Decimal('0')
            potenza_installata_val = Decimal(potenza_installata.replace('kW', '').replace(',', '.')) if potenza_installata else Decimal('0')
            tipologia_pannelli_val = Decimal(tipologia_pannelli)
            
            
              # Salva i dati nella sessione
            request.session['costo_impianto'] = costo_impianto
            request.session['storage'] = storage
            request.session['credito_contributo'] = credito_contributo
            request.session['bene_trainante2'] = bene_trainante2
            request.session['costo_totale_impianto'] = costo_totale_impianto
            request.session['credito_fiscale_5_0'] = credito_fiscale_5_0
            request.session['consumi_annui'] = consumi_annui
            request.session['produzione_annua'] = produzione_annua
            request.session['tipologia_pannelli'] = tipologia_pannelli
            request.session['costi_annui'] = costi_annui
            request.session['potenza_installata'] = potenza_installata
            request.session['Bolletta_primo_annuo'] = Bolletta_primo_annuo
            request.session['risparmio_primo_annuo'] = risparmio_primo_annuo
            request.session.save()
            print("Dopo l'assegnazione dei dati di sessione:", request.session.items())
           
            
    
            # Calcolo del costo totale dell'impianto
            somma_val = costo_impianto_val + storage_val
            costo_totale_impianto = format_euro(somma_val)
    
            # Calcolo "Bolletta primo anno"
            if consumi_annui_val > Decimal('0'):
                Bolletta_val = (consumi_annui_val - produzione_annua_val) * costi_annui_val / consumi_annui_val
                Bolletta_primo_annuo = format_euro(Bolletta_val)
            else:
                Bolletta_primo_annuo = "0 €"
    
            # Calcolo del credito fiscale 5.0
            credito_fiscale_5_0_val = credito_contributo_val + storage_val + bene_trainante2_val
            credito_fiscale_5_0 = format_euro(credito_fiscale_5_0_val)
    
            # Calcolo del risparmio primo anno
            risparmio_primo_annuo_val = credito_fiscale_5_0_val + Bolletta_val
            risparmio_primo_annuo = format_euro(risparmio_primo_annuo_val)
    
            # Lettura del CSV e ricerca di impianto coperto
            df = pd.read_csv(CSV_PATH)
            impianto_coperto_row = df[df['min'] <= float(potenza_installata_val)].iloc[-1:]
    
            if not impianto_coperto_row.empty:
                    impianto_coperto_value = impianto_coperto_row['copertura'].values[0]
                    impianto_coperto_val = Decimal(int(impianto_coperto_value))

            else:
                error_message = "Potenza installata non trovata nel CSV"
                impianto_coperto_val = Decimal('0')
    
            if impianto_coperto_val > Decimal('0'):
                # Calcola l'aliquota concessa in percentuale
                aliquota_percentuale = calculate_aliquota_concessa_percentuale(
                    potenza_installata_val,
                    impianto_coperto_val,
                    risparmio_energetico_percentuale
                )
                
                if isinstance(aliquota_percentuale, Decimal):
                    aliquota_concessa_val = aliquota_percentuale
                    aliquota_concessa = f"{aliquota_concessa_val * 100}%"
                else:
                    # In caso di errore durante il calcolo
                    error_message = aliquota_percentuale
                    aliquota_concessa_val = Decimal('0')
            else:
                error_message = "Copertura impianto non valida."
                aliquota_concessa_val = Decimal('0')
    
            # Calcolo decadimento produzione e risparmio energetico per ogni anno dal 2 al 10
            for anno in range(2, 11):
                # Calcolo della produzione annua con decadimento
                decadimento = produzione_annua_val * (1 - (Decimal('0.005') * (anno - 1)))
                decadimento_annuale[anno] = format_euro(decadimento) + " kWh/kWp"
                
                # Calcolo del risparmio energetico per l'anno corrente
                if consumi_annui_val > Decimal('0'):
                    risparmio_energetico = (consumi_annui_val - decadimento) * costi_annui_val / consumi_annui_val
                    risparmio_annuo[anno] = format_euro(risparmio_energetico)
                else:
                    risparmio_annuo[anno] = "0 €"
    
            # Salvataggio condizionale
            if not calcolo_solo:
                nuovo_impianto = Impianto.objects.create(
                    costo_impianto=costo_impianto_val,
                    storage=storage_val,
                    produzione_annua=produzione_annua_val,
                )
                nuovo_impianto.save()
                
                
          
            
            
    
        except (InvalidOperation, ValueError, KeyError, IndexError) as e:
            error_message = f"Errore nei dati inseriti o nella lettura del CSV: {e}. Assicurati di inserire valori validi."
    
    # Passa i valori formattati al template
    return render(request, 'index.html', {
        'costo_impianto': format_euro(costo_impianto_val) if costo_impianto else '',
        'storage': format_euro(storage_val) if storage else '',
        'credito_contributo': credito_contributo,
        'bene_trainante2': format_euro(bene_trainante2_val) if bene_trainante2 else '',
        'costo_totale_impianto': costo_totale_impianto,
        'credito_fiscale_5_0': credito_fiscale_5_0,
        'creditoFiscale': credito_fiscale_5_0,
        'consumi_annui': format_euro(consumi_annui_val) if consumi_annui else '',
        'produzione_annua': produzione_annua,
        'risparmio_primo_annuo': risparmio_primo_annuo,
        'tipologia_pannelli': tipologia_pannelli,
        'costi_annui': format_euro(costi_annui_val) if costi_annui else '',
        'Bolletta_primo_annuo': Bolletta_primo_annuo,
        'potenza_installata': f"{potenza_installata_val} kW",
        'aliquota_concessa': aliquota_concessa,
        
        # Dizionari con il decadimento della produzione e il risparmio energetico per ogni anno
        'decadimento_annuale': decadimento_annuale,
        'risparmio_annuo': risparmio_annuo,
        
        'error_message': error_message,
    })
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
import fitz  # PyMuPDF
import io
import os
from django.http import HttpResponse
from django.shortcuts import render
import base64


# Funzione per formattare gli importi in euro
def format_euro(value):
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Funzione per generare l'anteprima
def generate_preview_with_text_overlay(request):
    # Dati salvati nella sessione o valori predefiniti
    context = {
        'costo_impianto': {'value': request.session.get('costo_impianto', ''), 'x': 900, 'y': 390},
        'potenzaInstallata': {'value': request.session.get('potenza_installata', 'DA PM'), 'x': 690, 'y': 900},
        'beneTrainante1': {'value': request.session.get('bene_trainante1', 'da inserire'), 'x': 900, 'y': 530},
        'costoTotaleImpianto': {'value': request.session.get('costo_totale_impianto', 'POTENZA INSTALLATA X COSTO COPERTO MAX(POTENZA IMPIANTO)'), 'x': 690, 'y': 690},
        'produzione_annua': {'value': request.session.get('produzione_annua', 'nulla'), 'x': 640, 'y': 1300},
        'tipologia_pannelli': {'value': request.session.get('tipologia_pannelli', '1.0'), 'x': 690, 'y': 1450},
        'credito_contributo': {'value': request.session.get('credito_contributo', '0 €'), 'x': 1760, 'y': 390},
        'storage': {'value': request.session.get('storage', 'da definire'), 'x': 1740, 'y': 450},
        'bene_trainante2': {'value': request.session.get('bene_trainante2', 'da inserire'), 'x': 1740, 'y': 515},
        'credito_fiscale_5_0': {'value': request.session.get('credito_fiscale_5_0', '0 €'), 'x':  1490, 'y': 690},
        'aliquota_concessa': {'value': request.session.get('aliquota_concessa', '0%'), 'x': 1490, 'y': 1300},
        'risparmio_energetico': {'value': request.session.get('risparmio_energetico', '5'), 'x': 1490, 'y': 1100},
        'creditoFiscale': {'value': request.session.get('creditoFiscale', '0 €'), 'x': 2550, 'y': 381},
        'Bolletta_primo_annuo': {'value': request.session.get('Bolletta_primo_annuo', '0 €'), 'x': 2550, 'y': 460},
        'risparmio_primo_annuo': {'value': request.session.get('risparmio_primo_annuo', '0 €'), 'x': 2280, 'y': 690},
    }
 # Definisci gli stili per ogni campo
    field_styles = {
        'costo_impianto': {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255)  # Rosso
        },
        'potenzaInstallata': {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (6, 143, 197)  #Ble
        },
        'beneTrainante1': {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255)   # bianco
        },
        
        'costoTotaleImpianto' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 40,
            'color': (6, 143, 197)   # Blu
        },
        
        'produzione_annua': {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (6, 143, 197)  #Ble
        },
        
        'storage' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255) #Bianco
            
        },
        
        'credito_fiscale_5_0' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 40,
            'color': (247, 39, 39)   #Rosso
            
        },
        
        'bene_trainante2' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255)   #Bianco
            
        },
        
        'aliquota_concessa' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (247, 39, 39) #Rosso
            
        },
        
        'creditoFiscale' :{
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255)   
            
            
        },
        
        'risparmio_energetico' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (247, 39, 39) #Rosso
        },
        
        'Bolletta_primo_annuo' :{
             'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255) #bianco
        },
        
        'risparmio_primo_annuo' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 40,
            'color': (44, 183, 44) #verde
        },
        
        'credito_contributo':{
              'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255) 
        },
        
        'tipologia_pannelli' :{
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (6, 143, 197)
        }
        
        
      }
    
    # Carica l'immagine di base
    base_pdf_path = "C:\\Users\\Giulio Lazzaro\\Desktop\\EPC_5_0\\Modulo commerciale 04112024.pdf"
    doc = fitz.open(base_pdf_path)
    page = doc.load_page(0)
    pix = page.get_pixmap(dpi=150)
    temp_image_path = "temp_base_image.png"
    pix.save(temp_image_path)
    
    background_img = Image.open(temp_image_path).convert("RGBA")
    text_overlay = Image.new("RGBA", background_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(text_overlay)
    
    for field, settings in context.items():
        x = settings['x']
        y = settings['y']
        value = settings['value']
        
        # Ottieni lo stile per il campo corrente
        style = field_styles.get(field, {})
        font_path = style.get('font_path', 'C:\\Windows\\Fonts\\Arial.ttf')
        font_size = style.get('font_size', 24)
        color = style.get('color', (0, 0, 0, 255))  # Nero come default
        
        # Crea il font
        font = ImageFont.truetype(font_path, font_size)
        
        # Disegna il testo con il font e il colore specificati
        draw.text((x, y), value, font=font, fill=color)
    
    combined_img = Image.alpha_composite(background_img, text_overlay)
    combined_img_rgb = combined_img.convert("RGB")
    
    buffer = io.BytesIO()
    combined_img_rgb.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    os.remove(temp_image_path)
    doc.close()
    
    return render(request, 'anteprima.html', {'image_base64': image_base64, 'context': context})

# Funzione per scaricare il PDF con overlay di testo
def download_pdf_with_text_overlay(request):
    # Recupera dati dalla sessione per il PDF
    context = {
      'costo_impianto': {'value': request.session.get('costo_impianto', ''), 'x': 900, 'y': 390},
        'potenzaInstallata': {'value': request.session.get('potenza_installata', 'DA PM'), 'x': 690, 'y': 900},
        'beneTrainante1': {'value': request.session.get('bene_trainante1', 'da inserire'), 'x': 900, 'y': 530},
        'costoTotaleImpianto': {'value': request.session.get('costo_totale_impianto', 'POTENZA INSTALLATA X COSTO COPERTO MAX(POTENZA IMPIANTO)'), 'x': 690, 'y': 690},
        'produzione_annua': {'value': request.session.get('produzione_annua', 'nulla'), 'x': 640, 'y': 1300},
        'tipologia_pannelli': {'value': request.session.get('tipologia_pannelli', '1.0'), 'x': 690, 'y': 1450},
        'credito_contributo': {'value': request.session.get('credito_contributo', '0 €'), 'x': 1760, 'y': 390},
        'storage': {'value': request.session.get('storage', 'da definire'), 'x': 1740, 'y': 450},
        'bene_trainante2': {'value': request.session.get('bene_trainante2', 'da inserire'), 'x': 1740, 'y': 515},
        'credito_fiscale_5_0': {'value': request.session.get('credito_fiscale_5_0', '0 €'), 'x':  1490, 'y': 690},
        'aliquota_concessa': {'value': request.session.get('aliquota_concessa', '0%'), 'x': 1490, 'y': 1300},
        'risparmio_energetico': {'value': request.session.get('risparmio_energetico', '5'), 'x': 1490, 'y': 1100},
        'creditoFiscale': {'value': request.session.get('creditoFiscale', '0 €'), 'x': 2550, 'y': 381},
        'Bolletta_primo_annuo': {'value': request.session.get('Bolletta_primo_annuo', '0 €'), 'x': 2550, 'y': 460},
        'risparmio_primo_annuo': {'value': request.session.get('risparmio_primo_annuo', '0 €'), 'x': 2280, 'y': 690},
       }

    field_styles = {
        'costo_impianto': {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255)  # Rosso
        },
        'potenzaInstallata': {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (6, 143, 197)  #Ble
        },
        'beneTrainante1': {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255)   # bianco
        },
        
        'costoTotaleImpianto' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 40,
            'color': (6, 143, 197)   # Blu
        },
        
        'produzione_annua': {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (6, 143, 197)  #Ble
        },
        
        'storage' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255) #Bianco
            
        },
        
        'credito_fiscale_5_0' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 40,
            'color': (247, 39, 39)   #Rosso
            
        },
        
        'bene_trainante2' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255)   #Bianco
            
        },
        
        'aliquota_concessa' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (247, 39, 39) #Rosso
            
        },
        
        'creditoFiscale' :{
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255)   
            
            
        },
        
        'risparmio_energetico' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (247, 39, 39) #Rosso
        },
        
        'Bolletta_primo_annuo' :{
             'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255) #bianco
        },
        
        'risparmio_primo_annuo' : {
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 40,
            'color': (44, 183, 44) #verde
        },
        
        'credito_contributo':{
              'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 30,
            'color': (255, 255,  255) 
        },
        
        'tipologia_pannelli' :{
            'font_path': 'C:\\Windows\\Fonts\\Arialbd.ttf',
            'font_size': 35,
            'color': (6, 143, 197)
        }
        
        
      }
    
    
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for field, settings in context.items():
        pdf.set_xy(settings['x'], settings['y'])
        pdf.cell(200, 10, txt=settings['value'], border=0, align='C')

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    response = HttpResponse(pdf_output, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="Report_Intestato.pdf"'
    return response

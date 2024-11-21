# kgstatistikk.py
import matplotlib
matplotlib.use('Agg')  # Sett backend til 'Agg' før du importerer pyplot
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

def generer_statistikk(valgt_kommune):
    # Les inn dataene fra Excel-filen, hopp over de første 3 radene
    kgdata = pd.read_excel("ssb-barnehager-2015-2023-alder-1-2-aar.xlsm", skiprows=3)
    
    # Sjekk kolonnenavnene
    print("Kolonnenavn i dataene:", kgdata.columns.tolist())
    
    # Anta at første kolonne er kommunenavn
    if kgdata.columns[0] == 'Unnamed: 0':
        kgdata.rename(columns={'Unnamed: 0': 'Kommune'}, inplace=True)
    
    # Sjekk at kolonnen 'Kommune' eksisterer
    if 'Kommune' not in kgdata.columns:
        print("Kolonnen 'Kommune' finnes ikke i dataene.")
        return None

    # Filtrer dataene for valgt kommune
    kgdata['Kommune'] = kgdata['Kommune'].astype(str)
    valgt_kommune_data = kgdata[kgdata['Kommune'].str.contains(valgt_kommune, na=False, case=False, regex=False)]

    if valgt_kommune_data.empty:
        print(f"Ingen data funnet for {valgt_kommune}.")
        return None
    else:
        # Hent årstallene fra kolonnene
        kolonner_yrs = [col for col in kgdata.columns if col not in ['Kommune']]
        
        # Konverter årstallene til strenger hvis nødvendig
        kolonner_yrs = [str(col) for col in kolonner_yrs]
        
        # Velg nødvendige kolonner
        valgt_kommune_data = valgt_kommune_data[['Kommune'] + kolonner_yrs].dropna(subset=kolonner_yrs)
        
        if valgt_kommune_data.empty:
            print(f"{valgt_kommune} har ingen verdier for de valgte årene.")
            return None
        else:
            # Konverter prosentandeler til tall
            valgt_kommune_data.replace({'.': None}, inplace=True)
            for col in kolonner_yrs:
                valgt_kommune_data[col] = valgt_kommune_data[col].astype(str).str.replace(',', '.').astype(float)
            
            yr = [int(y) for y in kolonner_yrs]
            prosentandeler = valgt_kommune_data[kolonner_yrs].values.flatten()
            
            if prosentandeler.size == 0:
                print(f"Ingen prosentandeler funnet for {valgt_kommune}.")
                return None
            else:
                # Bygg diagrammet
                plt.figure(figsize=(10, 6))
                plt.plot(yr, prosentandeler, marker='o', linestyle='-', color='orange', label=valgt_kommune)
                plt.xticks(yr)
                plt.xlabel('År')
                plt.ylabel('Prosentandel barn i barnehage')
                plt.title(f'Prosentandel barn i 1-2 års alderen i barnehagen for {valgt_kommune} (2015-2023)')
                plt.grid()
                plt.legend()
                plt.tight_layout()
                
                # Lagre bildet i en bytes buffer
                img = io.BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                plot_url = base64.b64encode(img.getvalue()).decode()
                plt.close()
                return plot_url

def hent_kommuneliste():
    kgdata = pd.read_excel("ssb-barnehager-2015-2023-alder-1-2-aar.xlsm", skiprows=3)
    
    # Anta at første kolonne er kommunenavn
    if kgdata.columns[0] == 'Unnamed: 0':
        kgdata.rename(columns={'Unnamed: 0': 'Kommune'}, inplace=True)
    
    # Sjekk at kolonnen 'Kommune' eksisterer
    if 'Kommune' not in kgdata.columns:
        print("Kolonnen 'Kommune' finnes ikke i dataene.")
        return []
    
    kommuner = kgdata['Kommune'].dropna().unique()
    return sorted(kommuner)

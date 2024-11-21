# kgcontroller.py
import pandas as pd
from dbexcel import barnehage, forelder, barn, soknad
from kgmodel import Foresatt, Barn, Soknad, Barnehage

# CRUD Methods

# Create (Insert) Methods
def insert_foresatt(f):
    global forelder
    new_id = forelder['foresatt_id'].max() + 1 if not forelder.empty else 1
    forelder = pd.concat([forelder, pd.DataFrame([{
        'foresatt_id': new_id,
        'foresatt_navn': f.foresatt_navn,
        'foresatt_adresse': f.foresatt_adresse,
        'foresatt_tlfnr': f.foresatt_tlfnr,
        'foresatt_pnr': f.foresatt_pnr
    }])], ignore_index=True)
    f.foresatt_id = new_id  # Sett ID i objektet
    return forelder

def insert_barn(b):
    global barn
    new_id = barn['barn_id'].max() + 1 if not barn.empty else 1
    barn = pd.concat([barn, pd.DataFrame([{
        'barn_id': new_id,
        'barn_pnr': b.barn_pnr
    }])], ignore_index=True)
    b.barn_id = new_id  # Sett ID i objektet
    return barn

def insert_soknad(s):
    global soknad
    new_id = soknad['sok_id'].max() + 1 if not soknad.empty else 1
    soknad = pd.concat([soknad, pd.DataFrame([{
        'sok_id': new_id,
        'foresatt_1': s.foresatt_1.foresatt_id,
        'foresatt_2': s.foresatt_2.foresatt_id,
        'barn_1': s.barn_1.barn_id,
        'fr_barnevern': s.fr_barnevern,
        'fr_sykd_familie': s.fr_sykd_familie,
        'fr_sykd_barn': s.fr_sykd_barn,
        'fr_annet': s.fr_annet,
        'barnehager_prioritert': s.barnehager_prioritert,
        'sosken__i_barnehagen': s.sosken__i_barnehagen,
        'tidspunkt_oppstart': s.tidspunkt_oppstart,
        'brutto_inntekt': s.brutto_inntekt,
        'status': s.status  # Lagre status
    }])], ignore_index=True)
    s.sok_id = new_id  # Sett ID i objektet
    return soknad

# Read Methods
def select_alle_barnehager():
    """Returnerer en liste med alle barnehager."""
    return barnehage.apply(lambda r: Barnehage(
        r['barnehage_id'],
        r['barnehage_navn'],
        r['barnehage_antall_plasser'],
        r['barnehage_ledige_plasser']
    ), axis=1).to_list()

def select_alle_foresatte():
    """Returnerer en liste med alle foresatte."""
    global forelder
    return forelder.to_dict(orient='records')

def select_alle_barn():
    """Returnerer en liste med alle barn."""
    global barn
    return barn.to_dict(orient='records')

def select_alle_soknader():
    """Henter alle søknader og returnerer dem som en liste av ordbøker."""
    global soknad
    soknader = soknad.to_dict(orient='records')
    return soknader

# Function to convert form data to Soknad object
def form_to_object_soknad(sd):
    """Konverterer form data til et Soknad-objekt."""
    foresatt_1 = Foresatt(
        0,
        sd.get('navn_forelder_1'),
        sd.get('adresse_forelder_1'),
        sd.get('tlf_nr_forelder_1'),
        sd.get('personnummer_forelder_1')
    )
    insert_foresatt(foresatt_1)

    foresatt_2 = Foresatt(
        0,
        sd.get('navn_forelder_2'),
        sd.get('adresse_forelder_2'),
        sd.get('tlf_nr_forelder_2'),
        sd.get('personnummer_forelder_2')
    )
    insert_foresatt(foresatt_2)

    barn_1 = Barn(0, sd.get('personnummer_barnet_1'))
    insert_barn(barn_1)

    soknad = Soknad(
        0,
        foresatt_1,
        foresatt_2,
        barn_1,
        sd.get('fortrinnsrett_barnevern', ''),
        sd.get('fortrinnsrett_sykdom_i_familien', ''),
        sd.get('fortrinnsrett_sykdome_paa_barnet', ''),
        sd.get('fortrinssrett_annet', ''),
        sd.get('liste_over_barnehager_prioritert_5'),
        sd.get('har_sosken_som_gaar_i_barnehagen', ''),
        sd.get('tidspunkt_for_oppstart', ''),
        sd.get('brutto_inntekt_husholdning', ''),
        ''  # Status vil bli satt etter behandling
    )

    return soknad

# Function to process the application
def behandle_soknad(s):
    global barnehage, soknad

    # Konverter barnehager_prioritert til int
    try:
        prioritet_id = int(s.barnehager_prioritert)
    except ValueError:
        print("Feil: 'barnehager_prioritert' kunne ikke konverteres til int.")
        s.status = "AVSLAG"
        return s.status

    # Hent valgt barnehage
    valgt_barnehage = barnehage[barnehage['barnehage_id'] == prioritet_id]

    if valgt_barnehage.empty:
        print("Barnehagen finnes ikke.")
        s.status = "AVSLAG"
        return s.status

    ledige_plasser = valgt_barnehage['barnehage_ledige_plasser'].iloc[0]

    # Sjekk for fortrinnsrett
    har_fortrinnsrett = any([
        s.fr_barnevern == 'on',
        s.fr_sykd_familie == 'on',
        s.fr_sykd_barn == 'on',
        s.fr_annet != '',
        s.sosken__i_barnehagen == 'on'
    ])

    # Bestem status basert på ledige plasser og fortrinnsrett
    if ledige_plasser > 0 or har_fortrinnsrett:
        s.status = "TILBUD"
        # Reduser antall ledige plasser
        barnehage.loc[valgt_barnehage.index[0], 'barnehage_ledige_plasser'] -= 1
    else:
        s.status = "AVSLAG"

    # Sett inn søknaden i DataFrame
    insert_soknad(s)

    return s.status

def commit_all():
    kgdata = pd.ExcelFile("kgdata.xlsx")
    print("Ark i kgdata.xlsx:", kgdata.sheet_names)

    try:
        barnehage = pd.read_excel(kgdata, 'barnehage')
        forelder = pd.read_excel(kgdata, 'foresatt')
        barn = pd.read_excel(kgdata, 'barn')
        soknad = pd.read_excel(kgdata, 'soknad')
    except ValueError as e:
        print("Feil ved lesing av ark:", e)
        return

    # ... eventuelle oppdateringer på dataene ...

    # Lagre dataene tilbake til Excel-filen
    with pd.ExcelWriter("kgdata.xlsx", mode='w') as writer:
        barnehage.to_excel(writer, sheet_name='barnehage', index=False)
        forelder.to_excel(writer, sheet_name='foresatt', index=False)
        barn.to_excel(writer, sheet_name='barn', index=False)
        soknad.to_excel(writer, sheet_name='soknad', index=False)




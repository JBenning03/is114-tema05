# initiate_db.py
import pandas as pd

def initiate_db(db_name):
    # Les inn barnehagene fra Excel-filen
    barnehage = pd.read_excel("kgdata.xlsx", sheet_name='barnehage')
    
    # Opprett tomme DataFrames for forelder, barn og søknad
    kolonner_forelder = ['foresatt_id', 'foresatt_navn', 'foresatt_adresse', 'foresatt_tlfnr', 'foresatt_pnr']
    kolonner_barn = ['barn_id', 'barn_pnr']
    kolonner_soknad = [
        'sok_id', 'foresatt_1', 'foresatt_2', 'barn_1', 'fr_barnevern', 'fr_sykd_familie',
        'fr_sykd_barn', 'fr_annet', 'barnehager_prioritert', 'sosken_i_barnehagen',
        'tidspunkt_oppstart', 'brutto_inntekt'
    ]
    
    forelder = pd.DataFrame(columns=kolonner_forelder)
    barn = pd.DataFrame(columns=kolonner_barn)
    soknad = pd.DataFrame(columns=kolonner_soknad)
    
    # Lagre DataFrames til Excel-filen
    with pd.ExcelWriter(db_name) as writer:
        forelder.to_excel(writer, sheet_name='foresatt', index=False)
        barnehage.to_excel(writer, sheet_name='barnehage', index=False)
        barn.to_excel(writer, sheet_name='barn', index=False)
        soknad.to_excel(writer, sheet_name='soknad', index=False)


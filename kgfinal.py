# kg.py

from flask import Flask, url_for, render_template, request, redirect, session
from kgmodel import Foresatt, Barn, Soknad, Barnehage
from kgcontroller import (
    form_to_object_soknad,
    insert_soknad,
    commit_all,
    select_alle_barnehager,
    behandle_soknad,
    select_alle_soknader,
    select_alle_foresatte,
    select_alle_barn
)
from kgstatistikk import generer_statistikk, hent_kommuneliste
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'  # Nødvendig for session-håndtering

# Hjemmeside
@app.route('/')
def index():
    return render_template('index.html')

# kg.py

@app.route('/statistikk')
def statistikk():
    kommune = '1867 Bø'  # Bruk det eksakte kommunenavnet fra dataene
    img = generer_statistikk(kommune)
    if img:
        return render_template('statistikk_resultat.html', kommune=kommune, plot_url=img)
    else:
        feil = f"Ingen data tilgjengelig for {kommune}."
        return render_template('statistikk_resultat.html', kommune=kommune, feil=feil)


# Søknader-rute
@app.route('/soknader')
def vis_soknader():
    # Hent alle søknader fra databasen
    soknader = select_alle_soknader()
    # Hent alle barnehager for å vise navn i stedet for ID
    barnehager = select_alle_barnehager()
    barnehager_dict = {str(b.barnehage_id): b.barnehage_navn for b in barnehager}
    return render_template('soknader.html', soknader=soknader, barnehager_dict=barnehager_dict)

# Barnehager-rute
@app.route('/barnehager')
def barnehager():
    information = select_alle_barnehager()
    return render_template('barnehager.html', data=information)

# Behandle søknad
@app.route('/behandle', methods=['GET', 'POST'])
def behandle():
    if request.method == 'POST':
        sd = request.form
        soknad = form_to_object_soknad(sd)
        
        # Behandle søknaden for å få umiddelbar respons
        status = behandle_soknad(soknad)
        
        # Send status til svar.html
        session['status'] = status
        return redirect(url_for('svar'))
    else:
        # Hent alle barnehager for dropdown
        barnehager = select_alle_barnehager()
        return render_template('soknad.html', barnehager=barnehager)

# Svar-side
@app.route('/svar')
def svar():
    # Hent status fra session og send den til svar.html
    status = session.get('status', 'Ingen status tilgjengelig')
    return render_template('svar.html', status=status)

# Commit-rute
@app.route('/commit')
def commit():
    commit_all()  # Lagre alle data til Excel

    # Hent oppdatert data fra Excel-filen
    barnehager = select_alle_barnehager()
    foresatte = select_alle_foresatte()
    barn_liste = select_alle_barn()
    soknader = select_alle_soknader()

    return render_template(
        'commit.html',
        barnehager=barnehager,
        foresatte=foresatte,
        barn=barn_liste,
        soknader=soknader
    )

if __name__ == "__main__":
    app.run(port=5001)  # Kjører Flask på port 5001

# dbexcel.py
import pandas as pd

kgdata = pd.ExcelFile("kgdata.xlsx")
barnehage = pd.read_excel(kgdata, "barnehage")
forelder = pd.read_excel(kgdata, 'foresatt')
barn = pd.read_excel(kgdata, 'barn')
soknad = pd.read_excel(kgdata, 'soknad')

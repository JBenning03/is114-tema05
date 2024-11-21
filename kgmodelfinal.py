# kgmodel.py
from dataclasses import dataclass

@dataclass
class Foresatt:
    foresatt_id: int
    foresatt_navn: str
    foresatt_adresse: str
    foresatt_tlfnr: str
    foresatt_pnr: str

@dataclass
class Barn:
    barn_id: int
    barn_pnr: str

@dataclass
class Barnehage:
    barnehage_id: int
    barnehage_navn: str
    barnehage_antall_plasser: int
    barnehage_ledige_plasser: int

@dataclass
class Soknad:
    sok_id: int
    foresatt_1: Foresatt
    foresatt_2: Foresatt
    barn_1: Barn
    fr_barnevern: str
    fr_sykd_familie: str
    fr_sykd_barn: str
    fr_annet: str
    barnehager_prioritert: str
    sosken__i_barnehagen: str
    tidspunkt_oppstart: str
    brutto_inntekt: int
    status: str  # Added status field

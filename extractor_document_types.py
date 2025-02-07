from enum import Enum


class DocumentROIs(Enum):

    CARTA_IDENTITA_ELETTRONICA = {
        "id": [(700, 20, 300, 75)],
        "comune": [(120, 166, 430, 35)],
        "cognome" : [(250, 215, 430, 35)],
        "nome": [(290, 261, 430, 35)],
        "luogo_data": [(270, 325, 700, 30)],
        "sesso": [(300, 370, 110, 43)],
        "altezza": [(420, 370, 200, 43)],
        "nazionalità": [(620, 370, 160, 43)],
        "data_emissione": [(300, 413, 250, 48)],
        "data_scadenza": [(630, 413, 250, 48)]
    }

    CARTA_IDENTITA_ELETTRONICA_RETRO = {
        "codice_fiscale": [(30, 100, 380, 80)],
        "indirizzo_residenza": [(30, 170, 380, 80)],
        "MRZ": [(15, 450, 950, 190)], #img.size() = [986, 657]
        "first_row_mrz" : [(15, 460, 800, 70)],
        "second_row_mrz": [(15, 510, 800, 70)],
        "third_row_mrz": [(15, 570, 800, 70)],
        #"estremi_atto_nascita": [(300, 370, 110, 43)],
        # "nazionalità": [(620, 370, 160, 43)],
        # "data_emissione": [(300, 413, 250, 48)],
        # "data_scadenza": [(630, 413, 250, 48)]
    }

    CARTA_IDENTITA_CARTACEA = {
        "cognome": [(50, 50, 300, 50)],
        "nome": [(50, 90, 300, 40)],
        "data_nascita" : [(50, 120, 300, 40)],
        "luogo_nascita": [(50, 190, 300, 40)],
        "cittadinanza": [(50, 220, 400, 40)],
        "residenza_citta": [(50, 250, 400, 40)],
        "residenza_via": [(50, 280, 400, 40)],
        "stato_civile": [(50, 310, 300, 40)],
        "professione": [(50, 340, 300, 40)],
        "altezza": [(150, 410, 200, 40)],
        "capelli": [(150, 450, 200, 40)],
        "occhi": [(150, 480, 300, 40)],
        # "segni_particolari": [(70, 510, 350, 150)]
    }

    CARTA_IDENTITA_CARTACEA_RETRO = {
        "data_scadenza": [(80, 180, 250, 80)],
        "id": [(140, 430, 300, 60)],
        "comune_emissione" : [(565, 230, 300, 80)],
        "id2": [(670, 360, 250, 60)],
        "cognome": [(550, 470, 300, 40)],
        "nome": [(550, 510, 300, 40)],
    }

    PATENTE = {
        "cognome": [(320, 70, 300, 60)],
        "nome": [(320, 120, 300, 60)],
        "luogo_data" : [(320, 160, 400, 60)],
        "data_emissione": [(323, 200, 200, 60)],
        "data_scadenza": [(323, 250, 300, 60)],
        "boh": [(320, 300, 300, 60)]
    }

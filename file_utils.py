import re
import cv2
import numpy as np


def save_temp_image(image, temp_image_path):
    cv2.imwrite(temp_image_path, image)

 
def pulisci_data(data):
    if data == None or data == "" or data == " ":
        data_corretta = None
    else:
        data_pulita = re.sub(r'\D', '', data)

        if len(data_pulita) != 8:
            data_corretta = None
        else:
            giorno = data_pulita[:2]
            mese = data_pulita[2:4]
            anno = data_pulita[4:]
            data_corretta = f"{giorno}.{mese}.{anno}"

    return data_corretta


def pulisci_data_scadenza_retro(data):
    if data == None or data == "" or data == " ":
        data_corretta = None
    else:
        data_pulita = re.sub(r'\D', '', data)

        if len(data_pulita) != 6:
            data_corretta = None
        else:
            anno = data_pulita[:2]
            mese = data_pulita[2:4]
            giorno = data_pulita[4:]
            data_corretta = f"{giorno}.{mese}.20{anno}"

    return data_corretta

def pulisci_data_nascita_retro(data):
    if data == None or data == "" or data == " ":
        data_corretta = None
    else:
        data_pulita = re.sub(r'\D', '', data)

        if len(data_pulita) != 6:
            data_corretta = None
        else:
            anno = data_pulita[:2]
            mese = data_pulita[2:4]
            giorno = data_pulita[4:]
            a2 = str(anno)
            a1 = "20"
            a = int(a1+a2)
            if a > 2025:
                a1 = 19
            else:
                a1 = 20
            data_corretta = f"{giorno}.{mese}.{a1}{anno}"

    return data_corretta


def text_formatting(name, result):

    if result.render() == "" or result.render() == " " or len(result.render()) == 0:
        value = None
        confidence = 0
    else:
        words = []
        confidences = []
        for word in result.pages[0].blocks[0].lines[-1].words:
            words.append(re.sub("[$@&-]", "", word.value))
            value = " ".join(words)
            if value == "" or value == " " or len(value) == 1:
                value = None 
                confidence = 0
            else:
                confidences.append(word.confidence)
                confidence = float(np.mean(confidences))
            if name in ["data_emissione", "data_scadenza"]:
                value = pulisci_data(value)
                if value == None:
                    confidence = 0

    results = {'category': name, 'value': value, 'confidence': confidence}

    return results


def text_formatting_retro(name, result:str):

    results = []
    result = result[result.conf != -1]
    lines = result.groupby(['block_num','par_num','line_num'])['text'].apply(lambda x: ' '.join(list(x))).tolist()
    confs = (result.groupby(['block_num','par_num','line_num'])['conf'].mean()/100).tolist()

    if lines == "" or lines == " " or len(lines) == 0:
        results.append({"category": name, "value": None, "confidence":0})
    else:
        cleaned_lines = [line.replace('<', '') for line in lines]

        if name == "MRZ":
            mrz_result = []
            mrz_result.append({'category': "paese_rilascio", 'value': cleaned_lines[0][1:4], 'confidence': confs[0]})
            mrz_result.append({'category': "id", 'value': cleaned_lines[0][4:13], 'confidence': confs[0]})
            mrz_result.append({'category': "data_nascita", 'value': pulisci_data_nascita_retro(cleaned_lines[1][0:6]), 'confidence': confs[1]})
            mrz_result.append({'category': "sesso", 'value': cleaned_lines[1][7:8], 'confidence': confs[1]})
            mrz_result.append({'category': "data_scadenza", 'value': pulisci_data_scadenza_retro(cleaned_lines[1][8:14]), 'confidence': confs[1]})
            mrz_result.append({'category': "nazionalità", 'value': cleaned_lines[1][15:18], 'confidence': confs[1]})
            mrz_result.append({'category': "cognome", 'value': lines[2].split('<<')[0], 'confidence': confs[2]})
            mrz_result.append({'category': "nome", 'value': lines[2].split('<<')[1].replace('<',''), 'confidence': confs[2]})

            results.extend(mrz_result)
        
        elif name == "first_row_mrz":
            first_row_result = []
            first_row_result.append({'category': "paese_rilascio", 'value': cleaned_lines[0][1:4], 'confidence': confs[0]})
            first_row_result.append({'category': "id", 'value': cleaned_lines[0][4:13], 'confidence': confs[0]})
            results.extend(first_row_result)

        elif name == "second_row_mrz":
            second_row_result = []
            second_row_result.append({'category': "data_nascita", 'value': pulisci_data_nascita_retro(cleaned_lines[0][0:6]), 'confidence': confs[0]})
            second_row_result.append({'category': "sesso", 'value': cleaned_lines[0][7:8], 'confidence': confs[0]})
            second_row_result.append({'category': "data_scadenza", 'value': pulisci_data_scadenza_retro(cleaned_lines[0][8:14]), 'confidence': confs[0]})
            second_row_result.append({'category': "nazionalità", 'value': cleaned_lines[0][15:18], 'confidence': confs[0]})

            results.extend(second_row_result)

        elif name == "third_row_mrz":
            third_row_result = []
            third_row_result.append({'category': "cognome", 'value': lines[0].split('<<')[0], 'confidence': confs[0]})
            third_row_result.append({'category': "nome", 'value': lines[0].split('<<')[1], 'confidence': confs[0]})

            results.extend(third_row_result)

    return results


def text_formatting_cartaceo(name, result:str):

    result = re.sub(r'\b(Nome|Cognome|Residenza|stato civile|stato|civile|cm|cittadinanza|nato il|scade il|nato|scade|il|)\b', "", result, flags=re.IGNORECASE)
    words = result.split()
    words = [re.sub(r"[$@&-*.]", "", word.lower()) for word in words]

    if len(words) > 5:
        value = None
        confidence = 0
    else:
        value = " ".join(words)
        confidence = 1.1

    results = {'category': name, 'value': value, 'confidence': confidence}

    return results

def check_valori(extracted_texts):
    if extracted_texts == None:
        return 100
    else:
        valori_not_ok = 0
        for item in extracted_texts:
            if not item["value"]:  # Controlla se l'elemento è vuoto
                valori_not_ok += 1
            elif item["value"].strip() == "":  # Controlla se l'elemento è solo spazi bianchi
                valori_not_ok += 1
            elif item["value"].strip() == None:  # Controlla se l'elemento è None
                valori_not_ok += 1
            elif all(char in '-?!0.,' for char in item["value"]):
                valori_not_ok +=1
            else:
                valori_not_ok = valori_not_ok

    return valori_not_ok
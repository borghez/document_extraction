import os
import ollama
import pytesseract


from . import DocumentROIs

from .file_utils import save_temp_image, text_formatting, text_formatting_retro, text_formatting_cartaceo
from .image_processing import base_alignement, contouring_image, contouring_image_nn, mrz_filter, cartaceo_filter

from tempfile import mkstemp
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"



class OCR:
    def __init__(self, image):
        self.image = image
        self.predictor = ocr_predictor('db_resnet50', 'crnn_vgg16_bn', pretrained=True).cuda()
        self.extracted_text = []


    def correct_image_ocr(self, doc):
        temp_image_path = None
        try:
            aligned_image = base_alignement(self.image, doc)
            v = getattr(DocumentROIs, doc).value
            for name, roi in v.items():
                x, y, w, h = roi[0]
                roi_image = aligned_image[y:y+h, x:x+w]

                # tentativo cartaceo
                if doc == DocumentROIs.CARTA_IDENTITA_CARTACEA or DocumentROIs.CARTA_IDENTITA_CARTACEA_RETRO:
                    result = None
                    temp_file, temp_image_path = mkstemp(suffix=".jpg")
                    with os.fdopen(temp_file, "wb") as f:
                        save_temp_image(roi_image, temp_image_path)
                        with open(temp_image_path, 'rb') as file:
                            response = ollama.chat(
                            model='llama3.2-vision', #llava #llama3.2-vision #minicpm-v
                            messages=[
                              {
                                'role': 'user',
                                'content': 'Act as an OCR. Analyze the provided image and: 1. Recognize all visible text in the image as accurately as possible. 2. Maintain the original structure and formatting of the text. 3. If any words or phrases are unclear, indicate this with [unclear] in your transcription. 4. Provide only the transcription without any additional comments. Just writte the transcription, no comments or other text! Reember to DO NOT add any other text or comment other than the transcription!',
                                'images': [file.read()],
                              }
                            ],
                          )
                        result = response['message']['content']
                        formatted_result = text_formatting_cartaceo(name, result)
                        self.extracted_text.append(formatted_result)
                    try:
                        #formatted_result = text_formatting(name, result)
                        print(formatted_result)
                        #self.extracted_text.append(formatted_result)
                        os.remove(temp_image_path)

                    except TypeError:
                        os.remove(temp_image_path)
                        raise TypeError("Formattazione testo non riuscita. Esco dal programma")
                    # fine test cartaceo

                elif name in ["MRZ", "first_row_mrz", "second_row_mrz", "third_row_mrz"]:
                    roi_image = mrz_filter(roi_image)
                    save_temp_image(roi_image, temp_image_path)
                    result = pytesseract.image_to_data(temp_image_path, lang="mrz", output_type="data.frame")
                    result_formatted = text_formatting_retro(name, result)
                    self.extracted_text.extend(result_formatted) # qui è extend perché altrimenti farebbe lista di lista, se cambi qualcosa presta attenzione a questo
                else:
                    result = None
                    temp_file, temp_image_path = mkstemp(suffix=".jpg")
                    with os.fdopen(temp_file, "wb") as f:
                        save_temp_image(roi_image, temp_image_path)
                        doc_img = DocumentFile.from_images(temp_image_path)
                        result = self.predictor(doc_img)
                    try:
                        formatted_result = text_formatting(name, result)
                        self.extracted_text.append(formatted_result)
                        os.remove(temp_image_path)
                    
                    except TypeError:
                        os.remove(temp_image_path)
                        raise TypeError("Formattazione testo non riuscita. Esco dal programma")
            return self.extracted_text

        except IndexError:
            os.remove(temp_image_path) if temp_image_path else None
            print("Non sono riuscito ad allineare le immagini. Utilizzo il secondo metodo")
            self.extracted_text = None
            return self.extracted_text


    def uncorrect_high_contrast_ocr(self, doc):
        temp_image_path = None
        try:
            warped_image = contouring_image(self.image)
            try:
                aligned_image = base_alignement(warped_image, doc)
                v = getattr(DocumentROIs, doc).value
                for name, roi in v.items():
                    x, y, w, h = roi[0]
                    roi_image = aligned_image[y:y+h, x:x+w]

                    # tentativo cartaceo
                    if doc == DocumentROIs.CARTA_IDENTITA_CARTACEA or DocumentROIs.CARTA_IDENTITA_CARTACEA_RETRO:
                        result = None
                        temp_file, temp_image_path = mkstemp(suffix=".jpg")
                        with os.fdopen(temp_file, "wb") as f:
                            save_temp_image(roi_image, temp_image_path)
                            with open(temp_image_path, 'rb') as file:
                                response = ollama.chat(
                                model='llama3.2-vision', #llava #llama3.2-vision #minicpm-v
                                messages=[
                                  {
                                    'role': 'user',
                                    'content': 'Act as an OCR. Analyze the provided image and: 1. Recognize all visible text in the image as accurately as possible. 2. Maintain the original structure and formatting of the text. 3. If any words or phrases are unclear, indicate this with [unclear] in your transcription. 4. Provide only the transcription without any additional comments. Just write the transcription, no comments or other text! Reember to DO NOT add any other text or comment other than the transcription!',
                                    'images': [file.read()],
                                  }
                                ],
                                options={
                                    'temperature': 0.0,      # Increasing the temperature will make the model answer more creatively (Default: 0.8)
                                    'top_k': 10,             # Reduces the probability of generating nonsense (Default: 40)
                                    'top_p': 0.5,            # Lower value (e.g., 0.5) will generate more focused and conservative text (Default: 0.9)
                                }
                              )
                            result = response['message']['content']
                            formatted_result = text_formatting_cartaceo(name, result)
                            self.extracted_text.append(formatted_result)
                        try:
                            #formatted_result = text_formatting(name, result)
                            print(formatted_result)
                            #self.extracted_text.append(formatted_result)
                            os.remove(temp_image_path)

                        except TypeError:
                            os.remove(temp_image_path)
                            raise TypeError("Formattazione testo non riuscita. Esco dal programma")
                        # fine test cartaceo                    

                    elif name in ["MRZ", "first_row_mrz", "second_row_mrz", "third_row_mrz"]:
                        roi_image = mrz_filter(roi_image)
                        save_temp_image(roi_image, temp_image_path)
                        result = pytesseract.image_to_data(temp_image_path, lang="mrz", output_type="data.frame")
                        result_formatted = text_formatting_retro(name, result)
                        self.extracted_text.extend(result_formatted) # qui è extend perché altrimenti farebbe lista di lista, se cambi qualcosa presta attenzione a questo
                    else:
                        result = None
                        temp_file, temp_image_path = mkstemp(suffix=".jpg")
                        with os.fdopen(temp_file, "wb") as f:
                            save_temp_image(roi_image, temp_image_path)
                            doc_img = DocumentFile.from_images(temp_image_path)
                            result = self.predictor(doc_img)
                        try:
                            formatted_result = text_formatting(name, result)
                            self.extracted_text.append(formatted_result)
                            os.remove(temp_image_path)

                        except TypeError:
                            os.remove(temp_image_path)
                            raise TypeError("Formattazione testo non riuscita. Esco dal programma")

                return self.extracted_text
            
            except Exception:
                os.remove(temp_image_path) if temp_image_path else None
                print("Non sono riuscito ad allineare le immagini. Utilizzo il terzo metodo")
                self.extracted_text = None
                return self.extracted_text
        except AttributeError:
            os.remove(temp_image_path) if temp_image_path else None
            print("Non ho trovato il contorno con Canny. Utilizzo il terzo metodo")
            self.extracted_text = None
            return self.extracted_text


    def uncorrect_low_contrast_ocr(self, hed_path, doc):
        temp_image_path = None
        try:
            warped_image = contouring_image_nn(self.image, hed_path)
            os.remove(hed_path)
            try:
                aligned_image = base_alignement(warped_image, doc)
                v = getattr(DocumentROIs, doc).value
                for name, roi in v.items():
                    x, y, w, h = roi[0]
                    roi_image = aligned_image[y:y+h, x:x+w]

                    # tentativo cartaceo
                    if doc == DocumentROIs.CARTA_IDENTITA_CARTACEA or DocumentROIs.CARTA_IDENTITA_CARTACEA_RETRO:
                        result = None
                        temp_file, temp_image_path = mkstemp(suffix=".jpg")
                        with os.fdopen(temp_file, "wb") as f:
                            save_temp_image(roi_image, temp_image_path)
                            with open(temp_image_path, 'rb') as file:
                                response = ollama.chat(
                                model='llama3.2-vision', #llava #llama3.2-vision #minicpm-v
                                messages=[
                                  {
                                    'role': 'user',
                                    'content': 'Act as an OCR. Analyze the provided image and: 1. Recognize all visible text in the image as accurately as possible. 2. Maintain the original structure and formatting of the text. 3. If any words or phrases are unclear, indicate this with [unclear] in your transcription. 4. Provide only the transcription without any additional comments. Just writte the transcription, no comments or other text! Reember to DO NOT add any other text or comment other than the transcription!',
                                    'images': [file.read()],
                                  }
                                ],
                              )
                            result = response['message']['content']
                            formatted_result = text_formatting_cartaceo(name, result)
                            self.extracted_text.append(formatted_result)
                        try:
                            #formatted_result = text_formatting(name, result)
                            print(formatted_result)
                            #self.extracted_text.append(formatted_result)
                            os.remove(temp_image_path)

                        except TypeError:
                            os.remove(temp_image_path)
                            raise TypeError("Formattazione testo non riuscita. Esco dal programma")
                        # fine test cartaceo                    
                
                    elif name in ["MRZ", "first_row_mrz", "second_row_mrz", "third_row_mrz"]:
                        roi_image = mrz_filter(roi_image)
                        save_temp_image(roi_image, temp_image_path)
                        result = pytesseract.image_to_data(temp_image_path, lang="mrz", output_type="data.frame")
                        result_formatted = text_formatting_retro(name, result)
                        self.extracted_text.extend(result_formatted) # qui è extend perché altrimenti farebbe lista di lista, se cambi qualcosa presta attenzione a questo
                    else:
                        result = None
                        temp_file, temp_image_path = mkstemp(suffix=".jpg")
                        with os.fdopen(temp_file, "wb") as f:
                            save_temp_image(roi_image, temp_image_path)
                            doc_img = DocumentFile.from_images(temp_image_path)
                            result = self.predictor(doc_img)
                        try:
                            formatted_result = text_formatting(name, result)
                            self.extracted_text.append(formatted_result)
                            os.remove(temp_image_path)

                        except TypeError:
                            os.remove(temp_image_path)
                            raise TypeError("Formattazione testo non riuscita. Esco dal programma")

                return self.extracted_text
            
            except IndexError as ie:
                os.remove(temp_image_path) if temp_image_path else None
                print("Non sono riuscito ad allineare le immagini")
                raise Exception(ie)
        except AttributeError as ae:
            os.remove(temp_image_path) if temp_image_path else None
            print("Non ho trovato il contorno con la rete neurale")
            raise Exception(ae)





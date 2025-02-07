import warnings
warnings.filterwarnings("ignore", "You are using `torch.load` with `weights_only=False`*.")

from . import DocumentROIs, ExtractorMethods

from .ocr_methods import OCR
from .neural_network import DNN
from .file_utils import check_valori
from .image_processing import preprocessing



class IdExtractor:
    def __init__(self, image_path, document_type):
        self.image_path = image_path
        self.document_type = document_type
 

    def correct_image_extraction(self, image):
        extracted_texts = OCR(image).correct_image_ocr(self.document_type)
        valori_not_ok = check_valori(extracted_texts)
        if valori_not_ok > 3:
            extracted_texts = None
        return extracted_texts
        

    def uncorrect_high_contrast_image_extraction(self, image):
        extracted_texts = OCR(image).uncorrect_high_contrast_ocr(self.document_type)
        valori_not_ok = check_valori(extracted_texts)
        if valori_not_ok > 3:
            extracted_texts = None
        return extracted_texts
    

    def uncorrect_low_contrast_image_extraction(self, image):
        hed_path = DNN(image)
        extracted_texts = OCR(image).uncorrect_low_contrast_ocr(hed_path, self.document_type)
        return extracted_texts
    

    def extraction(self):

        method = ExtractorMethods.CORRECT_IMAGE.value

        try:
            hasattr(DocumentROIs, self.document_type) == True
            print("Documento accettato")
        except:
            print("Documento non supportato")
            raise Exception

        try:
            image = preprocessing(self.image_path)
        except Exception as ex:
            print("Path incorretto")
            raise Exception(str(ex))  
        
        extracted_texts = self.correct_image_extraction(image)

        if extracted_texts == None:
            print("Risultati non soddisfacenti. Utilizzo il secondo metodo")
            extracted_texts = self.uncorrect_high_contrast_image_extraction(image)
            method = ExtractorMethods.UNCORRECT_HIGH_CONTRAST.value

            if extracted_texts == None:
                print("Risultati non soddisfacenti. Utilizzo il terzo metodo")
                extracted_texts = self.uncorrect_low_contrast_image_extraction(image)
                method = ExtractorMethods.UNCORRECT_LOW_CONTRAST.value

        return {"extracted_texts": extracted_texts, "method": method}
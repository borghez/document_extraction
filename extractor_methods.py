from enum import Enum

class ExtractorMethods(Enum):
    """Classe per codificare l'elenco dei metodi che estraggono le informazioni dal documento.
    NB: E' soggetto a modifiche future."""

    CORRECT_IMAGE = 1
    UNCORRECT_HIGH_CONTRAST = 2
    UNCORRECT_LOW_CONTRAST = 3

    
    ## Descrizioni per un eventuale endpoint in GET (es. 'get_methods_info').
    ## Da modificare all'occorrenza
    
    CORRECT_IMAGE_DESCR = """Questo è il primo metodo ad essere eseguito.
    Presuppone che l'immagine passata possegga il giusto contrasto e un corretto allineamento."""

    UNCORRECT_HIGH_CONTRAST_DESCR = """Questo è il secondo metodo ad essere eseguito.
    Questa funzione restituisce le informazioni relative al documento nel caso in cui l'immagine possegga un contrasto elevato."""

    UNCORRECT_LOW_CONTRAST_DESCR = """Questo è il terzo metodo ad essere eseguito.
    Se le informazioni estratte dal documento provengono da qui, vuol dire che l'immagine potrebbe possedere un basso contrasto.
    Inoltre, se questo metodo non restituisce informazioni, significa che l'immagine deve essere catturatata con una qualità migliore."""


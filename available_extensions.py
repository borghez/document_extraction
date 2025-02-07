from enum import Enum

class AvailableExtensions(Enum):
    """Classe per gestire ed enumerare tutte le estensioni dei file.
    Viene utilizzata nella request del post per poter verificare che il file abbia un'estensione ammissibile."""
    
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
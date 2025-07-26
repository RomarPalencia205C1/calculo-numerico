import re
from datetime import datetime
from errores.tiposErrores import FileNameFormatError
from core.tiposUtilidades import allElementsMeet

class FormatValidator:
    @staticmethod
    def validateFileName(fileName: str) -> bool:
        fileNamePattern = r"^([a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]+)_((\d{8})|(\d{2}-\d{2}-\d{4}))_(serial)?(\d{3,4})\.(txt|bin)$"
        
        patternMatch = re.match(fileNamePattern, fileName)
        
        if not patternMatch:
            raise FileNameFormatError(f"Formato invalido: {fileName}")
        
        try:
            dateString = patternMatch.group(2)
            serialNumber = patternMatch.group(6) 
            
            try:
                datetime.strptime(dateString, "%Y%m%d")
            except ValueError:
                datetime.strptime(dateString, "%d-%m-%Y")

            if not (3 <= len(serialNumber) <= 4):
                raise ValueError("Serial debe tener 3 o 4 digitos")

            return True
            
        except (ValueError, TypeError) as validationError:
            raise FileNameFormatError(
                f"Error en validacion de fecha o serial en '{fileName}': {str(validationError)}"
            ) from validationError
    
    @staticmethod
    def isValidBinary(value: str) -> bool:
        return allElementsMeet(
            value, 
            lambda char: char in '01.'  
        )
    
    @staticmethod
    def isValidDecimal(value: str) -> bool:
        try:
            float(value.replace(',', '.'))
            return True
        except ValueError:
            return False
    
    @staticmethod
    def isValidHexadecimal(value: str) -> bool:
        return allElementsMeet(
            value,
            lambda char: char in '0123456789abcdefABCDEF.'
        )
    
    @staticmethod
    def determineNumberSystem(inputValue: str) -> str:
        if FormatValidator.isValidBinary(inputValue):
            return "Binario"  
        elif FormatValidator.isValidDecimal(inputValue):
            return "Decimal"
        elif FormatValidator.isValidHexadecimal(inputValue):
            return "Hexadecimal"
        return "Desconocido"
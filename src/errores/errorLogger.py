import os
import random
import traceback
from datetime import datetime

class ErrorLogger:
    _logDir = "log"
    _logFile = os.path.join(_logDir, "errores.log")
    
    @staticmethod
    def _ensureLogDirectoryExists():
        if not os.path.exists(ErrorLogger._logDir):
            os.makedirs(ErrorLogger._logDir)

    @staticmethod
    def log(errorType: str, details: str):
        try:
            if not os.path.exists(ErrorLogger._logDir):
                os.makedirs(ErrorLogger._logDir)
        except OSError as e:
            print(f"CRITICO: No se pudo crear el directorio de log: {str(e)}")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d")
        serial = random.randint(100, 999)
        
        stackTrace = traceback.extract_stack()
        if stackTrace:
            frame = stackTrace[-2] 
            location = f"{os.path.basename(frame.filename)}:{frame.lineno}"
        else:
            location = "desconocido:0"
        
        logEntry = f"{errorType}_{timestamp}_{serial}: Error [{details}] | Ubicacion: {location}\n"
        
        try:
            with open(ErrorLogger._logFile, "a", encoding="utf-8") as file:
                file.write(logEntry)
        except Exception as e:
            print(f"CRITICO: No se pudo escribir en el log: {str(e)}")
            print(f"Entrada de log: {logEntry}")
    
    @staticmethod
    def logMatrixOperation(matrix: 'Matrix', operation: str, error: Exception):
        details = f"Operacion: {operation}, Dimensiones: {matrix.rows}x{matrix.cols}, Error: {str(error)}"
        ErrorLogger.log("MatrixOperationError", details)
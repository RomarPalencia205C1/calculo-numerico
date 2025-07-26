import os
import random
from datetime import datetime
from estructuras.listaEnlazada import LinkedList

class FileGenerator:
    def __init__(self, outputDirectory: str):
        self.outputDirectory = outputDirectory
        self.validateOutputDirectory()
    
    def validateOutputDirectory(self):
        if not os.path.exists(self.outputDirectory):
            try:
                os.makedirs(self.outputDirectory)
                print(f"Directorio creado: {self.outputDirectory}")
            except OSError as error:
                raise OSError(f"Error creando directorio: {str(error)}")

        log_directory = 'log'

        if not os.path.exists(log_directory):
            try:
                os.makedirs(log_directory)
                print(f"Directorio creado: {log_directory}")
            except OSError as error:
                raise OSError(f"Error creando directorio de log: {str(error)}")
    
    def generateOutputFile(self, baseName: str, resultsList: LinkedList) -> str:
        if not baseName or not resultsList or resultsList.getListLength() == 0:
            raise ValueError("Datos insuficientes para generar archivo")
        
        fileName = self.generateFileName(baseName)
        fullPath = os.path.join(self.outputDirectory, fileName)
        
        try:
            self.writeResultsToFile(fullPath, resultsList)
            return fullPath
        except Exception as error:
            print(f"Error generando archivo: {str(error)}")
            return None
    
    def generateFileName(self, baseName: str) -> str:
        currentDate = datetime.now().strftime("%Y%m%d")
        serialNumber = random.randint(1, 999)
        return f"{baseName}_{currentDate}_{serialNumber:03d}.txt"
    
    def writeResultsToFile(self, filePath: str, resultsList: LinkedList):
        try:
            with open(filePath, 'w', encoding='utf-8') as outputFile:
                currentNode = resultsList.headNode
                while currentNode:
                    outputFile.write(currentNode.elementData + "\n")
                    currentNode = currentNode.nextNode
        except IOError as ioError:
            raise IOError(f"Error escribiendo archivo: {str(ioError)}")
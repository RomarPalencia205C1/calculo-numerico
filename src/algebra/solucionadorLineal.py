from estructuras.listaEnlazada import LinkedList
from algebra.matrix import Matrix
from numeros.binario import Binary
from numeros.decimal import Decimal
from numeros.hexadecimal import Hexadecimal
from utilidades.validadorFormato import FormatValidator
from errores.tiposErrores import (
    FileNameFormatError,
    FileNotFoundException,
    IOException,
    InvalidNumberFormatError
)

class FileReader:
    def __init__(self):
        self.processedData = LinkedList()
        self.errorLog = LinkedList()
        self.totalRows = 0
        self.totalColumns = 0
    
    def processInputFile(self, filePath: str) -> LinkedList:
        fileName = self.extractFileNameFromPath(filePath)
        
        
        if not FormatValidator.validateFileName(fileName):
            raise FileNameFormatError(f"Formato invalido: {fileName}")
        
        
        isBinaryFile = self.isValidBinaryFile(filePath)
        
        
        if isBinaryFile:
            rawLines = self.readBinaryFile(filePath)
        else:
            rawLines = self.readTextFileLines(filePath)
            
        self.processAllLines(rawLines)
        
        return self.processedData
    
    def isValidBinaryFile(self, filePath: str) -> bool:
        try:
            with open(filePath, 'rb') as file:
                
                chunk = file.read(1024)
                
                try:
                    chunk.decode('utf-8')
                    return False
                except UnicodeDecodeError:
                    return True
        except Exception:
            return False
    
    def readBinaryFile(self, filePath: str) -> LinkedList:
        linesQueue = LinkedList()
        
        try:
            with open(filePath, 'rb') as file:
                binaryData = file.read()
                
                try:
                    decodedText = binaryData.decode('utf-8')
                except UnicodeDecodeError:
                    decodedText = binaryData.decode('iso-8859-1')
                
                currentLine = ""
                for char in decodedText:
                    if char == '\n':
                        linesQueue.addElementAtEnd(currentLine.strip())
                        currentLine = ""
                    else:
                        currentLine += char
                
                if currentLine:
                    linesQueue.addElementAtEnd(currentLine.strip())
                    
        except FileNotFoundError:
            raise FileNotFoundException(f"Archivo no encontrado: {filePath}")
        except IOError as ioError:
            raise IOException(f"Error de lectura binaria: {str(ioError)}")
            
        return linesQueue
    
    def readTextFileLines(self, filePath: str) -> LinkedList:
        lines = LinkedList()
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                for line in file:
                    cleaned = line.strip().replace('\0', '')
                    if cleaned:
                        lines.addElementAtEnd(cleaned)
        except Exception as e:
            raise IOError(f"Error de lectura: {str(e)}")
        return lines
    
    def extractFileNameFromPath(self, path: str) -> str:
        pathParts = LinkedList()
        currentSegment = ""
        
        for char in path:
            if char in ['/', '\\']:
                if currentSegment:
                    pathParts.addElementAtEnd(currentSegment)
                    currentSegment = ""
            else:
                currentSegment += char
        
        if currentSegment:
            pathParts.addElementAtEnd(currentSegment)
        
        return pathParts.getElementAtIndex(pathParts.getListLength() - 1) if pathParts.getListLength() > 0 else ""
    
    def readFileLines(self, filePath: str) -> LinkedList:
        linesQueue = LinkedList()
        
        try:
            with open(filePath, 'r', encoding='utf-8') as file:
                currentLine = ""
                while True:
                    char = file.read(1)
                    if not char:
                        break
                    if char == '\n':
                        linesQueue.addElementAtEnd(currentLine.strip())
                        currentLine = ""
                    else:
                        currentLine += char
                
                if currentLine:
                    linesQueue.addElementAtEnd(currentLine.strip())
                    
        except FileNotFoundError:
            raise FileNotFoundException(f"Archivo no encontrado: {filePath}")
        except IOError as ioError:
            raise IOException(f"Error de lectura: {str(ioError)}")
            
        return linesQueue
    
    def processAllLines(self, linesQueue: LinkedList):
        currentLineNode = linesQueue.headNode
        lineCounter = 1
        
        while currentLineNode:
            processedRow = self.processSingleLine(currentLineNode.elementData, lineCounter)
            
            if processedRow.getListLength() > self.totalColumns:
                self.totalColumns = processedRow.getListLength()
            
            if processedRow.getListLength() > 0:
                self.processedData.addElementAtEnd(processedRow)
                self.totalRows += 1
            
            currentLineNode = currentLineNode.nextNode
            lineCounter += 1
    
    def processSingleLine(self, lineContent: str, lineNumber: int) -> LinkedList:
        rowData = LinkedList()
        fields = self.splitFields(lineContent)
        currentFieldNode = fields.headNode
        
        while currentFieldNode:
            rawValue = currentFieldNode.elementData
            if rawValue:
                try:
                    numberObj = self.createNumberObject(rawValue)
                    rowData.addElementAtEnd(numberObj)
                except InvalidNumberFormatError as formatError:
                    self.logError(lineNumber, rawValue, str(formatError))
            currentFieldNode = currentFieldNode.nextNode
        
        return rowData
    
    def splitFields(self, lineContent: str) -> LinkedList:
        fieldList = LinkedList()
        currentField = ""
        
        for char in lineContent:
            if char == '#':
                if currentField:
                    fieldList.addElementAtEnd(currentField.strip())
                    currentField = ""
            else:
                currentField += char
        
        if currentField:
            fieldList.addElementAtEnd(currentField.strip())
            
        return fieldList
    
    def createNumberObject(self, rawValue: str):
        normalizedValue = rawValue.replace(',', '.').lower()
        
        
        numberSystem = FormatValidator.determineNumberSystem(normalizedValue)
        
        if numberSystem == "Binario":
            return Binary(normalizedValue)
        elif numberSystem == "Decimal":
            return Decimal(normalizedValue)
        elif numberSystem == "Hexadecimal":
            return Hexadecimal(normalizedValue)
        else:
            raise InvalidNumberFormatError("Formato numerico desconocido")
    
    def logError(self, lineNumber: int, rawData: str, message: str):
        errorEntry = f"Linea {lineNumber}, dato '{rawData}': {message}"
        self.errorLog.addElementAtEnd(errorEntry)
    
    def getDimensions(self) -> tuple:
        return (self.totalRows, self.totalColumns)
    
    def getErrorLog(self) -> LinkedList:
        return self.errorLog

    def processAsMatrix(self) -> Matrix:
        if self.processedData.isEmpty():
            return Matrix(0, 0)
        
        rows = self.totalRows
        cols = self.totalColumns
        
        decimal_data = LinkedList()
        current_row = self.processedData.headNode
        
        while current_row:
            row_data = current_row.elementData
            decimal_row = LinkedList()
            current_cell = row_data.headNode
            
            while current_cell:
                num_obj = current_cell.elementData
                try:
                    decimal_value = num_obj.convertToFloat()
                    decimal_row.addElementAtEnd(decimal_value)
                except Exception as e:
                    self.logError(0, str(num_obj), f"Error conversion decimal: {str(e)}")
                    decimal_row.addElementAtEnd(0.0)
                current_cell = current_cell.nextNode
            
            decimal_data.addElementAtEnd(decimal_row)
            current_row = current_row.nextNode
        
        return Matrix(rows, cols, decimal_data)
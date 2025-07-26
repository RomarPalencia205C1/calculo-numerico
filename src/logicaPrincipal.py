import os
import time
from datetime import datetime
from estructuras.listaEnlazada import LinkedList
from archivos.lectorArchivos import FileReader
from utilidades.Generador import FileGenerator
from errores.calculadoraErrores import ErrorCalculator
from errores.tiposErrores import (
    FileProcessingException,
    FileNameFormatError,
    FileNotFoundException,
    IOException,
    MatrixDimensionsError,
    SingularMatrixError,
    FileOperationException
)
from core.tiposUtilidades import isTypeInstance
from algebra.matrix import Matrix
from algebra.solucionadorLineal import LinearSystemSolver
from algebra.analizadorEcuacion import EquationParser, EquationError
from errores.errorLogger import ErrorLogger

class LogicaPrincipal:
    def __init__(self, dataDirectoryPath: str, outputDirectoryPath: str, matrixDirectoryPath: str):
        self.dataDirectoryPath = dataDirectoryPath
        self.outputDirectoryPath = outputDirectoryPath
        self.matrixDirectoryPath = matrixDirectoryPath
        self.fileProcessor = FileReader()
        self.fileGenerator = FileGenerator(self.outputDirectoryPath)
        self.variables = self._loadVariables()
        self.parser = EquationParser(self.variables)

    def _loadVariables(self) -> dict:
        """
        Carga todas las matrices desde la carpeta de matrices especificada.
        CORRECCIÓN: Utiliza una lógica de lectura simple y directa para los archivos
                    de matrices, sin depender del FileReader complejo.
        """
        print("Cargando variables (matrices)...")
        loaded_variables = {}
        if not os.path.exists(self.matrixDirectoryPath):
            print(f"ADVERTENCIA: El directorio de matrices '{self.matrixDirectoryPath}' no existe.")
            return loaded_variables

        for fileName in os.listdir(self.matrixDirectoryPath):
            if fileName.endswith(".txt"):
                variableName = os.path.splitext(fileName)[0].upper()
                filePath = os.path.join(self.matrixDirectoryPath, fileName)
                
                try:
                    
                    matrix_data = LinkedList()
                    rows = 0
                    cols = 0
                    
                   
                    with open(filePath, 'r') as f:
                        lines = f.readlines()
                        rows = len(lines)
                        for line in lines:
                            line = line.strip()
                            if line:
                                
                                row_list = LinkedList()
                                values = [float(val) for val in line.split()]
                                for v in values:
                                    row_list.addElementAtEnd(v)
                                
                                if cols == 0:
                                    cols = len(values)
                                elif len(values) != cols:
                                    raise ValueError("Las filas de la matriz no tienen la misma cantidad de columnas.")
                                
                                matrix_data.addElementAtEnd(row_list)
                    
                    
                    if rows > 0 and cols > 0:
                        matrix_obj = Matrix(rows, cols, matrix_data)
                        loaded_variables[variableName] = matrix_obj
                        print(f"  - Variable '{variableName}' ({rows}x{cols}) cargada correctamente.")
                    else:
                        print(f"  - ADVERTENCIA: El archivo de matriz '{fileName}' está vacío o mal formado.")

                except Exception as e:
                    error_msg = f"Fallo al cargar la variable desde {fileName}: {e}"
                    print(f"  - ERROR: {error_msg}")
                    ErrorLogger.log("VariableLoadError", error_msg)

        return loaded_variables

    def setupProcessingEnvironment(self):
        for directory in [self.dataDirectoryPath, self.outputDirectoryPath, self.matrixDirectoryPath, 'log']:
            if not os.path.exists(directory):
                try:
                    os.makedirs(directory)
                except OSError as osError:
                    raise OSError(f"Error al crear directorio {directory}: {str(osError)}")

    def processFileCollection(self, fileList: LinkedList, mode='numerical') -> list:
        """
        Procesa una colección de archivos y DEVUELVE los resultados como una lista de strings.
        """
        output_lines = [] 
        currentNode = fileList.headNode
        
        while currentNode:
            filePath = currentNode.elementData
            fileName = os.path.basename(filePath)
            output_lines.append(f"--- Procesando Archivo: {fileName} ---")
            
            try:
                if mode == 'equation':
                   
                    results = self.processEquationFile(filePath)
                    output_lines.extend(results)
                else:
                   
                    results = self.processSingleInputFile(filePath)
                    output_lines.extend(results)

            except Exception as error:
                error_msg = f"Error fatal procesando {fileName}: {str(error)}"
                output_lines.append(error_msg)
                ErrorLogger.log("FileProcessingError", error_msg)
            
            output_lines.append("\n")
            currentNode = currentNode.nextNode
            
        return output_lines

    def processEquationFile(self, filePath: str):
        fileName = os.path.basename(filePath)
        self.printProcessingHeader(f"Procesando archivo de ecuaciones: {fileName}")
        
        results = LinkedList()
        lines = self.fileProcessor.readTextFileLines(filePath)
        
        currentLineNode = lines.headNode
        lineNum = 1
        while currentLineNode:
            equation_str = currentLineNode.elementData
            if equation_str.strip():
                print(f"  Evaluando linea {lineNum}: {equation_str}")
                try:
                    result = self.parser.evaluate(equation_str)
                    result_str = f"Resultado de '{equation_str}':\n{str(result)}"
                    results.addElementAtEnd(result_str)
                    print(f"    -> ¡Exito!")
                except (EquationError, MatrixDimensionsError, Exception) as e:
                    failReason = f"Fallo en ecuación '{equation_str}'. Causa: {e}"
                    results.addElementAtEnd(f"ERROR: {failReason}") 
                    ErrorLogger.log("EquationEvaluationError", failReason)
                    print(f"    -> ERROR: {e}")
            lineNum += 1
            currentLineNode = currentLineNode.nextNode
            
        baseName = f"resultados_ecuaciones_{os.path.splitext(fileName)[0]}"
        outputFilePath = self.fileGenerator.generateOutputFile(baseName, results)
        print(f"Resultados de ecuaciones guardados en: {outputFilePath}")

        return results.toPythonList()

    def processSingleInputFile(self, filePath: str):
        try:
            startTime = time.time()
            fileName = os.path.basename(filePath)
            
            self.printProcessingHeader(f"Procesando archivo de datos: {fileName}")

            processedData = self.fileProcessor.processInputFile(filePath)
            rowCount, columnCount = self.fileProcessor.getDimensions()
            print(f"Archivo procesado: {rowCount} filas x {columnCount} columnas")
            
            analysisResults = LinkedList()
           
            self.calculateNumericalAnalysis(processedData, analysisResults)
            self.calculateErrorMetrics(processedData, analysisResults)
            
            matrix = self.fileProcessor.processAsMatrix()
            self.performMatrixOperations(matrix, analysisResults)
            
            baseName = fileName.split('_')[0]
            outputFilePath = self.fileGenerator.generateOutputFile(baseName, analysisResults)
            
            self.displayProcessingStatistics(startTime, outputFilePath)
            
        except (FileNameFormatError, FileNotFoundException, IOException) as ioError:
            raise FileProcessingException(f"Error de procesamiento: {str(ioError)}")
        except Exception as processingError:
            ErrorLogger.log("FileProcessingError", f"Error procesando {filePath}: {str(processingError)}")
            raise FileProcessingException(f"Error inesperado: {str(processingError)}")
        
        return analysisResults.toPythonList()

    def printProcessingHeader(self, title: str):
        separator = "=" * 50
        print(f"\n{separator}")
        print(title)
        print(f"{separator}")

    def calculateNumericalAnalysis(self, processedData: LinkedList, resultContainer: LinkedList):
        resultContainer.addElementAtEnd("=== Análisis Numérico por Dato ===")
        currentRowNode = processedData.headNode
        rowNumber = 1
        while currentRowNode:
            rowData = currentRowNode.elementData
            currentCellNode = rowData.headNode
            columnNumber = 1
            while currentCellNode:
                numberObject = currentCellNode.elementData
                resultLine = self.formatAnalysisResult(rowNumber, columnNumber, numberObject)
                resultContainer.addElementAtEnd(resultLine)
                currentCellNode = currentCellNode.nextNode
                columnNumber += 1
            currentRowNode = currentRowNode.nextNode
            rowNumber += 1

    def formatAnalysisResult(self, rowIndex: int, columnIndex: int, numberObject) -> str:
        try:
            normalizedForm = numberObject.getNormalizedForm()
            significantDigits = numberObject.getSignificantDigitsCount()
            operations = numberObject.getSupportedOperations()
            numberType = self.getNumberTypeDescription(numberObject)
            
            return (f"Fila {rowIndex}, Col {columnIndex}: "
                    f"Valor: {numberObject.getOriginalValue()} | "
                    f"Sistema: {numberType} | "
                    f"Normalizado: {normalizedForm} | "
                    f"Digitos significativos: {significantDigits} | "
                    f"Operaciones: {','.join(operations)}")
        except Exception as formatError:
            return f"Error al formatear el resultado: {str(formatError)}"

    def getNumberTypeDescription(self, numberObject) -> str:
        if isTypeInstance(numberObject, "Binary"):
            return "Binario"
        elif isTypeInstance(numberObject, "Decimal"):
            return "Decimal"
        elif isTypeInstance(numberObject, "Hexadecimal"):
            return "Hexadecimal"
        return "Desconocido"

    def calculateErrorMetrics(self, processedData: LinkedList, resultContainer: LinkedList):
        if processedData.isEmpty() or processedData.getListLength() < 2:
            return
        
        allValues = LinkedList()
        currentRow = processedData.headNode
        while currentRow:
            row = currentRow.elementData
            if not row.isEmpty():
                currentCell = row.headNode
                while currentCell:
                    try:
                        floatVal = currentCell.elementData.convertToFloat()
                        allValues.addElementAtEnd(floatVal)
                    except Exception as e:
                        print(f"Advertencia: valor no convertible a float - {str(e)}")
                    currentCell = currentCell.nextNode
            currentRow = currentRow.nextNode
        
        if allValues.getListLength() < 2:
            return
        
        resultContainer.addElementAtEnd("\n=== Resultados del Análisis de Errores ===")
        
        current = allValues.headNode
        while current and current.nextNode:
            exact = current.elementData
            approx = current.nextNode.elementData
            
            try:
                absError = ErrorCalculator.calculateAbsoluteError(exact, approx)
                relError = ErrorCalculator.calculateRelativeError(exact, approx)
                roundError = ErrorCalculator.calculateRoundingError(approx) 
                truncError = ErrorCalculator.calculateTruncationError(approx)
                
                errorList = LinkedList()
                errorList.addElementAtEnd(absError)
                errorList.addElementAtEnd(absError)
                propError = ErrorCalculator.calculateSumErrorPropagation(errorList)

                relErrorStr = f"{relError:.6f}" if relError != float('inf') else "inf"
                
                resultLine = (
                    f"Comparación: Valor Exacto={exact:.6f} vs. Valor Aproximado={approx:.6f}\n"
                    f"  - Error Absoluto: {absError:.6f}\n"
                    f"  - Error Relativo: {relErrorStr}\n"
                    f"  - Error por Redondeo (en aprox): {roundError:.6f}\n"
                    f"  - Error por Truncamiento (en aprox): {truncError:.6f}\n"
                    f"  - Error por Propagación (ejemplo): {propError:.6f}"
                )
                resultContainer.addElementAtEnd(resultLine)
                
            except Exception as e:
                errorMsg = f"Error en cálculo para valores {exact:.6f} y {approx:.6f}: {str(e)}"
                resultContainer.addElementAtEnd(errorMsg)
                ErrorLogger.log("ErrorMetricCalculation", errorMsg)
            
            current = current.nextNode.nextNode if current.nextNode else None

    def performMatrixOperations(self, matrix: Matrix, resultContainer: LinkedList):
        resultContainer.addElementAtEnd("\n=== Operaciones Matriciales ===")
        
        try:
            transposed = matrix.transpose()
            resultContainer.addElementAtEnd(f"\nMatriz Transpuesta ({transposed.rows}x{transposed.cols}):\n{str(transposed)}")
        except Exception as e:
            resultContainer.addElementAtEnd(f"Error en transpuesta: {str(e)}")

        if matrix.isSquare():
            resultContainer.addElementAtEnd("\n=== Descomposición de Matrices ===")
            
            
            try:
                L_doo, U_doo = matrix.doolittleDecomposition()
                resultContainer.addElementAtEnd("\n--- Descomposición Doolittle (A = LU) ---")
                resultContainer.addElementAtEnd(f"Matriz L:\n{str(L_doo)}")
                resultContainer.addElementAtEnd(f"Matriz U:\n{str(U_doo)}")
            except Exception as e:
                msg = f"Error en descomposición Doolittle: {e}"
                resultContainer.addElementAtEnd(msg)
                ErrorLogger.log("DoolittleError", msg)

            
            try:
                L_cho = matrix.choleskyDecomposition()
                resultContainer.addElementAtEnd("\n--- Descomposición Cholesky (A = LL^T) ---")
                resultContainer.addElementAtEnd(f"Matriz L:\n{str(L_cho)}")
            except Exception as e:
                msg = f"Error en descomposición Cholesky: {e}"
                resultContainer.addElementAtEnd(msg)
                ErrorLogger.log("CholeskyError", msg)
        else:
            resultContainer.addElementAtEnd("\nDescomposiciones omitidas: la matriz no es cuadrada.")
    
    def collectAllAbsoluteErrors(self, fileList: LinkedList) -> list:
        allAbsoluteErrors = []
        allValues = LinkedList()
        
        currentNode = fileList.headNode
        while currentNode:
            filePath = currentNode.elementData
            try:
                tempReader = FileReader()
                lines = tempReader.readTextFileLines(filePath)
                tempReader.processAllLines(lines)
                
                processedData = tempReader.processedData
                
                currentRow = processedData.headNode
                while currentRow:
                    row = currentRow.elementData
                    currentCell = row.headNode
                    while currentCell:
                        try:
                            floatVal = currentCell.elementData.convertToFloat()
                            allValues.addElementAtEnd(floatVal)
                        except Exception:
                            pass 
                        currentCell = currentCell.nextNode
                    currentRow = currentRow.nextNode
            except Exception as e:
                print(f"Advertencia: No se pudo procesar {os.path.basename(filePath)} para recoleccion de errores. Causa: {e}")
            
            currentNode = currentNode.nextNode
            
        if allValues.getListLength() < 2:
            return []

        valueNode = allValues.headNode
        while valueNode and valueNode.nextNode:
            exact = valueNode.elementData
            approx = valueNode.nextNode.elementData
            
            try:
                absError = ErrorCalculator.calculateAbsoluteError(exact, approx)
                allAbsoluteErrors.append(absError)
            except Exception:
                pass
            
            valueNode = valueNode.nextNode.nextNode if valueNode.nextNode else None
            
        return allAbsoluteErrors
    
    def collectErrorsFromDataLines(self, dataLines: list) -> list:
        allAbsoluteErrors = []
        allValues = LinkedList()
        
        
        tempReader = FileReader()
        linesAsLinkedList = LinkedList()
        for line in dataLines:
            linesAsLinkedList.addElementAtEnd(line)
        
        tempReader.processAllLines(linesAsLinkedList)
        processedData = tempReader.processedData

        
        currentRow = processedData.headNode
        while currentRow:
            row = currentRow.elementData
            currentCell = row.headNode
            while currentCell:
                try:
                    floatVal = currentCell.elementData.convertToFloat()
                    allValues.addElementAtEnd(floatVal)
                except Exception:
                    pass
                currentCell = currentCell.nextNode
            currentRow = currentRow.nextNode

        
        if allValues.getListLength() < 2:
            return []

        valueNode = allValues.headNode
        while valueNode and valueNode.nextNode:
            exact = valueNode.elementData
            approx = valueNode.nextNode.elementData
            try:
                absError = ErrorCalculator.calculateAbsoluteError(exact, approx)
                allAbsoluteErrors.append(absError)
            except Exception:
                pass
            valueNode = valueNode.nextNode.nextNode if valueNode.nextNode else None
            
        return allAbsoluteErrors

    def displayProcessingStatistics(self, startTime: float, outputPath: str):
        processingDuration = time.time() - startTime
        print(f"Archivo procesado en: {processingDuration:.4f} segundos")
        if outputPath:
            print(f"Resultados guardados en: {outputPath}")
        
        if not self.fileProcessor.getErrorLog().isEmpty():
            print("\nErrores encontrados durante el procesamiento del archivo:")
            errorNode = self.fileProcessor.getErrorLog().headNode
            while errorNode:
                print(f"  - {errorNode.elementData}")
                errorNode = errorNode.nextNode
    
    def getProcessableFiles(self, directory=None) -> LinkedList:
        targetDirectory = directory or self.dataDirectoryPath
        fileList = LinkedList()
        try:
            if os.path.exists(targetDirectory):
                for fileName in os.listdir(targetDirectory):
                    if fileName.endswith('.txt') or fileName.endswith('.bin'):
                        fullPath = os.path.join(targetDirectory, fileName)
                        fileList.addElementAtEnd(fullPath)
        except FileNotFoundError:
            print(f"Advertencia: no se encontro la carpeta '{targetDirectory}'")
        return fileList
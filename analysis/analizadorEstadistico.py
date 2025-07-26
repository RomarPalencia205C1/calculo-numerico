

import matplotlib


matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
from logicaPrincipal import LogicaPrincipal
from .muestreador import DataSampler 
from estructuras.listaEnlazada import LinkedList

class StatisticalAnalyzer:
    def __init__(self, mainLogicInstance: LogicaPrincipal, iterations=5):
        self.mainLogic = mainLogicInstance
        self.iterations = iterations
        self.collectedErrors = []
      
        self.LARGE_FILE_THRESHOLD_BYTES = 10 * 1024 * 1024 

    def runAnalysis(self, filesToProcess: LinkedList):
        print(f"Ejecutando analisis estadístico con {self.iterations} iteraciones...")
        
        if filesToProcess.isEmpty():
            print("No hay archivos para el analisis estadistico.")
            return None

        fileNode = filesToProcess.headNode
        while fileNode:
            filePath = fileNode.elementData
            fileName = os.path.basename(filePath)
            fileSize = os.path.getsize(filePath)
            
            print(f"\nProcesando archivo: {fileName} (Tamaño: {fileSize / 1024 / 1024:.2f} MB)")

            if fileSize > self.LARGE_FILE_THRESHOLD_BYTES:
                print("  -> Archivo grande detectado. Aplicando muestreo estadistico...")
                sampler = DataSampler(filePath)
                sampleLines = sampler.getSampleFromFile()
                
                errors = self.mainLogic.collectErrorsFromDataLines(sampleLines)
            else:
                print("  -> Archivo de prueba detectado. Procesando archivo completo...")
                singleFileList = LinkedList()
                singleFileList.addElementAtEnd(filePath)
                errors = self.mainLogic.collectAllAbsoluteErrors(singleFileList)
            
            for i in range(self.iterations):
                self.collectedErrors.extend(errors)
                print(f"  - Iteración {i + 1}/{self.iterations} completada para {fileName}.")

            fileNode = fileNode.nextNode
        
        if not self.collectedErrors:
            print("No se recolectaron errores para analizar.")
            return None
            
        return self.generateDistributionPlot()

    def generateDistributionPlot(self):
        if not self.collectedErrors:
            return None

        errors_array = np.array(self.collectedErrors)
        
        finite_errors = errors_array[np.isfinite(errors_array)]
        
        if len(finite_errors) < 2:
            print("No hay suficientes errores finitos para generar una grafica.")
            return None
        
        mu = np.mean(finite_errors)
        sigma = np.std(finite_errors)

        plt.figure(figsize=(10, 6))
        plt.hist(finite_errors, 30, density=True, alpha=0.6, color='b')

        xmin, xmax = plt.xlim()
        x = np.linspace(xmin, xmax, 100)
        p = (1/(sigma * np.sqrt(2 * np.pi))) * np.exp( - (x - mu)**2 / (2 * sigma**2) )
        plt.plot(x, p, 'r', linewidth=2)

        plt.title('Distribucion Normal de Errores de Calculo (Valores Finitos)')
        plt.xlabel('Valor del Error')
        plt.ylabel('Densidad de Probabilidad')
        plt.grid(True)
        plt.axvline(mu, color='k', linestyle='dashed', linewidth=1)
        plt.text(mu * 1.05, plt.ylim()[1] * 0.9, f'Media (μ) = {mu:.4f}\nDE (σ) = {sigma:.4f}')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        
        imagePng = buffer.getvalue()
        graph = base64.b64encode(imagePng).decode('utf-8')
        
        buffer.close()

        return graph
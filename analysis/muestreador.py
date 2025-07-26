import random
import math

class DataSampler:
    def __init__(self, filePath: str):
        self.filePath = filePath

    def calculateSampleSize(self, confidenceLevel=0.95, marginOfError=0.05) -> int:

        z_scores = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.58
        }
        
        if confidenceLevel not in z_scores:
            raise ValueError("El nivel de confianza debe ser 0.90, 0.95, o 0.99")

        Z = z_scores[confidenceLevel]
        p = 0.5
        E = marginOfError
        
        sampleSize = ((Z**2) * p * (1-p)) / (E**2)
        
        return math.ceil(sampleSize)

    def getSampleFromFile(self, confidenceLevel=0.95, marginOfError=0.05) -> list:
        sampleSize = self.calculateSampleSize(confidenceLevel, marginOfError)
        print(f"Tamaño de muestra calculado: {sampleSize} registros.")
        sample = []
        with open(self.filePath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if i < sampleSize:
                    sample.append(line.strip())
                else:
                    j = random.randint(0, i)
                    if j < sampleSize:
                        sample[j] = line.strip()
        
        print(f"Se ha tomado una muestra de {len(sample)} lineas del archivo.")
        return sample
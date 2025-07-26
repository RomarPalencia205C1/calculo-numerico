

import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
from .muestreador import DataSampler

class DataVisualizer3D:
    def __init__(self, filePath: str):
        self.filePath = filePath
        self.points = []
        self.LARGE_FILE_THRESHOLD_BYTES = 10 * 1024 * 1024

    def generatePointsFromFile(self, colX: int, colY: int, colZ: int):
        lines = []
        fileSize = os.path.getsize(self.filePath)

        if fileSize > self.LARGE_FILE_THRESHOLD_BYTES:
            print(f"Archivo grande detectado ({fileSize / 1024 / 1024:.2f} MB). Aplicando muestreo.")
            sampler = DataSampler(self.filePath)
            lines = sampler.getSampleFromFile()
        else:
            print("Archivo pequeño detectado. Procesando archivo completo.")
            with open(self.filePath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f.readlines()]

        extracted_points = []
        max_cols = 0
        for line in lines:
            parts = line.split('#')
            if len(parts) > max_cols:
                max_cols = len(parts)
            
            if len(parts) > max(colX, colY, colZ):
                try:
                    x = float(parts[colX])
                    y = float(parts[colY])
                    z = float(parts[colZ])
                    extracted_points.append((x, y, z))
                except (ValueError, IndexError):
                    continue
        
        if not extracted_points:
            raise ValueError(f"No se pudieron extraer puntos validos. "
                            f"Verifica que los índices de columna (0 a {max_cols-1}) sean correctos y contengan datos numericos.")

        self.points = extracted_points
        return self.points

    def generate3DGraph(self, colX: int, colY: int, colZ: int):
        if not self.points:
            return None
            
        x_vals = [p[0] for p in self.points]
        y_vals = [p[1] for p in self.points]
        z_vals = [p[2] for p in self.points]

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x_vals, y_vals, z_vals, c=z_vals, cmap='viridis', marker='o', alpha=0.6)

        ax.set_title('Visualizacion 3D de Datos del Archivo')
        ax.set_xlabel(f'Eje X (Columna {colX})')
        ax.set_ylabel(f'Eje Y (Columna {colY})')
        ax.set_zlabel(f'Eje Z (Columna {colZ})')
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)
        
        imagePng = buffer.getvalue()
        graph = base64.b64encode(imagePng).decode('utf-8')
        
        buffer.close()
        return graph

    def runVisualization(self, colX: int, colY: int, colZ: int):
        self.generatePointsFromFile(colX, colY, colZ)
        grafica = self.generate3DGraph(colX, colY, colZ)
        return grafica
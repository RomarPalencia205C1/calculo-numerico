import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from itertools import combinations

class Proyector3D:
    def __init__(self):
        self.puntos = []
        self.formulaX = lambda t: np.cos(t)
        self.formulaY = lambda t: np.sin(t)
        self.formulaZ = lambda t: t

    def generarPuntos(self, numPuntos=50):
        rangoT = np.linspace(0, 10, numPuntos)

        x = self.formulaX(rangoT)
        y = self.formulaY(rangoT)
        z = self.formulaZ(rangoT)

        self.puntos = list(zip(x, y, z))
        return self.puntos

    def calcularDistancias(self) -> list:
        if len(self.puntos) < 2:
            return []

        distancias = []
        for (p1, p2) in combinations(self.puntos, 2):
            distancia = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

            punto1Str = f"({p1[0]:.2f}, {p1[1]:.2f}, {p1[2]:.2f})"
            punto2Str = f"({p2[0]:.2f}, {p2[1]:.2f}, {p2[2]:.2f})"

            resultadoConjunto = f"d{punto1Str, punto2Str} = {distancia:.4f}"
            distancias.append(resultadoConjunto)

        return distancias

    def generarGrafica3D(self):
        if not self.puntos:
            return None

        x_vals = [p[0] for p in self.puntos]
        y_vals = [p[1] for p in self.puntos]
        z_vals = [p[2] for p in self.puntos]

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(x_vals, y_vals, z_vals, c=z_vals, cmap='viridis', marker='o')

        ax.set_title('Proyección de Puntos en 3 Ejes')
        ax.set_xlabel('Eje X (cos(t))')
        ax.set_ylabel('Eje Y (sin(t))')
        ax.set_zlabel('Eje Z (t)')
        plt.grid(True)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)

        imagePng = buffer.getvalue()
        graph = base64.b64encode(imagePng).decode('utf-8')

        buffer.close()
        return graph

    def runProyeccion(self):
        self.generarPuntos()
        distancias = self.calcularDistancias()
        grafica = self.generarGrafica3D()

        return grafica, distancias
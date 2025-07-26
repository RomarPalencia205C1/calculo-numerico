from estructuras.listaEnlazada import LinkedList
from errores.tiposErrores import MatrixDimensionsError

class Matrix:
    def __init__(self, rows: int, cols: int, data: LinkedList = None):
        self.rows = rows
        self.cols = cols
        
        if data is None:
            self.data = LinkedList()
            for _ in range(rows):
                row = LinkedList()
                for _ in range(cols):
                    row.addElementAtEnd(0.0)
                self.data.addElementAtEnd(row)
        else:
            self.data = data
    
    def get(self, i: int, j: int) -> float:
        row = self.data.getElementAtIndex(i)
        return row.getElementAtIndex(j)
    
    def set(self, i: int, j: int, value: float):
        row = self.data.getElementAtIndex(i)
        row.setElementAtIndex(j, value)
    
    def __str__(self):
        if self.rows == 0 or self.cols == 0:
            return "[]"

        col_widths = []
        for j in range(self.cols):
            max_len = 0
            for i in range(self.rows):
                num_str = f"{self.get(i, j):.4f}" 
                if len(num_str) > max_len:
                    max_len = len(num_str)
            col_widths.append(max_len)

        matrix_str = "[\n"
        for i in range(self.rows):
            row_str = "  [ "
            for j in range(self.cols):
                num_str = f"{self.get(i, j):.4f}"
                row_str += f"{num_str:>{col_widths[j]}}  "
            row_str += "]\n"
            matrix_str += row_str
        matrix_str += "]"
        
        return matrix_str

    def swapRows(self, i: int, j: int):
        rowI = self.data.getElementAtIndex(i)
        rowJ = self.data.getElementAtIndex(j)
        self.data.setElementAtIndex(i, rowJ)
        self.data.setElementAtIndex(j, rowI)
    
    def scaleRow(self, i: int, scalar: float):
        row = self.data.getElementAtIndex(i)
        current = row.headNode
        while current:
            current.elementData *= scalar
            current = current.nextNode
    
    def addRow(self, sourceIdx: int, targetIdx: int, scalar: float = 1.0):
        source = self.data.getElementAtIndex(sourceIdx)
        target = self.data.getElementAtIndex(targetIdx)
        
        sourceNode = source.headNode
        targetNode = target.headNode
        
        while sourceNode and targetNode:
            targetNode.elementData += scalar * sourceNode.elementData
            sourceNode = sourceNode.nextNode
            targetNode = targetNode.nextNode
    
    def isSquare(self) -> bool:
        return self.rows == self.cols
    
    def transpose(self) -> 'Matrix':
        transposedMatrix = Matrix(self.cols, self.rows)
        for i in range(self.rows):
            for j in range(self.cols):
                transposedMatrix.set(j, i, self.get(i, j))
        return transposedMatrix
    
    def scalarMultiply(self, scalar: float) -> 'Matrix':
        scaledMatrix = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                scaledMatrix.set(i, j, self.get(i, j) * scalar)
        return scaledMatrix
    
    def add(self, other: 'Matrix') -> 'Matrix':
        if self.rows != other.rows or self.cols != other.cols:
            raise MatrixDimensionsError(
                f"Dimensiones incompatibles para suma: "
                f"{self.rows}x{self.cols} vs {other.rows}x{other.cols}"
            )
        
        resultMatrix = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                resultMatrix.set(i, j, self.get(i, j) + other.get(i, j))
        return resultMatrix
    
    def multiply(self, other: 'Matrix') -> 'Matrix':
        if self.cols != other.rows:
            raise MatrixDimensionsError(
                f"Dimensiones incompatibles para multiplicacion: "
                f"{self.rows}x{self.cols} vs {other.rows}x{other.cols}"
            )
        
        resultMatrix = Matrix(self.rows, other.cols)
        for i in range(self.rows):
            for j in range(other.cols):
                total = 0.0
                for k in range(self.cols):
                    total += self.get(i, k) * other.get(k, j)
                resultMatrix.set(i, j, total)
        return resultMatrix
    
    def subtract(self, other: 'Matrix') -> 'Matrix':
        if self.rows != other.rows or self.cols != other.cols:
            raise MatrixDimensionsError(
                f"Dimensiones incompatibles para resta: "
                f"{self.rows}x{self.cols} vs {other.rows}x{other.cols}"
            )
        
        resultMatrix = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols):
                resultMatrix.set(i, j, self.get(i, j) - other.get(i, j))
        return resultMatrix

    def isSymmetric(self) -> bool:
        if not self.isSquare():
            return False
        for i in range(self.rows):
            for j in range(i + 1, self.cols):
                if self.get(i, j) != self.get(j, i):
                    return False
        return True

    def choleskyDecomposition(self) -> 'Matrix':
        if not self.isSquare():
            raise MatrixDimensionsError("La matriz debe ser cuadrada para Cholesky.")
        if not self.isSymmetric():
            raise MatrixDimensionsError("La matriz debe ser simetrica para Cholesky.")

        n = self.rows
        L = Matrix(n, n)

        for i in range(n):
            for j in range(i + 1):
                s = sum(L.get(i, k) * L.get(j, k) for k in range(j))
                
                if i == j:
                    val = self.get(i, i) - s
                    if val < 0:
                        raise MatrixDimensionsError("La matriz no es definida positiva.")
                    L.set(i, j, val**0.5)
                else:
                    L.set(i, j, (1.0 / L.get(j, j) * (self.get(i, j) - s)))
        return L

    def doolittleDecomposition(self) -> tuple['Matrix', 'Matrix']:
        if not self.isSquare():
            raise MatrixDimensionsError("La matriz debe ser cuadrada para Doolittle.")
            
        n = self.rows
        L = Matrix(n, n)
        U = Matrix(n, n)

        for i in range(n):
            L.set(i, i, 1.0)
            
            for k in range(i, n):
                s = sum(L.get(i, j) * U.get(j, k) for j in range(i))
                U.set(i, k, self.get(i, k) - s)

            for k in range(i + 1, n):
                s = sum(L.get(k, j) * U.get(j, i) for j in range(i))
                if U.get(i, i) == 0:
                    raise MatrixDimensionsError("La descomposicion de Doolittle fallo: division por cero.")
                L.set(k, i, (self.get(k, i) - s) / U.get(i, i))
                
        return (L, U)
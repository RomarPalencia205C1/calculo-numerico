class Node:
    def __init__(self, elementData):
        self.elementData = elementData
        self.nextNode = None

class LinkedList:
    def __init__(self):
        self.headNode = None
        self.listLength = 0
    
    def addElementAtEnd(self, elementData):
        newNode = Node(elementData)
        
        if self.headNode is None:
            self.headNode = newNode
        else:
            currentNode = self.headNode
            while currentNode.nextNode:
                currentNode = currentNode.nextNode
            currentNode.nextNode = newNode
            
        self.listLength += 1
    
    def addElementAtPosition(self, elementData, positionIndex: int):
        if positionIndex < 0 or positionIndex > self.listLength:
            raise IndexError("Indice fuera de rango")
            
        newNode = Node(elementData)
        
        if positionIndex == 0:
            newNode.nextNode = self.headNode
            self.headNode = newNode
        else:
            currentNode = self.headNode
            for _ in range(positionIndex - 1):
                currentNode = currentNode.nextNode
            newNode.nextNode = currentNode.nextNode
            currentNode.nextNode = newNode
            
        self.listLength += 1
    
    def getElementAtIndex(self, positionIndex: int):
        if positionIndex < 0 or positionIndex >= self.listLength:
            raise IndexError("Indice fuera de rango")
            
        currentNode = self.headNode
        for _ in range(positionIndex):
            currentNode = currentNode.nextNode
            
        return currentNode.elementData
    
    def removeElementAtIndex(self, positionIndex: int):
        if positionIndex < 0 or positionIndex >= self.listLength:
            raise IndexError("Indice fuera de rango")
            
        if positionIndex == 0:
            removedData = self.headNode.elementData
            self.headNode = self.headNode.nextNode
        else:
            previousNode = self.headNode
            for _ in range(positionIndex - 1):
                previousNode = previousNode.nextNode
                
            removedData = previousNode.nextNode.elementData
            previousNode.nextNode = previousNode.nextNode.nextNode
            
        self.listLength -= 1
        return removedData
    
    def searchElement(self, targetData):
        currentNode = self.headNode
        currentIndex = 0
        
        while currentNode:
            if currentNode.elementData == targetData:
                return currentIndex
            currentNode = currentNode.nextNode
            currentIndex += 1
            
        return -1
    
    def isEmpty(self):
        return self.listLength == 0
    
    def getListLength(self):
        return self.listLength
    
    def clearList(self):
        self.headNode = None
        self.listLength = 0
    
    def __iter__(self):
        currentNode = self.headNode
        while currentNode:
            yield currentNode.elementData
            currentNode = currentNode.nextNode
    
    def setElementAtIndex(self, index: int, value):
        if index < 0 or index >= self.listLength:
            raise IndexError("Índice fuera de rango")
        current = self.headNode
        for _ in range(index):
            current = current.nextNode
        current.elementData = value
    
    def toPythonList(self):
        result = []
        current = self.headNode
        while current:
            result.append(str(current.elementData))
            current = current.nextNode
        return result
    
def __str__(self):
    if self.isEmpty():
        return "[]"
    
    buffer = LinkedList()
    current = self.headNode
    while current:
        buffer.addElementAtEnd(str(current.elementData))
        current = current.nextNode
    
    return "[" + self.joinLinkedList(buffer, " -> ") + "]"

@staticmethod
def joinLinkedList(ll: LinkedList, separator: str) -> str:
    if ll.isEmpty():
        return ""
    
    current = ll.headNode
    result = current.elementData
    current = current.nextNode
    
    while current:
        result += separator + current.elementData
        current = current.nextNode
    
    return result
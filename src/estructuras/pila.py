from .listaEnlazada import LinkedList

class Stack:
    def __init__(self):
        self.linkedListData = LinkedList()

    def push(self, element):
        self.linkedListData.addElementAtPosition(element, 0)

    def pop(self):
        if self.isEmpty():
            raise IndexError("Error: Se intento hacer pop en una pila vacia.")
        return self.linkedListData.removeElementAtIndex(0)

    def peek(self):
        if self.isEmpty():
            raise IndexError("Error: Se intento hacer peek en una pila vacia.")
        return self.linkedListData.getElementAtIndex(0)

    def isEmpty(self):
        return self.linkedListData.isEmpty()

    def size(self):
        return self.linkedListData.getListLength()
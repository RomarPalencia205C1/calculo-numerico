from .listaEnlazada import LinkedList

class Queue:
    def __init__(self):
        self.queueData = LinkedList()

    def enqueue(self, element):
        self.queueData.addToEnd(element)

    def dequeue(self):
        if self.isEmpty():
            raise IndexError("dequeue de la cola vacia")
        return self.queueData.removeFromHead() 

    def peek(self):
        if self.isEmpty():
            raise IndexError("peek de la cola vacia")
        return self.queueData.headNode.elementData

    def isEmpty(self):
        return self.queueData.isEmpty()

    def size(self):
        return self.queueData.size()
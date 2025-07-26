from estructuras.pila import Stack
from numeros.numero import Number
from algebra.matrix import Matrix
from errores.tiposErrores import FileOperationException

class EquationError(FileOperationException):
    pass

class EquationParser:
    def __init__(self, variables: dict):
        self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        self.variables = variables

    def _infixToPostfix(self, expression: str) -> list:
        tokens = self._tokenize(expression)
        
        outputQueue = []
        operatorStack = Stack()

        for token in tokens:
            if isinstance(token, (float, int, Matrix)):
                outputQueue.append(token)
            elif token in self.precedence:
                while (not operatorStack.isEmpty() and
                    operatorStack.peek() in self.precedence and
                    self.precedence.get(operatorStack.peek(), 0) >= self.precedence.get(token, 0)):
                    outputQueue.append(operatorStack.pop())
                operatorStack.push(token)
            elif token == '(':
                operatorStack.push(token)
            elif token == ')':
                while not operatorStack.isEmpty() and operatorStack.peek() != '(':
                    outputQueue.append(operatorStack.pop())
                if operatorStack.isEmpty():
                    raise EquationError("Parentesis no balanceados: falta '('")
                operatorStack.pop()

        while not operatorStack.isEmpty():
            op = operatorStack.pop()
            if op == '(':
                raise EquationError("Parentesis no balanceados: falta ')'")
            outputQueue.append(op)
            
        return outputQueue

    def _tokenize(self, expression: str) -> list:
        expression = expression.replace('(', ' ( ').replace(')', ' ) ')
        expression = expression.replace('+', ' + ').replace('-', ' - ')
        expression = expression.replace('*', ' * ').replace('/', ' / ')

        parts = expression.split()
        processed_parts = []
        
        for i, part in enumerate(parts):
            processed_parts.append(part)
            
            if i + 1 < len(parts):
                next_part = parts[i+1]

                is_operand = self._isNumber(part) or part in self.variables or part.isalpha()
                if is_operand and next_part == '(':
                    processed_parts.append('*')
                    continue
                
                if part == ')' and (self._isNumber(next_part) or next_part in self.variables or next_part.isalpha() or next_part == '('):
                    processed_parts.append('*')
                    continue

        processed_expression = ' '.join(processed_parts)
        
        tokens = []
        for part in processed_expression.split():
            if part in self.variables:
                tokens.append(self.variables[part])
            elif self._isNumber(part):
                tokens.append(float(part))
            elif part in self.precedence or part in ['(', ')']:
                tokens.append(part)
            else:
                if len(part) > 1 and all(c.isalpha() for c in part):
                    tokens.append('(')
                    for i, char_var in enumerate(part):
                        if char_var in self.variables:
                            tokens.append(self.variables[char_var])
                            if i < len(part) - 1:
                                tokens.append('*')
                        else:
                            raise EquationError(f"Variable desconocida '{char_var}' en el grupo '{part}'")
                    tokens.append(')')
                else:
                    raise EquationError(f"Token desconocido o expresion mal formada cerca de '{part}'")

        return tokens

    def _isNumber(self, s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    def evaluate(self, expression: str):
        try:
            postfixExpression = self._infixToPostfix(expression)
            evalStack = Stack()

            for token in postfixExpression:
                if isinstance(token, (float, int, Matrix)):
                    evalStack.push(token)
                elif token in self.precedence:
                    if evalStack.size() < 2:
                        raise EquationError(f"Argumentos insuficientes para el operador '{token}'")
                    
                    op2 = evalStack.pop()
                    op1 = evalStack.pop()
                    
                    result = self._performOperation(op1, op2, token)
                    evalStack.push(result)
            
            if evalStack.size() != 1:
                raise EquationError("Expresion mal formada.")
                
            return evalStack.pop()
        except Exception as e:
            failReason = f"Fallo en la evaluacion de la ecuacion. Causa: {type(e).__name__} - {e}"
            raise EquationError(failReason) from e

    def _performOperation(self, op1, op2, operator: str):
        if isinstance(op1, Matrix) or isinstance(op2, Matrix):
            if operator == '*':
                if isinstance(op1, Matrix) and isinstance(op2, (float, int)):
                    return op1.scalarMultiply(op2)
                if isinstance(op1, (float, int)) and isinstance(op2, Matrix):
                    return op2.scalarMultiply(op1)
            
            if not (isinstance(op1, Matrix) and isinstance(op2, Matrix)):
                raise EquationError("Operacion no valida entre Matriz y numero.")

            if operator == '+': return op1.add(op2)
            if operator == '-': return op1.subtract(op2)
            if operator == '*': return op1.multiply(op2)
        else:
            if operator == '+': return op1 + op2
            if operator == '-': return op1 - op2
            if operator == '*': return op1 * op2
            if operator == '/':
                if op2 == 0: raise EquationError("Division por cero.")
                return op1 / op2
        
        raise EquationError(f"Operador desconocido o no soportado: '{operator}'")
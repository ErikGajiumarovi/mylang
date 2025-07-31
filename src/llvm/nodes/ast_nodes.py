# Базовые узлы
class NumberNode:
    def __init__(self, value):
        self.value = value

class VariableNode:
    def __init__(self, name):
        self.name = name

class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class AssignNode:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class PrintNode:
    def __init__(self, value):
        self.value = value

# Новые узлы для расширенной функциональности
class StringNode:
    def __init__(self, value):
        self.value = value

class BooleanNode:
    def __init__(self, value):
        self.value = value  # True или False

class UnaryOpNode:
    def __init__(self, op, operand):
        self.op = op        # 'MINUS', 'NOT'
        self.operand = operand

class IfNode:
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body    # список statements
        self.else_body = else_body    # список statements или None

class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body              # список statements

class FunctionDefNode:
    def __init__(self, name, params, body):
        self.name = name              # имя функции
        self.params = params          # список параметров
        self.body = body              # список statements

class ReturnNode:
    def __init__(self, value=None):
        self.value = value            # выражение или None

class CallNode:
    def __init__(self, name, args):
        self.name = name              # имя функции
        self.args = args              # список аргументов
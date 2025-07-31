#!/usr/bin/env python3
"""
Классы AST узлов для языка программирования
"""

class ASTNode:
    """Базовый класс для узлов AST"""
    pass

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

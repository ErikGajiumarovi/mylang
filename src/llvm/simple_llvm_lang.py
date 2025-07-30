#!/usr/bin/env python3
"""
Простой язык программирования с LLVM
Поддерживает:
- Числа (integers)
- Арифметические операции (+, -, *, /)
- Переменные
- Вывод (print)

Пример программы:
x = 10
y = 20
z = x + y * 2
print z
"""

import llvmlite.binding as llvm
import llvmlite.ir as ir
from llvmlite import binding
import re

from llvm.lexer import Lexer

# Инициализация LLVM
llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

class Token:
    def __init__(self, type_, value, line=1):
        self.type = type_
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Token({self.type}, {self.value})"



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

class Parser:
    """Синтаксический анализатор - строит AST"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]
    
    def advance(self):
        self.pos += 1
    
    def parse(self):
        statements = []
        while self.current_token().type != 'EOF':
            if self.current_token().type == 'NEWLINE':
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements
    
    def parse_statement(self):
        if self.current_token().type == 'IDENTIFIER':
            # Присваивание: x = выражение
            name = self.current_token().value
            self.advance()
            if self.current_token().type == 'ASSIGN':
                self.advance()
                value = self.parse_expression()
                return AssignNode(name, value)
        elif self.current_token().type == 'PRINT':
            # Вывод: print выражение
            self.advance()
            value = self.parse_expression()
            return PrintNode(value)
        
        return None
    
    def parse_expression(self):
        return self.parse_term()
    
    def parse_term(self):
        left = self.parse_factor()
        
        while self.current_token().type in ['PLUS', 'MINUS']:
            op = self.current_token().type
            self.advance()
            right = self.parse_factor()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_factor(self):
        left = self.parse_primary()
        
        while self.current_token().type in ['MULTIPLY', 'DIVIDE']:
            op = self.current_token().type
            self.advance()
            right = self.parse_primary()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def parse_primary(self):
        token = self.current_token()
        
        if token.type == 'NUMBER':
            self.advance()
            return NumberNode(token.value)
        elif token.type == 'IDENTIFIER':
            self.advance()
            return VariableNode(token.value)
        elif token.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            if self.current_token().type == 'RPAREN':
                self.advance()
            return expr
        
        raise SyntaxError(f"Неожиданный токен: {token}")

class CodeGenerator:
    """Генератор LLVM IR кода"""
    
    def __init__(self):
        # Создаем модуль LLVM
        self.module = ir.Module("my_language")
        
        # Создаем главную функцию
        func_type = ir.FunctionType(ir.IntType(32), [])
        self.main_func = ir.Function(self.module, func_type, "main")
        self.block = self.main_func.append_basic_block("entry")
        self.builder = ir.IRBuilder(self.block)
        
        # Словарь для переменных (указатели на память)
        self.variables = {}
        
        # Объявляем функцию printf для вывода
        printf_type = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
        self.printf = ir.Function(self.module, printf_type, "printf")
    
    def generate(self, ast):
        """Генерирует код для списка инструкций"""
        for node in ast:
            self.visit(node)
        
        # Возвращаем 0 из main
        self.builder.ret(ir.Constant(ir.IntType(32), 0))
        
        return str(self.module)
    
    def visit(self, node):
        """Диспетчер для разных типов узлов AST"""
        if isinstance(node, NumberNode):
            return self.visit_number(node)
        elif isinstance(node, VariableNode):
            return self.visit_variable(node)
        elif isinstance(node, BinaryOpNode):
            return self.visit_binary_op(node)
        elif isinstance(node, AssignNode):
            return self.visit_assign(node)
        elif isinstance(node, PrintNode):
            return self.visit_print(node)
    
    def visit_number(self, node):
        return ir.Constant(ir.IntType(32), node.value)
    
    def visit_variable(self, node):
        if node.name not in self.variables:
            raise NameError(f"Переменная '{node.name}' не определена")
        return self.builder.load(self.variables[node.name])
    
    def visit_binary_op(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if node.op == 'PLUS':
            return self.builder.add(left, right)
        elif node.op == 'MINUS':
            return self.builder.sub(left, right)
        elif node.op == 'MULTIPLY':
            return self.builder.mul(left, right)
        elif node.op == 'DIVIDE':
            return self.builder.sdiv(left, right)
    
    def visit_assign(self, node):
        value = self.visit(node.value)
        
        # Создаем переменную если её ещё нет
        if node.name not in self.variables:
            var_ptr = self.builder.alloca(ir.IntType(32), name=node.name)
            self.variables[node.name] = var_ptr
        
        # Сохраняем значение
        self.builder.store(value, self.variables[node.name])
    
    def visit_print(self, node):
        value = self.visit(node.value)
        
        # Создаем строку формата для printf
        fmt_str = "%d\n\0"
        fmt_arg = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_str)), 
                             bytearray(fmt_str.encode("utf8")))
        fmt_ptr = self.builder.alloca(fmt_arg.type)
        self.builder.store(fmt_arg, fmt_ptr)
        fmt_ptr = self.builder.gep(fmt_ptr, [ir.Constant(ir.IntType(32), 0),
                                           ir.Constant(ir.IntType(32), 0)])
        
        # Вызываем printf
        self.builder.call(self.printf, [fmt_ptr, value])

def compile_and_run(source_code):
    """Компилирует и выполняет код"""
    print("=== Исходный код ===")
    print(source_code)
    print("\n=== Токены ===")
    
    # Лексический анализ
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    print([t for t in tokens if t.type != 'EOF'])
    
    print("\n=== AST (упрощенно) ===")
    # Синтаксический анализ
    parser = Parser(tokens)
    ast = parser.parse()
    for node in ast:
        print(f"{type(node).__name__}: {node.__dict__}")
    
    print("\n=== LLVM IR ===")
    # Генерация кода
    generator = CodeGenerator()
    llvm_ir = generator.generate(ast)
    print(llvm_ir)
    
    print("\n=== Выполнение ===")
    # Компиляция и выполнение
    try:
        # Создаем LLVM модуль
        llvm_module = binding.parse_assembly(llvm_ir)
        
        # Создаем движок выполнения
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        
        # Создаем JIT компилятор
        backing_mod = binding.parse_assembly("")
        engine = binding.create_mcjit_compiler(backing_mod, target_machine)
        engine.add_module(llvm_module)
        engine.finalize_object()
        
        # Получаем указатель на функцию main
        main_func_ptr = engine.get_function_address("main")
        
        # Выполняем
        import ctypes
        main_func = ctypes.CFUNCTYPE(ctypes.c_int)(main_func_ptr)
        result = main_func()
        
        print(f"Программа завершилась с кодом: {result}")
        
    except Exception as e:
        print(f"Ошибка выполнения: {e}")

# Пример использования
if __name__ == "__main__":
    # Тестовая программа
    code = """
x = 10
y = 20
z = x + y * 2
print z
print x
result = z - x
print result
"""
    
    compile_and_run(code)
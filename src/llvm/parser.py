from src.llvm.nodes.ast_nodes import (
    AssignNode, BinaryOpNode, NumberNode, VariableNode, PrintNode,
    StringNode, BooleanNode  # Добавляем новые узлы если есть
)


class Parser:
    """Синтаксический анализатор - строит AST"""

    # Приоритеты операторов (чем больше число, тем выше приоритет)
    BINARY_OPERATORS = {
        # Логические операторы (самый низкий приоритет)
        'OR': 1,
        'AND': 2,

        # Операторы сравнения
        'EQUAL': 3,
        'NOT_EQUAL': 3,
        'LESS': 4,
        'GREATER': 4,
        'LESS_EQUAL': 4,
        'GREATER_EQUAL': 4,

        # Арифметические операторы
        'PLUS': 5,
        'MINUS': 5,
        'MULTIPLY': 6,
        'DIVIDE': 6
    }

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[self.pos]

    def peek_token(self, offset=1):
        """Смотрим следующий токен без продвижения"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.tokens):
            return self.tokens[-1]  # EOF
        return self.tokens[peek_pos]

    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1

    def consume(self, expected_type):
        """Проверяем и потребляем токен ожидаемого типа"""
        token = self.current_token()
        if token.type != expected_type:
            raise SyntaxError(f"Ожидался {expected_type}, получен {token.type} на строке {token.line}")
        self.advance()
        return token

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
        """Парсит различные типы инструкций"""
        token = self.current_token()

        if token.type == 'IDENTIFIER':
            # Проверяем следующий токен для определения типа инструкции
            next_token = self.peek_token()
            if next_token.type == 'ASSIGN':
                return self.parse_assignment()
            else:
                # Это выражение-инструкция (например, вызов функции)
                expr = self.parse_expression()
                return expr

        elif token.type == 'PRINT':
            return self.parse_print()

        # Добавляем поддержку новых конструкций
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'DEF':
            return self.parse_function_def()

        else:
            # Выражение-инструкция
            return self.parse_expression()

    def parse_assignment(self):
        """Парсит присваивание: identifier = expression"""
        name = self.consume('IDENTIFIER').value
        self.consume('ASSIGN')
        value = self.parse_expression()
        return AssignNode(name, value)

    def parse_print(self):
        """Парсит print statement"""
        self.consume('PRINT')
        value = self.parse_expression()
        return PrintNode(value)

    def parse_if(self):
        """Парсит if statement (заглушка для будущего расширения)"""
        # TODO: Реализовать when добавим IfNode
        self.consume('IF')
        condition = self.parse_expression()
        # Пока просто возвращаем condition как выражение
        return condition

    def parse_while(self):
        """Парсит while statement (заглушка)"""
        # TODO: Реализовать when добавим WhileNode
        self.consume('WHILE')
        condition = self.parse_expression()
        return condition

    def parse_function_def(self):
        """Парсит function definition (заглушка)"""
        # TODO: Реализовать when добавим FunctionDefNode
        self.consume('DEF')
        name = self.consume('IDENTIFIER').value
        return VariableNode(name)  # Временная заглушка

    def parse_expression(self):
        """Парсит выражение с учетом приоритета операторов"""
        return self.parse_binary_expression(0)

    def parse_binary_expression(self, min_precedence):
        """Парсит бинарные выражения с учетом приоритета (алгоритм Pratt parser)"""
        left = self.parse_unary_expression()

        while True:
            token = self.current_token()
            if token.type not in self.BINARY_OPERATORS:
                break

            precedence = self.BINARY_OPERATORS[token.type]
            if precedence < min_precedence:
                break

            op = token.type
            self.advance()

            # Для правоассоциативных операторов (если будут) используем precedence
            # Для левоассоциативных - precedence + 1
            right = self.parse_binary_expression(precedence + 1)
            left = BinaryOpNode(left, op, right)

        return left

    def parse_unary_expression(self):
        """Парсит унарные выражения"""
        token = self.current_token()

        if token.type in ['MINUS', 'NOT']:  # Унарные операторы
            op = token.type
            self.advance()
            operand = self.parse_unary_expression()
            # TODO: Добавить UnaryOpNode когда будет нужен
            if op == 'MINUS':
                # Временно представляем как 0 - operand
                return BinaryOpNode(NumberNode(0), 'MINUS', operand)
            return operand  # Пока просто возвращаем операнд для NOT

        return self.parse_primary()

    def parse_primary(self):
        """Парсит первичные выражения"""
        token = self.current_token()

        if token.type == 'NUMBER':
            self.advance()
            return NumberNode(token.value)

        elif token.type == 'STRING':
            self.advance()
            # TODO: Добавить StringNode если нужен
            return NumberNode(0)  # Временная заглушка

        elif token.type == 'TRUE':
            self.advance()
            # TODO: Добавить BooleanNode если нужен
            return NumberNode(1)  # true как 1

        elif token.type == 'FALSE':
            self.advance()
            return NumberNode(0)  # false как 0

        elif token.type == 'NULL':
            self.advance()
            return NumberNode(0)  # null как 0

        elif token.type == 'IDENTIFIER':
            self.advance()
            return VariableNode(token.value)

        elif token.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr

        else:
            raise SyntaxError(f"Неожиданный токен: {token.type} ({token.value}) на строке {token.line}")

    def parse_block(self):
        """Парсит блок кода в фигурных скобках (для будущего использования)"""
        statements = []
        self.consume('LBRACE')

        while self.current_token().type != 'RBRACE' and self.current_token().type != 'EOF':
            if self.current_token().type == 'NEWLINE':
                self.advance()
                continue
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)

        self.consume('RBRACE')
        return statements
from src.llvm.nodes.ast_nodes import AssignNode, BinaryOpNode, NumberNode, VariableNode, PrintNode


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
from src.llvm.ast_token import Token


class Lexer:
    """Продвинутый лексический анализатор"""

    # Многосимвольные операторы (проверяются первыми)
    MULTI_CHAR_TOKENS = {
        '==': 'EQUAL',
        '!=': 'NOT_EQUAL',
        '<=': 'LESS_EQUAL',
        '>=': 'GREATER_EQUAL',
        '&&': 'AND',
        '||': 'OR',
        '++': 'INCREMENT',
        '--': 'DECREMENT'
    }

    # Односимвольные операторы
    SINGLE_CHAR_TOKENS = {
        '=': 'ASSIGN',
        '+': 'PLUS',
        '-': 'MINUS',
        '*': 'MULTIPLY',
        '/': 'DIVIDE',
        '(': 'LPAREN',
        ')': 'RPAREN',
        '{': 'LBRACE',
        '}': 'RBRACE',
        '<': 'LESS',
        '>': 'GREATER',
        '!': 'NOT',
        '\n': 'NEWLINE'
    }

    # Ключевые слова
    KEYWORDS = {
        'print': 'PRINT',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'def': 'DEF',
        'return': 'RETURN',
        'true': 'TRUE',
        'false': 'FALSE',
        'null': 'NULL'
    }

    WHITESPACE = ' \t'

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1

    def current_char(self):
        return self.text[self.pos] if self.pos < len(self.text) else None

    def peek_char(self, offset=1):
        """Смотрим следующий символ без продвижения"""
        peek_pos = self.pos + offset
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    def advance(self):
        if self.current_char() == '\n':
            self.line += 1
        self.pos += 1

    def skip_whitespace(self):
        while self.current_char() and self.current_char() in self.WHITESPACE:
            self.advance()

    def read_number(self):
        num = ''
        # Поддержка float
        has_dot = False
        while self.current_char() and (self.current_char().isdigit() or
                                       (self.current_char() == '.' and not has_dot)):
            if self.current_char() == '.':
                has_dot = True
            num += self.current_char()
            self.advance()
        return float(num) if has_dot else int(num)

    def read_identifier(self):
        ident = ''
        while (self.current_char() and
               (self.current_char().isalnum() or self.current_char() == '_')):
            ident += self.current_char()
            self.advance()
        return ident

    def read_string(self):
        """Читает строку в кавычках"""
        quote_char = self.current_char()  # ' или "
        self.advance()  # пропускаем открывающую кавычку

        string_value = ''
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':  # обработка escape-последовательностей
                self.advance()
                escape_char = self.current_char()
                if escape_char == 'n':
                    string_value += '\n'
                elif escape_char == 't':
                    string_value += '\t'
                elif escape_char == '\\':
                    string_value += '\\'
                elif escape_char in ('"', "'"):
                    string_value += escape_char
                else:
                    string_value += escape_char
            else:
                string_value += self.current_char()
            self.advance()

        if not self.current_char():
            raise SyntaxError(f"Незакрытая строка на строке {self.line}")

        self.advance()  # пропускаем закрывающую кавычку
        return string_value

    def make_token(self, token_type, value=None):
        return Token(token_type, value, self.line)

    def try_multi_char_token(self):
        """Пытается распознать многосимвольный оператор"""
        char = self.current_char()
        next_char = self.peek_char()

        if char and next_char:
            two_char = char + next_char
            if two_char in self.MULTI_CHAR_TOKENS:
                token_type = self.MULTI_CHAR_TOKENS[two_char]
                self.advance()  # первый символ
                self.advance()  # второй символ
                return self.make_token(token_type, two_char)
        return None

    def tokenize(self):
        tokens = []

        while self.current_char():
            char = self.current_char()

            # Пропускаем пробелы
            if char in self.WHITESPACE:
                self.skip_whitespace()
                continue

            # Числа
            if char.isdigit():
                tokens.append(self.make_token('NUMBER', self.read_number()))
                continue

            # Строки
            if char in ('"', "'"):
                tokens.append(self.make_token('STRING', self.read_string()))
                continue

            # Идентификаторы и ключевые слова
            if char.isalpha() or char == '_':
                ident = self.read_identifier()
                token_type = self.KEYWORDS.get(ident, 'IDENTIFIER')
                tokens.append(self.make_token(token_type, ident))
                continue

            # Пытаемся распознать многосимвольный оператор
            multi_token = self.try_multi_char_token()
            if multi_token:
                tokens.append(multi_token)
                continue

            # Односимвольные токены
            if char in self.SINGLE_CHAR_TOKENS:
                token_type = self.SINGLE_CHAR_TOKENS[char]
                tokens.append(self.make_token(token_type, char))
                self.advance()
                continue

            # Неизвестный символ
            raise SyntaxError(f"Неизвестный символ '{char}' на строке {self.line}")

        tokens.append(self.make_token('EOF', None))
        return tokens
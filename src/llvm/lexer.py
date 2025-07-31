from src.llvm.ast_token import Token


class Lexer:
    """Лексический анализатор - разбивает код на токены"""
    
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
    
    def current_char(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def advance(self):
        if self.current_char() == '\n':
            self.line += 1
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t':
            self.advance()
    
    def read_number(self):
        num = ''
        while self.current_char() and self.current_char().isdigit():
            num += self.current_char()
            self.advance()
        return int(num)
    
    def read_identifier(self):
        ident = ''
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            ident += self.current_char()
            self.advance()
        return ident
    
    def tokenize(self):
        tokens = []
        
        while self.current_char():
            if self.current_char() in ' \t':
                self.skip_whitespace()
            elif self.current_char() == '\n':
                tokens.append(Token('NEWLINE', '\n', self.line))
                self.advance()
            elif self.current_char().isdigit():
                tokens.append(Token('NUMBER', self.read_number(), self.line))
            elif self.current_char().isalpha():
                ident = self.read_identifier()
                if ident == 'print':
                    tokens.append(Token('PRINT', ident, self.line))
                else:
                    tokens.append(Token('IDENTIFIER', ident, self.line))
            elif self.current_char() == '=':
                tokens.append(Token('ASSIGN', '=', self.line))
                self.advance()
            elif self.current_char() == '+':
                tokens.append(Token('PLUS', '+', self.line))
                self.advance()
            elif self.current_char() == '-':
                tokens.append(Token('MINUS', '-', self.line))
                self.advance()
            elif self.current_char() == '*':
                tokens.append(Token('MULTIPLY', '*', self.line))
                self.advance()
            elif self.current_char() == '/':
                tokens.append(Token('DIVIDE', '/', self.line))
                self.advance()
            elif self.current_char() == '(':
                tokens.append(Token('LPAREN', '(', self.line))
                self.advance()
            elif self.current_char() == ')':
                tokens.append(Token('RPAREN', ')', self.line))
                self.advance()
            else:
                raise SyntaxError(f"Неизвестный символ '{self.current_char()}' на строке {self.line}")
        
        tokens.append(Token('EOF', None, self.line))
        return tokens
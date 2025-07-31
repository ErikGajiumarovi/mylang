class Token:
    def __init__(self, type_, value, line=1):
        self.type = type_
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value})"
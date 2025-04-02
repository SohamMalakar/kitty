from enum import Enum


class TokenType(Enum):
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULT = "MULT"
    DIV = "DIV"
    POW = "POW"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    SEMICOLON = "SEMICOLON"
    EOF = "EOF"
    UNK = "UNK"


class Token:
    def __init__(self, line_no: int, col_no: int, type_: TokenType, value=None):
        self.type = type_
        self.value = value
        self.line_no = line_no
        self.col_no = col_no

    def __repr__(self):
        return f"{self.type}" + (f": {self.value}" if self.value else "") + f" [line no: {self.line_no}, col no: {self.col_no}]"

    def __str__(self):
        return self.__repr__()


# test = Token(TokenType.INT, 10, 1, 0)
# print(str(test))

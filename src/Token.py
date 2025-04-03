from enum import Enum

from Position import Position

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
    def __init__(self, pos: Position, type_: TokenType, value=None):
        self.type = type_
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"{self.type}" + (f": {self.value}" if self.value else "") + f" [line no: {self.pos.ln}, col no: {self.pos.col}]"

    def __str__(self):
        return self.__repr__()

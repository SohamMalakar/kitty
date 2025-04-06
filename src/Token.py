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
    ILLEGAL = "ILLEGAL"


class Token:
    def __init__(self, type_: TokenType, value=None, pos_start: Position=None, pos_end: Position=None):
        self.type = type_
        self.value = value
        
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance() # exclusive

        if pos_end:
            self.pos_end = pos_end.copy()

    def __str__(self):
        return f"{self.type}" + (f": {self.value}" if self.value else "") + f" [line no: {self.pos_start.ln}, col no: {self.pos_start.col}]"

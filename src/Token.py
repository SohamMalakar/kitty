from enum import Enum

from Position import Position

class TokenType(Enum):
    IDENT = "IDENT"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOL = "BOOL"
    PLUS = "PLUS"
    MINUS = "MINUS"
    ASTERISK = "ASTERISK"
    SLASH = "SLASH"
    POW = "POW"
    MODULUS = "MODULUS"
    EQ = "EQ"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
    TRUE = "TRUE"
    FALSE = "FALSE"
    VAR = "VAR"
    TYPE = "TYPE"
    COLON = "COLON"
    DEF = "DEF"
    RETURN = "RETURN"
    ARROW = "ARROW"
    END = "END"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    EOF = "EOF"
    ILLEGAL = "ILLEGAL"
    GT = ">"
    LT = "<"
    GT_EQ = ">="
    LT_EQ = "<="
    NOT_EQ = "!="
    EQ_EQ = "=="


class Token:
    def __init__(self, type_: TokenType, literal=None, pos_start: Position=None, pos_end: Position=None):
        self.type = type_
        self.literal = literal
        
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance() # exclusive

        if pos_end:
            self.pos_end = pos_end.copy()

    def __str__(self):
        return f"{self.type}" + (f": {self.literal}" if self.literal else "") + f" [line no: {self.pos_start.ln}, col no: {self.pos_start.col}]"


KEYWORDS = {
    "if": TokenType.IF,
    "elif": TokenType.ELIF,
    "else": TokenType.ELSE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "var": TokenType.VAR,
    "def": TokenType.DEF,
    "end": TokenType.END,
    "return": TokenType.RETURN
}

TYPE_KEYWORDS = ["int", "float", "bool"]

def lookup_ident(ident: str) -> TokenType:
    tt = KEYWORDS.get(ident)
    if tt is not None:
        return tt
    
    if ident in TYPE_KEYWORDS:
        return TokenType.TYPE

    return TokenType.IDENT
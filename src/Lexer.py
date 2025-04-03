from Token import Token, TokenType
from Position import Position

import string

WHITESPACES = " \n\t"
DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS


class Lexer:
    def __init__(self, program: str):
        self.program = program
        self.current_char = None

        self.pos = Position(idx=-1, ln=1, col=0, fn="/path/to/the/file", ftxt=program)

        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.program[self.pos.idx] if self.pos.idx < len(self.program) else None

    def make_number(self):
        dot_count = 0
        number = ""

        start_pos = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + ".":
            number += self.current_char

            if self.current_char == ".":
                if dot_count == 0:
                    dot_count += 1
                else:
                    break

            self.advance()

        if dot_count == 0:
            token = Token(start_pos, TokenType.INT, int(number))
        else:
            token = Token(start_pos, TokenType.FLOAT, float(number))
        
        return token

    def skip_whitespaces(self):
        while self.current_char in WHITESPACES:
            self.advance()
    
    def skip_comment(self):
        while self.current_char != "\n":
            self.advance()
        
        self.advance()

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in DIGITS + ".":
                tokens.append(self.make_number())
            elif self.current_char in WHITESPACES:
                self.skip_whitespaces()
            elif self.current_char == "#":
                self.skip_comment()
            elif self.current_char == "+":
                tokens.append(Token(self.pos.copy(), TokenType.PLUS))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(self.pos.copy(), TokenType.MINUS))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(self.pos.copy(), TokenType.MULT))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(self.pos.copy(), TokenType.DIV))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(self.pos.copy(), TokenType.POW))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(self.pos.copy(), TokenType.LPAREN))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(self.pos.copy(), TokenType.RPAREN))
                self.advance()
            elif self.current_char == ";":
                tokens.append(Token(self.pos.copy(), TokenType.SEMICOLON))
                self.advance()

            else:
                tokens.append(Token(self.pos.copy(), TokenType.UNK))
                self.advance()

        tokens.append(Token(self.pos.copy(), TokenType.EOF))

        return tokens

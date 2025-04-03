
from Token import Token, TokenType

import string

WHITESPACES = " \n\t"
DIGITS = "0123456789"
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS


class Lexer:
    def __init__(self, program: str):
        self.program = program
        self.pos = -1
        self.current_char = None

        self.col_no = 0
        self.line_no = 0

        self.advance()

    def advance(self):
        self.pos += 1
        self.col_no += 1
        self.current_char = self.program[self.pos] if self.pos < len(self.program) else None

    def make_number(self):
        dot_count = 0
        number = ""

        start_pos = self.col_no

        while self.current_char != None and self.current_char in DIGITS + ".":
            number += self.current_char

            if self.current_char == ".":
                if dot_count == 0:
                    dot_count += 1
                else:
                    break

            self.advance()
        
        if dot_count == 0:
            token = Token(self.line_no, start_pos, TokenType.INT, int(number))
        else:
            token = Token(self.line_no, start_pos, TokenType.FLOAT, float(number))
        
        return token

    def skip_whitespaces(self):
        while self.current_char in WHITESPACES:
            if self.current_char == "\n":
                self.col_no = 0
                self.line_no += 1
            self.advance()
    
    def skip_comment(self):
        while self.current_char != "\n":
            self.advance()
        
        self.col_no = 0
        self.line_no += 1

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
                tokens.append(Token(self.line_no, self.col_no, TokenType.PLUS))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(self.line_no, self.col_no, TokenType.MINUS))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(self.line_no, self.col_no, TokenType.MULT))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(self.line_no, self.col_no, TokenType.DIV))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(self.line_no, self.col_no, TokenType.POW))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(self.line_no, self.col_no, TokenType.LPAREN))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(self.line_no, self.col_no, TokenType.RPAREN))
                self.advance()
            elif self.current_char == ";":
                tokens.append(Token(self.line_no, self.col_no, TokenType.SEMICOLON))
                self.advance()

            else:
                tokens.append(Token(self.line_no, self.col_no, TokenType.UNK))
                self.advance()

        tokens.append(Token(self.line_no, self.col_no, TokenType.EOF))

        return tokens
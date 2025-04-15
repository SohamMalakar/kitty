from Token import Token, TokenType, lookup_ident
from Position import Position

from Error import ErrorHandler

import string

WHITESPACES = string.whitespace
DIGITS = string.digits
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS


class Lexer:
    def __init__(self, program: str, path="<stdin>", error_handler=None):
        self.program = program
        self.current_char = None

        self.pos = Position(idx=-1, ln=1, col=0, fn=path, ftxt=program)

        self.error_handler = error_handler if error_handler else ErrorHandler()

        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.program[self.pos.idx] if self.pos.idx < len(self.program) else None

    def make_number(self):
        dot_count = 0
        number = ""

        start_pos = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                if dot_count == 0:
                    dot_count += 1
                else:
                    # Potential error
                    start_pos_ = self.pos.copy()
                    end_pos = self.pos.copy()
                    end_pos.advance()

                    self.error_handler.add_error(
                        start_pos_, 
                        end_pos, 
                        "Lexical Error", 
                        f"Invalid number format: multiple decimal points in '{number}.'"
                    )

                    break

            number += self.current_char
            self.advance()

        if dot_count == 0:
            token = Token(TokenType.INT, int(number), start_pos, self.pos)
        else:
            token = Token(TokenType.FLOAT, float(number), start_pos, self.pos)
        
        return token

    def skip_whitespaces(self):
        while self.current_char and self.current_char in WHITESPACES:
            self.advance()
    
    def skip_comment(self):
        while self.current_char != None and self.current_char != "\n":
            self.advance()
        
        self.advance()

    def make_identifier(self):
        ident = ""

        start_pos = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS_DIGITS + "_":
            ident += self.current_char
            self.advance()

        return Token(lookup_ident(ident), ident, start_pos, self.pos)

    def make_minus_or_arrow(self):
        literal = self.current_char
        start_pos = self.pos.copy()

        self.advance()

        if self.current_char == '>':
            literal += self.current_char
            self.advance()
            return Token(TokenType.ARROW, literal, start_pos, self.pos)
        
        return Token(TokenType.MINUS, literal, pos_start=start_pos)

    def make_equal_or_equal_equal(self):
        literal = self.current_char
        start_pos = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.EQ_EQ, literal, start_pos, self.pos)
        
        return Token(TokenType.EQ, literal, pos_start=start_pos)

    def make_greater_or_greater_equal(self):
        literal = self.current_char
        start_pos = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.GT_EQ, literal, start_pos, self.pos)
        
        return Token(TokenType.GT, literal, pos_start=start_pos)

    def make_lesser_or_lesser_equal(self):
        literal = self.current_char
        start_pos = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.LT_EQ, literal, start_pos, self.pos)
        
        return Token(TokenType.LT, literal, pos_start=start_pos)

    def make_not_equal(self):
        literal = self.current_char
        start_pos = self.pos.copy()
        self.advance()

        if self.current_char == "=":
            literal += self.current_char
            self.advance()
            return Token(TokenType.NOT_EQ, literal, start_pos, self.pos)
        
        self.error_handler.add_error(
            start_pos, 
            self.pos, 
            "Lexical error",
            "Invalid token: '!' must be followed by '='"
        )

        return Token(TokenType.ILLEGAL, literal, start_pos, self.pos)

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in LETTERS + "_":
                tokens.append(self.make_identifier())
            elif self.current_char in DIGITS + ".":
                # Potential error
                if self.current_char == "." and (self.pos.idx + 1 >= len(self.program) or self.program[self.pos.idx + 1] not in DIGITS):
                    start_pos = self.pos.copy()
                    end_pos = self.pos.copy()
                    end_pos.advance()

                    self.error_handler.add_error(
                        start_pos, 
                        end_pos, 
                        "Lexical Error",
                        "Invalid token: decimal point must be followed by a digit"
                    )

                    self.advance()
                    continue
                tokens.append(self.make_number())
            elif self.current_char in WHITESPACES:
                self.skip_whitespaces()
            elif self.current_char == "#":
                self.skip_comment()
            elif self.current_char == "+":
                tokens.append(Token(TokenType.PLUS, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == "-":
                tokens.append(self.make_minus_or_arrow())
                # tokens.append(Token(TokenType.MINUS, literal=self.current_char, pos_start=self.pos))
                # self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TokenType.ASTERISK, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TokenType.SLASH, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == "%":
                tokens.append(Token(TokenType.MODULUS, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == "^":
                tokens.append(Token(TokenType.POW, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == "=":
                tokens.append(self.make_equal_or_equal_equal())
                # tokens.append(Token(TokenType.EQ, literal=self.current_char, pos_start=self.pos))
                # self.advance()
            elif self.current_char == ":":
                tokens.append(Token(TokenType.COLON, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TokenType.LPAREN, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TokenType.RPAREN, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token(TokenType.COMMA, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == ";":
                tokens.append(Token(TokenType.SEMICOLON, literal=self.current_char, pos_start=self.pos))
                self.advance()
            elif self.current_char == ">":
                tokens.append(self.make_greater_or_greater_equal())
            elif self.current_char == "<":
                tokens.append(self.make_lesser_or_lesser_equal())
            elif self.current_char == "!":
                tokens.append(self.make_not_equal())
            else:
                # Potential error
                tokens.append(Token(TokenType.ILLEGAL, literal=self.current_char, pos_start=self.pos))
                
                start_pos = self.pos.copy()
                end_pos = self.pos.copy()
                end_pos.advance()

                self.error_handler.add_error(
                    start_pos, 
                    end_pos, 
                    "Lexical Error", 
                    f"Unrecognized character: '{self.current_char}'"
                )
                
                self.advance()

        tokens.append(Token(TokenType.EOF, pos_start=self.pos))

        return tokens

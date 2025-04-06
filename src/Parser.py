from enum import Enum, auto

from Token import Token, TokenType
from Error import ErrorHandler

from AST import Statement, Expression, Program
from AST import ExpressionStatement
from AST import InfixExpression
from AST import IntegerLiteral, FloatLiteral


class PrecedenceType(Enum):
    LOWEST = 0
    SUM = auto()
    PRODUCT = auto()
    EXPONENT = auto()


PRECEDENCES = {
    TokenType.PLUS: PrecedenceType.SUM,
    TokenType.MINUS: PrecedenceType.SUM,
    TokenType.MULT: PrecedenceType.PRODUCT,
    TokenType.DIV: PrecedenceType.PRODUCT,
    TokenType.POW: PrecedenceType.EXPONENT
}


class Parser:
    def __init__(self, tokens: list[Token], error_handler=None):
        self.tokens = tokens
        self.pos = -1
        self.current_token = None

        self.error_handler = error_handler if error_handler else ErrorHandler()
        
        self.prefix_parse_fns = {
            TokenType.INT: self.parse_int_literal,
            TokenType.FLOAT: self.parse_float_literal,
            TokenType.LPAREN: self.parse_grouped_expression
        }

        self.infix_parse_fns = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.MULT: self.parse_infix_expression,
            TokenType.DIV: self.parse_infix_expression,
            TokenType.POW: self.parse_infix_expression
        }

        self.advance()

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def synchronize(self, token_types: [TokenType]):
        while (self.current_token and 
            self.current_token.type not in token_types and 
            self.current_token.type != TokenType.EOF):
                self.advance()
        # self.advance()

    def peek_token(self):
        token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
        return token

    def current_precedence(self):
        prec = PRECEDENCES.get(self.current_token.type)
        if prec is None:
            return PrecedenceType.LOWEST
        return prec

    def peek_precedence(self):
        prec = PRECEDENCES.get(self.peek_token().type)
        if prec is None:
            return PrecedenceType.LOWEST
        return prec

    def parse_program(self):
        program = Program()

        while self.current_token and self.current_token.type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                if stmt is not None:
                    program.statements.append(stmt)
                
                self.advance()
            except Exception as e:
                # DEBUGGING PURPOSES
                print(f"Synchronizing after error: {e}")

        return program
    
    def parse_statement(self):
        return self.parse_expression_statement()
    
    def parse_expression_statement(self):
        expr = self.parse_expression(PrecedenceType.LOWEST)

        if self.peek_token() and self.peek_token().type == TokenType.SEMICOLON:
            self.advance()
        else:
            # Potential error
            token = self.current_token
            self.error_handler.add_error(
                token.pos_start, 
                token.pos_end, 
                "Syntax Error",
                "Expected semicolon ';' after expression")
            self.synchronize([TokenType.SEMICOLON])
            self.advance()
            raise

        stmt = ExpressionStatement(expr)

        return stmt
    
    def parse_expression(self, precedence):
        prefix_fn = self.prefix_parse_fns.get(self.current_token.type)
        if prefix_fn is None:
            # Potential error
            # Synchronization need to be handled
            raise Exception(f"No prefix parse function for {self.current_token.type}")
        
        left_expr = prefix_fn()

        while (self.peek_token() and
               self.peek_token().type != TokenType.SEMICOLON and 
               precedence.value < self.peek_precedence().value):

            infix_fn = self.infix_parse_fns.get(self.peek_token().type)
            if infix_fn is None:
                return left_expr
            
            self.advance()

            left_expr = infix_fn(left_expr)

        return left_expr

    def parse_infix_expression(self, left_node):
        infix_expr = InfixExpression(left_node=left_node, operator=self.current_token.type.value)

        precedence = self.current_precedence()

        # Handle right associativity for exponentiation
        if self.current_token.type == TokenType.POW:
            precedence = PrecedenceType(precedence.value - 1)

        self.advance()

        infix_expr.right_node = self.parse_expression(precedence)

        return infix_expr
    
    def parse_grouped_expression(self):
        self.advance()

        expr = self.parse_expression(PrecedenceType.LOWEST)

        if self.peek_token().type != TokenType.RPAREN:
            # Potential error
            # token = self.peek_token()
            token = self.current_token
            self.error_handler.add_error(
                token.pos_start, 
                token.pos_end, 
                "Syntax Error",
                "Expected closing parenthesis ')' afrer expression")
                # f"Expected closing parenthesis ')' after {token.pos_start.ftxt[token.pos_start.idx: token.pos_end.idx]}")
            self.synchronize([TokenType.SEMICOLON])
            self.advance()
            raise

        self.advance()

        return expr
        
    def parse_int_literal(self):
        int_lit = IntegerLiteral(self.current_token.value)
        return int_lit

    def parse_float_literal(self):
        float_lit = FloatLiteral(self.current_token.value)
        return float_lit

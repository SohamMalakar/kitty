from enum import Enum, auto

from Token import Token, TokenType
from Error import ErrorHandler

from AST import Statement, Expression, Program
from AST import ExpressionStatement, VarStatement
from AST import InfixExpression
from AST import IntegerLiteral, FloatLiteral, IdentifierLiteral


class PrecedenceType(Enum):
    LOWEST = 0
    SUM = auto()
    PRODUCT = auto()
    EXPONENT = auto()


PRECEDENCES = {
    TokenType.PLUS: PrecedenceType.SUM,
    TokenType.MINUS: PrecedenceType.SUM,
    TokenType.ASTERISK: PrecedenceType.PRODUCT,
    TokenType.SLASH: PrecedenceType.PRODUCT,
    TokenType.MODULUS: PrecedenceType.PRODUCT,
    TokenType.POW: PrecedenceType.EXPONENT
}


class Parser:
    def __init__(self, tokens: list[Token], error_handler=None):
        self.tokens = tokens
        self.pos = -1
        self.current_token = None
        self.error_handler = error_handler if error_handler else ErrorHandler()
        
        # Register prefix parsing functions
        self.prefix_parse_fns = {
            TokenType.INT: self.parse_int_literal,
            TokenType.FLOAT: self.parse_float_literal,
            TokenType.LPAREN: self.parse_grouped_expression
        }

        # Register infix parsing functions
        self.infix_parse_fns = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.SLASH: self.parse_infix_expression,
            TokenType.MODULUS: self.parse_infix_expression,
            TokenType.POW: self.parse_infix_expression
        }

        self.advance()

    def advance(self):
        """Move to the next token"""
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def synchronize(self, token_types: list[TokenType]):
        """Skip tokens until one of the specified token types is found"""
        while (self.current_token and 
               self.current_token.type not in token_types and 
               self.current_token.type != TokenType.EOF):
            self.advance()

    def peek_token(self):
        """Look at the next token without advancing"""
        return self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

    def current_precedence(self):
        """Get precedence of current token"""
        return PRECEDENCES.get(self.current_token.type, PrecedenceType.LOWEST)

    def peek_precedence(self):
        """Get precedence of next token"""
        token = self.peek_token()
        return PRECEDENCES.get(token.type, PrecedenceType.LOWEST) if token else PrecedenceType.LOWEST

    def expect_token(self, token_type, error_message, error_at_current=False):
        """Check if next token is of expected type and advance, otherwise handle error"""
        if self.peek_token() and self.peek_token().type == token_type:
            self.advance()
            return True
        else:
            token = self.current_token if error_at_current else self.peek_token()
            self.report_error(token, error_message)
            return False

    def report_error(self, token, message):
        """Report an error and synchronize parser state"""
        self.error_handler.add_error(
            token.pos_start, 
            token.pos_end, 
            "Syntax Error",
            message
        )
        self.synchronize([TokenType.SEMICOLON])
        self.advance()
        raise Exception(message)

    # def expect_semicolon(self):
    #     """Check for required semicolon at end of statement"""
    #     if not self.expect_token(TokenType.SEMICOLON, "Expected semicolon ';' after expression"):
    #         # Error already reported in expect_token
    #         token = self.current_token
    #         self.report_error(token, "Expected semicolon ';' after expression")

    def expect_semicolon(self):
        """Check for required semicolon at end of statement"""
        return self.expect_token(TokenType.SEMICOLON, "Expected semicolon ';' after expression", error_at_current=True)

    def parse_program(self):
        """Parse the entire program"""
        exceptions = []
        program = Program()

        while self.current_token and self.current_token.type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                if stmt is not None:
                    program.statements.append(stmt)
                
                # Advance because the current token is ';'
                self.advance()
            except Exception as e:
                exceptions.append(f"Synchronizing after error: {e}")

        if exceptions:
            print("===== SYNCHRONIZATION =====")
            for exception in exceptions:
                print(exception)

        return program
    
    def parse_statement(self):
        """Parse a statement based on the current token type"""
        match self.current_token.type:
            case TokenType.VAR:
                return self.parse_var_statement()
            case _:
                return self.parse_expression_statement()
    
    def parse_var_statement(self):
        """Parse a variable declaration statement"""
        stmt = VarStatement()

        # Parse variable name
        if not self.expect_token(TokenType.IDENT, "Expected identifier after 'var'"):
            return None
        stmt.name = IdentifierLiteral(self.current_token.literal)
        
        # Parse colon
        if not self.expect_token(TokenType.COLON, "Expected colon ':' after identifier"):
            return None
        
        # Parse type
        if not self.expect_token(TokenType.TYPE, "Expected type after ':'"):
            return None
        stmt.value_type = self.current_token.literal

        # Parse equals sign
        if not self.expect_token(TokenType.EQ, "Expected '=' after type"):
            return None
        
        # Parse initialization expression
        self.advance()
        stmt.value = self.parse_expression(PrecedenceType.LOWEST)

        # Parse semicolon
        # if not self.expect_token(TokenType.SEMICOLON, "Expected semicolon ';' after expression"):
        #     return None

        if not self.expect_semicolon():
            return None

        return stmt

    def parse_expression_statement(self):
        """Parse an expression statement"""
        expr = self.parse_expression(PrecedenceType.LOWEST)
        
        # Parse semicolon
        # if not self.expect_token(TokenType.SEMICOLON, "Expected semicolon ';' after expression"):
        #     return None

        # Parse semicolon
        if not self.expect_semicolon():
            return None

        return ExpressionStatement(expr)
    
    def parse_expression(self, precedence):
        """Parse an expression with the given precedence"""
        prefix_fn = self.prefix_parse_fns.get(self.current_token.type)
        if prefix_fn is None:
            token = self.current_token
            self.report_error(token, f"Expected expression, got {self.current_token.type}")
            return None
        
        left_expr = prefix_fn()

        # Parse infix expressions as long as they have higher precedence
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
        """Parse an infix expression (e.g., a + b)"""
        infix_expr = InfixExpression(left_node=left_node, operator=self.current_token.literal)

        precedence = self.current_precedence()

        # Handle right associativity for exponentiation
        if self.current_token.type == TokenType.POW:
            precedence = PrecedenceType(precedence.value - 1)

        self.advance()
        infix_expr.right_node = self.parse_expression(precedence)

        return infix_expr
    
    def parse_grouped_expression(self):
        """Parse an expression within parentheses"""
        self.advance()  # Skip the opening parenthesis
        expr = self.parse_expression(PrecedenceType.LOWEST)

        # if self.peek_token() and self.peek_token().type != TokenType.RPAREN:
        #     token = self.current_token
        #     self.report_error(token, "Expected closing parenthesis ')' after expression")
        #     return None

        if not self.expect_token(TokenType.RPAREN, "Expected closing parenthesis ')' after expression", error_at_current=True):
            return None

        self.advance()  # Skip the closing parenthesis
        return expr
        
    def parse_int_literal(self):
        """Parse an integer literal"""
        return IntegerLiteral(self.current_token.literal)

    def parse_float_literal(self):
        """Parse a float literal"""
        return FloatLiteral(self.current_token.literal)
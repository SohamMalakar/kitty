from enum import Enum, auto

from Token import Token, TokenType
from Error import ErrorHandler

from AST import Statement, Expression, Program
from AST import ExpressionStatement, VarStatement, FunctionStatement, ReturnStatement, AssignStatement, IfStatement
from AST import InfixExpression
from AST import IntegerLiteral, FloatLiteral, IdentifierLiteral, BooleanLiteral


class PrecedenceType(Enum):
    LOWEST = 0
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    EXPONENT = auto()


PRECEDENCES = {
    TokenType.PLUS: PrecedenceType.SUM,
    TokenType.MINUS: PrecedenceType.SUM,
    TokenType.ASTERISK: PrecedenceType.PRODUCT,
    TokenType.SLASH: PrecedenceType.PRODUCT,
    TokenType.MODULUS: PrecedenceType.PRODUCT,
    TokenType.POW: PrecedenceType.EXPONENT,
    TokenType.EQ_EQ: PrecedenceType.EQUALS,
    TokenType.NOT_EQ: PrecedenceType.EQUALS,
    TokenType.LT: PrecedenceType.LESSGREATER,
    TokenType.GT: PrecedenceType.LESSGREATER,
    TokenType.LT_EQ: PrecedenceType.LESSGREATER,
    TokenType.GT_EQ: PrecedenceType.LESSGREATER,
}


class Parser:
    def __init__(self, tokens: list[Token], error_handler=None):
        self.tokens = tokens
        self.pos = -1
        self.current_token = None
        self.exceptions = []
        self.error_handler = error_handler if error_handler else ErrorHandler()
        
        # Register prefix parsing functions
        self.prefix_parse_fns = {
            TokenType.IDENT: self.parse_indentifier,
            TokenType.INT: self.parse_int_literal,
            TokenType.FLOAT: self.parse_float_literal,
            TokenType.LPAREN: self.parse_grouped_expression,
            TokenType.TRUE: self.parse_boolean,
            TokenType.FALSE: self.parse_boolean
        }

        # Register infix parsing functions
        self.infix_parse_fns = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.SLASH: self.parse_infix_expression,
            TokenType.MODULUS: self.parse_infix_expression,
            TokenType.POW: self.parse_infix_expression,
            TokenType.EQ_EQ: self.parse_infix_expression,
            TokenType.NOT_EQ: self.parse_infix_expression,
            TokenType.LT: self.parse_infix_expression,
            TokenType.GT: self.parse_infix_expression,
            TokenType.LT_EQ: self.parse_infix_expression,
            TokenType.GT_EQ: self.parse_infix_expression
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

    def expect_token(self, token_type, error_message, do_advance=True, look_current=False, error_at_current=False):
        """Check if next token is of expected type and advance, otherwise handle error"""

        if look_current:
            error_at_current = True

        token = self.current_token if look_current else self.peek_token()

        if token and token.type == token_type:
            if do_advance:
                self.advance()
            return True
        else:
            token = self.current_token if error_at_current else self.peek_token()
            self.report_error(token, error_message)
            return False

    def report_error(self, token, message, do_advance=True, sync_tokens=[TokenType.SEMICOLON]):
        """Report an error and synchronize parser state"""
        self.error_handler.add_error(
            token.pos_start, 
            token.pos_end, 
            "Syntax Error",
            message
        )
        self.synchronize(sync_tokens)
        if do_advance:
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
        program = Program()

        while self.current_token and self.current_token.type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                if stmt is not None:
                    program.statements.append(stmt)
                
                # Advance because the current token is ';'
                self.advance()
            except Exception as e:
                self.exceptions.append(f"Synchronizing after error: {e}")

        if self.exceptions:
            print("===== SYNCHRONIZATION =====")
            for exception in self.exceptions:
                print(exception)

        return program
    
    def parse_statement(self):
        """Parse a statement based on the current token type"""

        if self.current_token.type == TokenType.IDENT and self.peek_token().type == TokenType.EQ:
            return self.parse_assignment_statement()

        match self.current_token.type:
            case TokenType.VAR:
                return self.parse_var_statement()
            case TokenType.DEF:
                return self.parse_function_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case TokenType.IF:
                return self.parse_if_statement()
            case _:
                return self.parse_expression_statement()
    
    def parse_assignment_statement(self):
        stmt = AssignStatement()

        stmt.ident = self.parse_indentifier()

        self.advance() # skips the 'IDENT'
        self.advance() # skips the '='

        stmt.right_value = self.parse_expression(PrecedenceType.LOWEST)

        if not self.expect_semicolon():
            return None

        return stmt

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

    def parse_if_statement(self):
        stmt = IfStatement()

        self.advance()

        stmt.condition = self.parse_expression(PrecedenceType.LOWEST)

        if not self.expect_token(TokenType.COLON, "Expected colon ':' after condition"):
            return None
        
        self.advance()

        while self.current_token and self.current_token.type not in [TokenType.ELIF, TokenType.ELSE, TokenType.END]:
            try:
                stmt.body.append(self.parse_statement())
                self.advance()
            except Exception as e:
                self.exceptions.append(f"Synchronizing after error: {e}")
        
        if self.current_token and self.current_token.type == TokenType.ELIF:
            stmt.else_body.append(self.parse_if_statement())
        elif self.current_token and self.current_token.type == TokenType.ELSE:
            if not self.expect_token(TokenType.COLON, "Expected colon ':' after condition"):
                return None
            
            self.advance()

            while self.current_token and self.current_token.type != TokenType.END:
                try:
                    stmt.else_body.append(self.parse_statement())
                    self.advance()
                except Exception as e:
                    self.exceptions.append(f"Synchronizing after error: {e}")
        
        return stmt

    # def parse_if_statement(self):
    #     stmt = IfStatement()

    #     self.advance()

    #     stmt.condition = self.parse_expression(PrecedenceType.LOWEST)

    #     if not self.expect_token(TokenType.COLON, "Expected colon ':' after condition"):
    #         return None
        
    #     self.advance()

    #     # Parse statements
    #     while self.current_token and self.current_token.type not in [TokenType.ELIF, TokenType.ELSE, TokenType.END]:
    #         try:
    #             stmt.body.append(self.parse_statement())
    #             self.advance()
    #         except Exception as e:
    #             self.exceptions.append(f"Synchronizing after error: {e}")
        
    #     # Parse elif statements
    #     elif_conditions = []
    #     elif_bodies = []
        
    #     while self.current_token and self.current_token.type == TokenType.ELIF:
    #         self.advance()

    #         elif_condition = self.parse_expression(PrecedenceType.LOWEST)

    #         if not self.expect_token(TokenType.COLON, "Expected colon ':' after elif condition"):
    #             return None
            
    #         self.advance()

    #         elif_body = []

    #         while self.current_token and self.current_token.type not in [TokenType.ELIF, TokenType.ELSE, TokenType.END]:
    #             try:
    #                 elif_body.append(self.parse_statement())
    #                 self.advance()
    #             except Exception as e:
    #                 self.exceptions.append(f"Synchronizing after error: {e}")
            
    #         elif_conditions.append(elif_condition)
    #         elif_bodies.append(elif_body)
        
    #     stmt.elif_conditions = elif_conditions
    #     stmt.elif_bodies = elif_bodies

    #     # Parse else statement
    #     if self.current_token and self.current_token.type == TokenType.ELSE:
    #         # self.advance()

    #         if not self.expect_token(TokenType.COLON, "Expected colon ':' after else"):
    #             return None
            
    #         self.advance()

    #         stmt.else_body = []

    #         while self.current_token and self.current_token.type != TokenType.END:
    #             try:
    #                 stmt.else_body.append(self.parse_statement())
    #                 self.advance()
    #             except Exception as e:
    #                 self.exceptions.append(f"Synchronizing after error: {e}")
        
    #     # Parse end statement
    #     if not self.expect_token(TokenType.END, "Expected end keyword after a block", look_current=True, do_advance=False):
    #         return None

    #     return stmt

    def parse_function_statement(self):
        func = FunctionStatement()

        try:
            if not self.expect_token(TokenType.IDENT, "Expected identifier after 'def'", error_at_current=True):
                return None

            func.name = IdentifierLiteral(self.current_token.literal)

            if not self.expect_token(TokenType.LPAREN, "Expected left parenthesis '(", error_at_current=True):
                return None
            
            func.parameters = [] # TODO: implement

            if not self.expect_token(TokenType.RPAREN, "Expected right parenthesis ')'", error_at_current=True):
                return None

            if not self.expect_token(TokenType.ARROW, "Expected an arrow '->'", error_at_current=True):
                return None

            if not self.expect_token(TokenType.TYPE, "Expected type after '->'", error_at_current=True):
                return None
            
            func.return_type = self.current_token.literal
            
            if not self.expect_token(TokenType.COLON, "Expected colon ':' after type", error_at_current=True):
                return None
            
            self.advance()
        except Exception as e:
            self.exceptions.append(f"Synchronizing after error: {e}")

        # Parse statements
        # while self.current_token and self.current_token.type != TokenType.END:
        #     func.body.append(self.parse_statement())
        #     self.advance()

        # Parse statements
        while self.current_token and self.current_token.type != TokenType.END and self.current_token.type != TokenType.EOF:
            try:
                stmt = self.parse_statement()
                if stmt is not None:
                    func.body.append(stmt)
                self.advance()
            except Exception as e:
                self.exceptions.append(f"Synchronizing after error: {e}")

        if not self.expect_token(TokenType.END, "Expected end keyword after a block", look_current=True, do_advance=False):
            return None

        return func

    def parse_return_statement(self):
        stmt = ReturnStatement()

        self.advance()

        stmt.return_value = self.parse_expression(PrecedenceType.LOWEST)

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

        # self.advance()  # Skip the closing parenthesis
        return expr

    def parse_indentifier(self):
        return IdentifierLiteral(self.current_token.literal)

    def parse_int_literal(self):
        """Parse an integer literal"""
        return IntegerLiteral(self.current_token.literal)

    def parse_float_literal(self):
        """Parse a float literal"""
        return FloatLiteral(self.current_token.literal)
    
    def parse_boolean(self):
        """Parse a boolean literal"""
        return BooleanLiteral(self.current_token.literal == "true")
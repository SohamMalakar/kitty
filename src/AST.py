from enum import Enum


class NodeType(Enum):
    Program = "Program"
    ExpressionStatement = "ExpressionStatement"
    FunctionStatement = "FunctionStatement"
    ReturnStatement = "ReturnStatement"
    AssignStatement = "AssignStatement"
    IfStatement = "IfStatement"
    VarStatement = "VarStatement"
    InfixExpression = "InfixExpression"
    CallExpression = "CallExpression"
    IntegerLiteral = "IntegerLiteral"
    FloatLiteral = "FloatLiteral"
    IdentifierLiteral = "IdentifierLiteral"
    BooleanLiteral = "BooleanLiteral"


class Node:
    def type(self):
        pass

    def json(self):
        pass


class Statement(Node):
    pass


class Expression(Node):
    pass


class Program(Node):
    def __init__(self):
        self.statements = []
    
    def type(self):
        return NodeType.Program
    
    def json(self):
        return {
            "type": self.type().value,
            "statements": [{stmt.type().value: stmt.json()} for stmt in self.statements]
        }


class ExpressionStatement(Statement):
    def __init__(self, expr: Expression = None):
        self.expr = expr

    def type(self):
        return NodeType.ExpressionStatement

    def json(self):
        return {
            "type": self.type().value,
            "expr": self.expr.json()
        }


class AssignStatement(Statement):
    def __init__(self, ident: Expression = None, right_value: Expression = None):
        self.ident = ident
        self.right_value = right_value
    
    def type(self):
        return NodeType.AssignStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "ident": self.ident.json(),
            "right_value": self.right_value.json()
        }


class IfStatement(Statement):
    def __init__(self, condition: Expression = None, body: list = None, else_body: list = None):
        self.condition = condition
        self.body = body or []
        self.else_body = else_body or []
    
    def type(self):
        return NodeType.IfStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "condition": self.condition.json(),
            "body": [stmt.json() for stmt in self.body],
            "else_body": [stmt.json() for stmt in self.else_body]
        }

# Nice implementation but wont work
# class IfStatement(Statement):
#     def __init__(self, condition: Expression = None, body: list = None, elif_conditions: list = None, 
#                  elif_bodies: list = None, else_body: list = None):
#         self.condition = condition
#         self.body = body or []
#         self.elif_conditions = elif_conditions or []
#         self.elif_bodies = elif_bodies or []
#         self.else_body = else_body or []

#     def type(self):
#         return NodeType.IfStatement
    
#     def json(self):
#         elif_conditions = []
#         if self.elif_conditions:
#             for i in range(len(self.elif_conditions)):
#                 elif_conditions.append({
#                     "condition": self.elif_conditions[i].json(),
#                     "body": [stmt.json() for stmt in self.elif_bodies[i]]
#                 })

#         return {
#             "type": self.type().value,
#             "condition": self.condition.json(),
#             "body": [stmt.json() for stmt in self.body],
#             "elif_conditions": elif_conditions,
#             # "else_body": [stmt.json() for stmt in self.else_body] if self.else_body else None
#             "else_body": [stmt.json() for stmt in self.else_body] if self.else_body else []
#         }


# class IfStatement(Statement):
#     def __init__(self, condition: Expression = None, body: list = None, elif_conditions: list = None, elif_bodies: list = None, else_body: list = None):
#         self.condition = condition
#         self.body = body or []
#         self.elif_conditions = elif_conditions or []
#         self.elif_bodies = elif_bodies or []
#         self.else_body = else_body or []

#     def type(self):
#         return NodeType.IfStatement
    
#     def json(self):
#         elif_conditions = []
#         for i in range(len(self.elif_conditions)):
#             elif_conditions.append({
#                 "condition": self.elif_conditions[i].json(),
#                 "body": [stmt.json() for stmt in self.elif_bodies[i]]
#             })

#         return {
#             "type": self.type().value,
#             "condition": self.condition.json(),
#             "body": [stmt.json() for stmt in self.body],
#             "elif_conditions": elif_conditions,
#             "else_body": [stmt.json() for stmt in self.else_body] if self.else_body else None
#         }


class FunctionStatement(Statement):
    def __init__(self, parameters = None, body = None, name = None, return_type: str = None):
        self.parameters = parameters or []
        self.body = body or []
        self.name = name
        self.return_type = return_type

    def type(self):
        return NodeType.FunctionStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "name": self.name.json(),
            "return_type": self.return_type,
            "parameters": [p.json() for p in self.parameters],
            "body": [stmt.json() for stmt in self.body]
        }


class ReturnStatement(Statement):
    def __init__(self, return_value: Expression = None):
        self.return_value = return_value
    
    def type(self):
        return NodeType.ReturnStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "return_value": self.return_value.json()
        }


class VarStatement(Statement):
    def __init__(self, name: Expression = None, value: Expression = None, value_type: str = None):
        self.name = name
        self.value = value
        self.value_type = value_type
    
    def type(self):
        return NodeType.VarStatement
    
    def json(self):
        return {
            "type": self.type().value,
            "name": self.name.json(),
            "value": self.value.json(),
            "value_type": self.value_type
        }


class InfixExpression(Expression):
    def __init__(self, left_node: Expression, operator: str, right_node: Expression = None):
        self.left_node: Expression = left_node
        self.operator: str = operator
        self.right_node: Expression = right_node

    def type(self):
        return NodeType.InfixExpression

    def json(self):
        return {
            "type": self.type().value,
            "left_node": self.left_node.json(),
            "operator": self.operator,
            "right_node": self.right_node.json()
        }


class CallExpression(Expression):
    def __init__(self, function: Expression = None, args: list[Expression] = None):
        self.function = function # IdentifierLiteral
        self.args = args or []

    def type(self):
        return NodeType.CallExpression
    
    def json(self):
        return {
            "type": self.type().value,
            "function": self.function.json(),
            "args": [arg.json() for arg in self.args]
        }


class IntegerLiteral(Expression):
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.IntegerLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }


class FloatLiteral(Expression):
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.FloatLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }

class IdentifierLiteral(Expression):
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.IdentifierLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }

class BooleanLiteral(Expression):
    def __init__(self, value):
        self.value = value
    
    def type(self):
        return NodeType.BooleanLiteral
    
    def json(self):
        return {
            "type": self.type().value,
            "value": self.value
        }
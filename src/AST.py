from enum import Enum


class NodeType(Enum):
    Program = "Program"
    ExpressionStatement = "ExpressionStatement"
    InfixExpression = "InfixExpression"
    IntegerLiteral = "IntegerLiteral"
    FloatLiteral = "FloatLiteral"


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
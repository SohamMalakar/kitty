from llvmlite import ir

from AST import Node, NodeType, Program, Expression
from AST import ExpressionStatement, VarStatement, FunctionStatement, ReturnStatement, AssignStatement, IfStatement
from AST import InfixExpression
from AST import IntegerLiteral, FloatLiteral, IdentifierLiteral, BooleanLiteral

from Environment import Environment

class Compiler:
    def __init__(self):
        self.type_map: dict[str, ir.Type] = {
            "int": ir.IntType(32),
            "float": ir.FloatType(),
            "bool": ir.IntType(1)
        }

        self.module: ir.Module = ir.Module("main")

        self.builder: ir.IRBuilder = ir.IRBuilder()

        self.env: Environment = Environment()

        self.errors = []

        self.initialize_builtins()
    
    def initialize_builtins(self):
        def init_booleans(self) -> tuple[ir.GlobalVariable, ir.GlobalVariable]:
            bool_type: ir.Type = self.type_map["bool"]

            true_var = ir.GlobalVariable(self.module, bool_type, "true")
            true_var.initializer = ir.Constant(bool_type, 1)
            true_var.global_constant = True

            false_var = ir.GlobalVariable(self.module, bool_type, "false")
            false_var.initializer = ir.Constant(bool_type, 0)
            false_var.global_constant = True

            return true_var, false_var
        
        true_var, false_var = init_booleans(self)

        self.env.define("true", true_var, true_var.type)
        self.env.define("false", false_var, true_var.type)
    
    def compile(self, node: Node):
        match node.type():
            case NodeType.Program:
                self.visit_program(node)
            
            case NodeType.ExpressionStatement:
                self.visit_expression_statement(node)
            
            case NodeType.VarStatement:
                self.visit_var_statement(node)
            
            case NodeType.FunctionStatement:
                self.visit_function_statement(node)
            
            case NodeType.ReturnStatement:
                self.visit_return_statement(node)
            
            case NodeType.AssignStatement:
                self.visit_assign_statement(node)
            
            case NodeType.IfStatement:
                self.visit_if_statement(node)

            case NodeType.InfixExpression:
                self.visit_infix_expression(node)

    def visit_program(self, node: Program):
        func_name = "main"
        param_types: list[ir.Type] = []
        return_type: ir.Type = self.type_map["int"]

        fnty = ir.FunctionType(return_type, param_types)
        func = ir.Function(self.module, fnty, name=func_name)

        block = func.append_basic_block(f"{func_name}_entry")

        self.builder = ir.IRBuilder(block)

        for stmt in node.statements:
            self.compile(stmt)
        
        return_value: ir.Constant = ir.Constant(self.type_map["int"], 69)
        self.builder.ret(return_value)
    
    def visit_expression_statement(self, node: ExpressionStatement):
        self.compile(node.expr)
    
    def visit_if_statement(self, node: IfStatement):
        condition = node.condition
        body = node.body
        else_body = node.else_body

        test, _ = self.resolve_value(condition)

        if else_body is None:
            with self.builder.if_then(test):
                for stmt in body:
                    self.compile(stmt)
        else:
            with self.builder.if_else(test) as (then, otherwise):
                with then:
                    for stmt in body:
                        self.compile(stmt)
                with otherwise:
                    for stmt in else_body:
                        self.compile(stmt)


    def visit_var_statement(self, node: VarStatement):
        name = node.name.value
        value = node.value
        value_type = node.value_type # TODO: Implement

        value, Type = self.resolve_value(node=value)

        if self.env.lookup(name) is None:
            # Define and allocate the variable
            ptr = self.builder.alloca(Type)

            # Starting the value to the ptr
            self.builder.store(value, ptr)

            # Add the variable to the environment
            self.env.define(name, ptr, Type)
        else:
            ptr, _ = self.env.lookup(name)
            self.builder.store(value, ptr)

    def visit_function_statement(self, node: FunctionStatement):
        name: str = node.name.value
        body = node.body
        params: list[IdentifierLiteral] = node.parameters

        # Keep track of the names of each parameter
        param_names: list[str] = [p.value for p in params]

        # Keep track of the types for each parameter
        param_types: list[ir.Type] = []  # TODO

        return_type: ir.Type = self.type_map[node.return_type]

        fnty: ir.FunctionType = ir.FunctionType(return_type, param_types)
        func: ir.Function = ir.Function(self.module, fnty, name=name)

        block: ir.Block = func.append_basic_block(f'{name}_entry')

        previous_builder = self.builder

        self.builder = ir.IRBuilder(block)

        previous_env = self.env

        self.env = Environment(parent=self.env)
        self.env.define(name, func, return_type)

        for stmt in body:
            self.compile(stmt)

        self.env = previous_env
        self.env.define(name, func, return_type)

        self.builder = previous_builder

    def visit_return_statement(self, node: ReturnStatement):
        value: Expression = node.return_value
        value, Type = self.resolve_value(value)

        self.builder.ret(value)
    
    def visit_assign_statement(self, node: AssignStatement):
        name = node.ident.value
        value = node.right_value

        value, Type = self.resolve_value(value)

        if self.env.lookup(name) is None:
            self.errors.append(f"COMPILE ERROR: Identifier {name} has not been declared before it was re-assigned.")
        else:
            ptr, _ = self.env.lookup(name)
            self.builder.store(value, ptr)

    def visit_infix_expression(self, node: InfixExpression):
        operator: str = node.operator
        left_value, left_type = self.resolve_value(node.left_node)
        right_value, right_type = self.resolve_value(node.right_node)
    
        value = None
        Type = None

        if isinstance(right_type, ir.IntType) and isinstance(left_type, ir.IntType):
            Type = self.type_map["int"]
            match operator:
                case '+':
                    value = self.builder.add(left_value, right_value)
                case '-':
                    value = self.builder.sub(left_value, right_value)
                case '*':
                    value = self.builder.mul(left_value, right_value)
                case '/':
                    value = self.builder.sdiv(left_value, right_value)
                case '%':
                    value = self.builder.srem(left_value, right_value)
                case '^':
                    pass # TODO: implement
                case "<":
                    value = self.builder.icmp_signed("<", left_value, right_value)
                    Type = ir.IntType(1)
                case ">":
                    value = self.builder.icmp_signed(">", left_value, right_value)
                    Type = ir.IntType(1)
                case "<=":
                    value = self.builder.icmp_signed("<=", left_value, right_value)
                    Type = ir.IntType(1)
                case ">=":
                    value = self.builder.icmp_signed(">=", left_value, right_value)
                    Type = ir.IntType(1)
                case "==":
                    value = self.builder.icmp_signed("==", left_value, right_value)
                    Type = ir.IntType(1)
                case "!=":
                    value = self.builder.icmp_signed("!=", left_value, right_value)
                    Type = ir.IntType(1)

        elif isinstance(right_type, ir.FloatType) and isinstance(left_type, ir.FloatType):
            Type = self.type_map["float"]
            match operator:
                case '+':
                    value = self.builder.fadd(left_value, right_value)
                case '-':
                    value = self.builder.fsub(left_value, right_value)
                case '*':
                    value = self.builder.fmul(left_value, right_value)
                case '/':
                    value = self.builder.fdiv(left_value, right_value)
                case '%':
                    value = self.builder.frem(left_value, right_value)
                case '^':
                    pass # TODO: implement
                case "<":
                    value = self.builder.fcmp_ordered("<", left_value, right_value)
                    Type = ir.IntType(1)
                case ">":
                    value = self.builder.fcmp_ordered(">", left_value, right_value)
                    Type = ir.IntType(1)
                case "<=":
                    value = self.builder.fcmp_ordered("<=", left_value, right_value)
                    Type = ir.IntType(1)
                case ">=":
                    value = self.builder.fcmp_ordered(">=", left_value, right_value)
                    Type = ir.IntType(1)
                case "==":
                    value = self.builder.fcmp_ordered("==", left_value, right_value)
                    Type = ir.IntType(1)
                case "!=":
                    value = self.builder.fcmp_ordered("!=", left_value, right_value)
                    Type = ir.IntType(1)

        return value, Type

    def resolve_value(self, node: Expression, value_type: str = None) -> tuple[ir.Value, ir.Type]:
        match node.type():
            case NodeType.IntegerLiteral:
                node: IntegerLiteral = node
                value, Type = node.value, self.type_map["int" if value_type is None else value_type]
                return ir.Constant(Type, value), Type
            case NodeType.FloatLiteral:
                node: FloatLiteral = node
                value, Type = node.value, self.type_map["float" if value_type is None else value_type]
                return ir.Constant(Type, value), Type
            case NodeType.IdentifierLiteral:
                node: IdentifierLiteral = node
                ptr, Type = self.env.lookup(node.value)
                return self.builder.load(ptr), Type
            case NodeType.BooleanLiteral:
                node: BooleanLiteral = node
                return ir.Constant(ir.IntType(1), 1 if node.value else 0), ir.IntType(1)
            
            case NodeType.InfixExpression:
                return self.visit_infix_expression(node)

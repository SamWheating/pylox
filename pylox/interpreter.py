from pylox.types import LoxObject
from pylox.exceptions import LoxRuntimeError, LoxAssertionError, LoxReturn
from pylox.token_type import TokenType
from pylox.token import Token
from pylox.environment import Environment
from pylox.lox_callable import LoxCallable
from pylox.lox_function import LoxFunction
from pylox.lox_class import LoxClass
from pylox.lox_instance import LoxInstance

from pylox import expr
from pylox import stmt

from typing import List

import time

class ClockBuiltinFn(LoxCallable):

    # Defines a builtin function clock() which returns the current epoch time in seconds
    # TODO: move the builtin functions to their own file?

    def arity(self) -> int:
        return 0

    def call(self, interpreter, arguments: List[LoxObject]):
        return time.time()

    def __str__(self):
        return "< native fn >"


class Interpreter(expr.Visitor, stmt.Visitor):

    def __init__(self, runtime):
        self.runtime = runtime
        self.globals = Environment()
        self.environment = self.globals
        self.locals = {}

        self.globals.define("clock", ClockBuiltinFn())

    def interpret(self, statements: List[stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            self.runtime.runtime_error(e)
        except LoxAssertionError as e:
            self.runtime.assertion_error(e)

    def execute(self, statement: stmt.Stmt):
        statement.accept(self)

    def resolve(self, expression: expr.Expr, depth: int) -> None:
        self.locals[expression] = depth

    def visit_literal_expr(self, expr) -> LoxObject:
        return expr.value

    def visit_if_stmt(self, statement: stmt.Stmt) -> None:
        if self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.then_branch)
        elif statement.else_branch is not None:
            self.execute(statement.else_branch)

    def visit_grouping_expr(self, expr) -> LoxObject:
        return self.evaluate(expr.expression)

    def visit_logical_expr(self, expression: expr.Expr) -> LoxObject:
        left = self.evaluate(expression.left)
        if expression.operator.type == TokenType.OR:
            if self.is_truthy(left):
                return left
        elif expression.operator.type == TokenType.AND:
            if not self.is_truthy(left):
                return left
        
        return self.evaluate(expression.right)

    def visit_unary_expr(self, expr) -> LoxObject:
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.BANG:
                return not self.is_truthy(right)
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -1 * float(right)

    def visit_binary_expr(self, expr) -> LoxObject:

        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.type:
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return left != right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return float(left) - float(right)
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                if right == 0:
                    raise LoxRuntimeError(expr.operator, "Runtime Error: Cannot Divide by zero.")
                return float(left) / float(right)
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return float(left) * float(right)
            case TokenType.PLUS:
                if (type(left) == type(right)) and type(left) in [str, float]:
                    return left + right
                raise LoxRuntimeError(
                    expr.operator, "Runtime Error: Operands must be two numbers or two strings"
                )
            case _:
                pass  # TODO: Handle errors n stuff

    def visit_expression_stmt(self, statement: stmt.Expression) -> None:
        self.evaluate(statement.expression)

    def visit_return_stmt(self, statement: stmt.Return) -> None:
        value = None
        if statement.value is not None:
            value = self.evaluate(statement.value)
        
        raise LoxReturn(value)

    def visit_print_stmt(self, statement: stmt.Print) -> None:
        value = self.evaluate(statement.expression)
        print(str(value))

    def visit_function_stmt(self, statement: stmt.Function) -> None:
        function = LoxFunction(statement, self.environment, False)
        self.environment.define(statement.name.lexeme, function)

    def visit_assert_stmt(self, statement: stmt.Assert) -> None:
        value = self.evaluate(statement.expression)
        if not self.is_truthy(value):
            raise LoxAssertionError(statement.assert_token.line, "Assertion Error")

    def visit_while_stmt(self, statement: stmt.While) -> None:
        while self.is_truthy(self.evaluate(statement.condition)):
            self.execute(statement.body)

    def visit_var_stmt(self, statement: stmt.Var) -> None:
        value = None
        if statement.initializer is not None:
            value = self.evaluate(statement.initializer)
        
        self.environment.define(statement.name.lexeme, value)

    def visit_variable_expr(self, expression: expr.Variable) -> LoxObject:
        return self.look_up_variable(expression.name, expression)

    def visit_get_expr(self, expression: expr.Get) -> object:
        obj = self.evaluate(expression.object)
        if isinstance(obj, LoxInstance):
            return obj.get_attr(expression.name)
        raise LoxRuntimeError(expression.name, "Only class instances have properties.")

    def visit_set_expr(self, expression: expr.Set) -> object:
        obj = self.evaluate(expression.object)
        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expression.name, "Only instances have fields.")
        value = self.evaluate(expression.value)
        obj.set_attr(expression.name, value)
        return value

    def visit_this_expr(self, expression: expr.This) -> object:
        return self.look_up_variable(expression.keyword, expression)

    def look_up_variable(self, name: Token, expression: expr.Expr) -> LoxObject:
        distance = self.locals.get(expression, None)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        return self.globals.get(name)

    def visit_block_stmt(self, stmt: stmt.Block) -> None:
        self.execute_block(stmt.statements, Environment(enclosing=self.environment))

    def execute_block(self, statements: List[stmt.Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def visit_assign_expr(self, expression: expr.Assign):
        value = self.evaluate(expression.value)


        distance = self.locals.get(expression)
        if distance is not None:
            self.environment.assign_at(distance, expression.name, value)
        else:
            self.globals.assign(expression.name, value)

        return value

    def visit_class_stmt(self, statement: stmt.Class) -> None:
        superclass = None
        if statement.superclass is not None:
            superclass = self.evaluate(statement.superclass)
            if not isinstance(superclass, LoxClass):
                raise LoxRuntimeError(statement.superclass.name, "Superclass must be a class.")

        self.environment.define(statement.name.lexeme, None)

        if statement.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)

        methods = {}
        for method in statement.methods:
            function = LoxFunction(method, self.environment, method.name.lexeme == "init")
            methods[method.name.lexeme] = function
        
        klass = LoxClass(statement.name.lexeme, superclass, methods)
        
        if superclass is not None:
            self.environment = self.environment.enclosing

        self.environment.assign(statement.name, klass)

    def visit_super_expr(self, expression: expr.Super) -> None:
        distance = self.locals.get(expression)
        superclass = self.environment.get_at(distance, "super")

        # bind uses of 'super' to the defining class's superclass
        parent_object = self.environment.get_at(distance-1, "this")
        method = superclass.find_method(expression.method.lexeme)
        
        if method is None:
            raise LoxRuntimeError(expression.method, f"Undefined property '{expr.method.lexeme}'.")
        
        return method.bind(parent_object)

    def visit_call_expr(self, expression: expr.Call):
        callee = self.evaluate(expression.callee)
        arguments = []
        for argument in expression.arguments:
            arguments.append(self.evaluate(argument))

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expression.paren, "Can only call functions and classes.")

        function = callee

        if len(arguments) != function.arity():
            raise LoxRuntimeError(expression.paren, f"Expected {function.arity()} arguments but got { len(arguments) }.")

        return function.call(self, arguments)


    def evaluate(self, expr) -> LoxObject:
        return expr.accept(self)

    @staticmethod
    def check_number_operands(
        operator: TokenType, left: LoxObject, right: LoxObject
    ) -> None:
        if type(left) == type(right) == float:
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    @staticmethod
    def check_number_operand(operator: TokenType, operand: LoxObject) -> None:
        if type(operand) == float:
            return
        raise LoxRuntimeError(operator, "Operand must be a numbers.")

    @staticmethod
    def is_truthy(value: LoxObject):
        if value is None:
            return False
        if type(value) == bool:
            return value
        return True

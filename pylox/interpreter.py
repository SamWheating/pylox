from pylox.types import LoxObject
from pylox.exceptions import LoxRuntimeError, LoxAssertionError, LoxReturn
from pylox.token_type import TokenType
from pylox.environment import Environment
from pylox.lox_callable import LoxCallable
from pylox.lox_function import LoxFunction

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
        function = LoxFunction(statement)
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

    def visit_variable_expr(self, expression: expr.Variable):
        return self.environment.get(expression.name)

    def visit_block_stmt(self, stmt: stmt.Block) -> None:
        self.execute_block(stmt.statements, Environment(enclosing=self.environment))

    def execute_block(self, statements: List[stmt.Stmt], environment: Environment):
        self.environment = environment
        try:
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = self.environment.enclosing

    def visit_assign_expr(self, expr: expr.Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

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

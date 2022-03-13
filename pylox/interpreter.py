from pylox.types import LoxObject
from pylox.exceptions import LoxRuntimeError
from pylox.token_type import TokenType
from pylox.environment import Environment

from pylox import expr
from pylox import stmt

from typing import List


class Interpreter(expr.Visitor, stmt.Visitor):
    def __init__(self, runtime):
        self.runtime = runtime
        self.environment = Environment()

    def interpret(self, statements: List[stmt.Stmt]) -> None:
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            self.runtime.runtime_error(e)

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

    def visit_print_stmt(self, statement: stmt.Print) -> None:
        value = self.evaluate(statement.expression)
        print(str(value))

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
        previous_env = self.environment
        self.environment = environment
        try:
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.environment = previous_env

    def visit_assign_expr(self, expr: expr.Assign):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value

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

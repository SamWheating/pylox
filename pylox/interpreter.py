from pylox.expr import Visitor, Expr
from pylox.types import LoxObject
from pylox.exceptions import LoxRuntimeError
from pylox.token_type import TokenType


class Interpreter(Visitor):
    def __init__(self, runtime):
        self.runtime = runtime

    def interpret(self, expression: Expr) -> None:
        try:
            value = self.evaluate(expression)
            return value
        except LoxRuntimeError as e:
            self.runtime.runtime_error(e)

    def visit_literal_expr(self, expr) -> LoxObject:
        return expr.value

    def visit_grouping_expr(self, expr) -> LoxObject:
        return self.evaluate(expr.expression)

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

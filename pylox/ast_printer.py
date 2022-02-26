# This is just a sample usage of the Visitor pattern for Expressions

from pylox.expr import Visitor, Expr, Binary, Grouping, Literal, Unary
from pylox.token import Token
from pylox.token_type import TokenType


class ASTPrinter(Visitor):
    def print(self, expr: Expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs):

        string = "("
        string += name
        for expr in exprs:
            string += " "
            string += expr.accept(self)

        string += ")"
        return string


if __name__ == "__main__":

    expression = Binary(
        Unary(Token(TokenType.MINUS, "-", None, 1), Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(Literal(45.67)),
    )

    printer = ASTPrinter()

    print(printer.print(expression))

import unittest
from pylox.interpreter import Interpreter
from pylox.token_type import TokenType
from pylox.token import Token
from pylox.lox import Lox
import pylox.expr as expr

class TestInterpreter(unittest.TestCase):

    def setUp(self):
        self.runtime = Lox()
        self.interpreter = Interpreter(runtime=self.runtime)

    def test_interpreter_binary_expression(self):

        expression = expr.Binary(
            expr.Unary(Token(TokenType.MINUS, "-", None, 1), expr.Literal(123.0)),
            Token(TokenType.STAR, "*", None, 1),
            expr.Grouping(expr.Literal(45.67)),
        )

        result = self.interpreter.interpret(expression)
        
        assert result == -5617.41

    def test_interpreter_throws_runtime_error(self):

        expression = expr.Binary(
            expr.Literal(123.0),
            Token(TokenType.PLUS, "+", None, 1),
            expr.Literal("A String"),
        )

        result = self.interpreter.interpret(expression)
        
        assert result is None
        assert self.runtime.had_runtime_error
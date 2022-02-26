import unittest
from pylox.parser import Parser
from pylox.token_type import TokenType
from pylox.token import Token
from pylox.lox import Lox
import pylox.expr as expr

# TODO: Move this to a setup method or fixture or something
RUNTIME=Lox()

class TestParser(unittest.TestCase):

    def test_simple_binary_expression_parsing(self):

        tokens = [
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "15", 15.0, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        parser = Parser(tokens, RUNTIME)
        result = parser.parse()

        assert type(result) == expr.Binary
        assert result.operator.type == TokenType.PLUS
        assert result.left.value == 12.0
        assert result.right.value == 15.0

    def test_unary_parsing(self):

        tokens = [
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        parser = Parser(tokens, RUNTIME)
        result = parser.parse()

        assert type(result) == expr.Unary
        assert result.operator.type == TokenType.MINUS
        assert result.right.value == 12.0

    def test_multiple_unary_parsing(self):

        tokens = [
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        parser = Parser(tokens, RUNTIME)
        result = parser.parse()

        assert type(result) == expr.Unary
        assert result.operator.type == TokenType.MINUS
        assert type(result.right) == expr.Unary
        assert result.right.operator.type == TokenType.MINUS
        assert type(result.right.right) == expr.Unary
        assert result.right.right.operator.type == TokenType.MINUS
import unittest
from pylox.parser import Parser
from pylox.token_type import TokenType
from pylox.token import Token
from pylox.lox import Lox
import pylox.expr as expr

class TestParser(unittest.TestCase):

    def setUp(self):
        self.runtime = Lox()
        self.parser = Parser(tokens=[], runtime=self.runtime)

    def test_simple_binary_expression_parsing(self):

        self.parser.tokens = [
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "15", 15.0, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        result = self.parser.parse()

        assert type(result) == expr.Binary
        assert result.operator.type == TokenType.PLUS
        assert result.left.value == 12.0
        assert result.right.value == 15.0

    def test_unary_parsing(self):

        self.parser.tokens = [
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        result = self.parser.parse()

        assert type(result) == expr.Unary
        assert result.operator.type == TokenType.MINUS
        assert result.right.value == 12.0

    def test_multiple_unary_parsing(self):

        self.parser.tokens = [
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        result = self.parser.parse()

        assert type(result) == expr.Unary
        assert result.operator.type == TokenType.MINUS
        assert type(result.right) == expr.Unary
        assert result.right.operator.type == TokenType.MINUS
        assert type(result.right.right) == expr.Unary
        assert result.right.right.operator.type == TokenType.MINUS

    def test_parser_error_handling(self):

        self.parser.tokens = [
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.STAR, "*", None, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        result = self.parser.parse()
        
        assert result is None
        assert self.runtime.had_error


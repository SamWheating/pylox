import unittest
from pylox.parser import Parser
from pylox.token_type import TokenType
from pylox.token import Token
from pylox.lox import Lox
import pylox.expr as expr
import pylox.stmt as stmt

class TestParser(unittest.TestCase):

    def setUp(self):
        self.runtime = Lox()
        self.parser = Parser(tokens=[], runtime=self.runtime)

    def test_simple_binary_expression_parsing(self):

        self.parser.tokens = [
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "15", 15.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        result = self.parser.parse()[0]

        assert type(result) == stmt.Expression
        assert result.expression.operator.type == TokenType.PLUS
        assert result.expression.left.value == 12.0
        assert result.expression.right.value == 15.0

    def test_unary_parsing(self):

        self.parser.tokens = [
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        result = self.parser.parse()[0]

        assert type(result.expression) == expr.Unary
        assert result.expression.operator.type == TokenType.MINUS
        assert result.expression.right.value == 12.0

    def test_multiple_unary_parsing(self):

        self.parser.tokens = [
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.MINUS, "-", None, 1),
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.SEMICOLON, ";", None, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        result = self.parser.parse()[0]

        assert type(result.expression) == expr.Unary
        assert result.expression.operator.type == TokenType.MINUS
        assert type(result.expression.right) == expr.Unary
        assert result.expression.right.operator.type == TokenType.MINUS
        assert type(result.expression.right.right) == expr.Unary
        assert result.expression.right.right.operator.type == TokenType.MINUS

    def test_parser_error_handling(self):

        self.parser.tokens = [
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.STAR, "*", None, 1),
            Token(TokenType.PLUS, "+", None, 1),
            Token(TokenType.NUMBER, "12", 12.0, 1),
            Token(TokenType.EOF, "", None, 1)
        ]

        result = self.parser.parse()[0]
        
        assert result is None
        assert self.runtime.had_error


import unittest
from pylox.scanner import Scanner
from pylox.token_type import TokenType
from pylox.lox import Lox

class TestScanner(unittest.TestCase):

    def setUp(self):
        self.runtime = Lox()
        self.scanner = Scanner("", runtime=self.runtime)

    def test_scanner_simple_lexemes(self):

        self.scanner.source = "()"
        tokens = self.scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN, TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_two_character_lexemes(self):

        self.scanner.source = "!="
        tokens = self.scanner.scan_tokens()

        assert len(tokens) == 2

        expected = [TokenType.BANG_EQUAL, TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_spaces(self):

        self.scanner.source = "!= >="
        tokens = self.scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.BANG_EQUAL, TokenType.GREATER_EQUAL, TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_strings(self):

        self.scanner.source = '"This is a String"'
        tokens = self.scanner.scan_tokens()

        assert len(tokens) == 2

        expected = [TokenType.STRING, TokenType.EOF]
        assert [t.type for t in tokens] == expected

        expected_values = ["This is a String", None]
        assert [t.literal for t in tokens] == expected_values

    def test_scanner_numbers(self):

        self.scanner.source = "13 19.1"
        tokens = self.scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.NUMBER, TokenType.NUMBER, TokenType.EOF]
        assert [t.type for t in tokens] == expected

        expected_values = [13.0, 19.1, None]
        assert [t.literal for t in tokens] == expected_values

    def test_scanner_comments(self):

        self.scanner.source = "// This is just a big comment"
        tokens = self.scanner.scan_tokens()

        assert len(tokens) == 1

        expected = [TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_reserved_words(self):

        self.scanner.source = "if true"
        tokens = self.scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.IF, TokenType.TRUE, TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_identifiers(self):

        self.scanner.source = "my_identifier beep boop"
        tokens = self.scanner.scan_tokens()

        assert len(tokens) == 4

        expected = [TokenType.IDENTIFIER, TokenType.IDENTIFIER, TokenType.IDENTIFIER, TokenType.EOF]
        assert [t.type for t in tokens] == expected

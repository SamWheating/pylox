import unittest
from pylox.scanner import Scanner
from pylox.token_type import TokenType


class TestScanner(unittest.TestCase):
    def test_scanner_simple_lexemes(self):

        scanner = Scanner("()")
        tokens = scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.LEFT_PAREN, TokenType.RIGHT_PAREN, TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_two_character_lexemes(self):

        scanner = Scanner("!=")
        tokens = scanner.scan_tokens()

        assert len(tokens) == 2

        expected = [TokenType.BANG_EQUAL, TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_spaces(self):

        scanner = Scanner("!= >=")
        tokens = scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.BANG_EQUAL, TokenType.GREATER_EQUAL, TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_strings(self):

        scanner = Scanner('"This is a String"')
        tokens = scanner.scan_tokens()

        assert len(tokens) == 2

        expected = [TokenType.STRING, TokenType.EOF]
        assert [t.type for t in tokens] == expected

        expected_values = ["This is a String", None]
        assert [t.literal for t in tokens] == expected_values

    def test_scanner_numbers(self):

        scanner = Scanner("13 19.1")
        tokens = scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.NUMBER, TokenType.NUMBER, TokenType.EOF]
        assert [t.type for t in tokens] == expected

        expected_values = [13.0, 19.1, None]
        assert [t.literal for t in tokens] == expected_values

    def test_scanner_comments(self):

        scanner = Scanner("// This is just a big comment")
        tokens = scanner.scan_tokens()

        assert len(tokens) == 1

        expected = [TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_reserved_words(self):

        scanner = Scanner("if true")
        tokens = scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.IF, TokenType.TRUE, TokenType.EOF]
        assert [t.type for t in tokens] == expected

    def test_scanner_identifiers(self):

        scanner = Scanner("if true")
        tokens = scanner.scan_tokens()

        assert len(tokens) == 3

        expected = [TokenType.IF, TokenType.TRUE, TokenType.EOF]
        assert [t.type for t in tokens] == expected

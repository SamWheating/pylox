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

    

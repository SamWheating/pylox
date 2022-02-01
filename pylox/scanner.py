from pylox.token_type import TokenType
from pylox.token import Token

from typing import List, Union


class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def scan_tokens(self) -> List[TokenType]:

        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        match c:
            case "(":
                self.add_token(TokenType.LEFT_PAREN)
            case ")":
                self.add_token(TokenType.RIGHT_PAREN)
            case "{":
                self.add_token(TokenType.LEFT_BRACE)
            case "{":
                self.add_token(TokenType.RIGHT_BRACE)
            case ",":
                self.add_token(TokenType.COMMA)
            case ".":
                self.add_token(TokenType.DOT)
            case "-":
                self.add_token(TokenType.MINUS)
            case "+":
                self.add_token(TokenType.PLUS)
            case ";":
                self.add_token(TokenType.SEMICOLON)
            case "*":
                self.add_token(TokenType.STAR)

            case "!":
                self.add_token(TokenType.BANG_EQUAL) if self.match(
                    "="
                ) else self.add_token(TokenType.BANG)
            case "=":
                self.add_token(TokenType.EQUAL_EQUAL) if self.match(
                    "="
                ) else self.add_token(TokenType.EQUAL)
            case "<":
                self.add_token(TokenType.LESS_EQUAL) if self.match(
                    "="
                ) else self.add_token(TokenType.LESS)
            case ">":
                self.add_token(TokenType.GREATER_EQUAL) if self.match(
                    "="
                ) else self.add_token(TokenType.GREATER)

            case " " | "\t" | "\r":
                pass

            case _:
                print(self.line, "Unexpected Character.")

    def match(self, expected):

        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def add_token(
        self, type: TokenType, literal: Union[float, str, None] = None
    ) -> None:
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

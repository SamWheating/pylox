from token_type import TokenType
from typing import Union


class Token:
    def __init__(
        self, token_type: TokenType, lexeme: str, literal: Union[str, float, None], line: int
    ):
        self.type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"

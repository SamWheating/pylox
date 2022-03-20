from pylox.token import Token
from pylox.types import LoxObject


class ParseError(Exception):
    pass

class LoxAssertionError(Exception):
    def __init__(self, line: int, message: str):
        super().__init__(message)
        self.line = line

class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token

class LoxReturn(Exception):
    def __init__(self, value: LoxObject):
        super().__init__()
        self.value = value

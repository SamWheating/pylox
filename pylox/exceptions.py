from pylox.token import Token


class ParseError(Exception):
    pass


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        super().__init__(message)
        self.token = token

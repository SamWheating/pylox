from pylox.token import Token
from pylox.exceptions import LoxRuntimeError

class LoxInstance:

    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def __str__(self) -> str:
        return self.klass.name + " instance"

    def get_attr(self, name: Token) -> object:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise LoxRuntimeError(name, f"Undefined property {name.lexeme}.")

    def set_attr(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value

from pylox.types import LoxObject
from pylox.token import Token
from pylox.exceptions import LoxRuntimeError

class Environment:

    # TODO: whats the correct type hint for `enclosing`? (See PEP 673)
    def __init__(self, enclosing=None) -> None:
        self.enclosing = enclosing
        self.values = {}

    def define(self, name: str, value: LoxObject) -> None:
        self.values[name] = value

    def get(self, name: Token) -> LoxObject:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        # recursively check all of the parent environments for this value
        if self.enclosing is not None:
            return self.enclosing.get(name)
        
        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")

    def assign(self, name: Token, value: LoxObject) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return

        if self.enclosing is not None:
            self.enclosing.assign(name, value)

        raise LoxRuntimeError(name, f"Undefined variable {name.lexeme}.")

from pylox.lox_callable import LoxCallable
from pylox.types import LoxObject
from pylox import stmt
from typing import List
from pylox.environment import Environment

class LoxFunction(LoxCallable):

    def __init__(self, declaration: stmt.Function) -> LoxObject:
        self.declaration = declaration

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter, arguments: List[LoxObject]):
        environment = Environment(interpreter.globals)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        interpreter.execute_block(self.declaration.body, environment)
        return None

    def __str__(self):
        return f"< fn {declaration.name.lexeme} >"

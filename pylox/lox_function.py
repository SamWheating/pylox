from pylox.lox_callable import LoxCallable
from pylox.types import LoxObject
from pylox.exceptions import LoxReturn
from pylox import stmt
from typing import List
from pylox.environment import Environment

class LoxFunction(LoxCallable):

    def __init__(self, declaration: stmt.Function, closure: Environment) -> LoxObject:
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter, arguments: List[LoxObject]):
        environment = Environment(self.closure)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except LoxReturn as lr:
            return lr.value
        return None

    def __str__(self):
        return f"< fn {declaration.name.lexeme} >"

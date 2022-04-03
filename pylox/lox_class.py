from pylox.lox_callable import LoxCallable
from pylox.lox_function import LoxFunction
from pylox.types import LoxObject
from pylox.lox_instance import LoxInstance

from typing import List

class LoxClass(LoxCallable):

    def __init__(self, name: str, methods: dict[str, LoxFunction]):
        self.name = name
        self.methods = methods

    def __str__(self) -> str:
        return self.name

    def call(self, interpreter, arguments: List[LoxObject]):
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def find_method(self, name: str) -> LoxFunction:
        if name in self.methods:
            return self.methods[name]

    def arity(self) -> int:
        initializer = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

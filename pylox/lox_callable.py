from abc import ABC
from pylox.types import LoxObject
from typing import List

class LoxCallable(ABC):

    def arity(self):
        raise NotImplementedError

    def call(self, interpreter, arguments: List[LoxObject]):
        raise NotImplementedError
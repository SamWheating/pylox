# this file generated by tool/generate_ast.py
from abc import ABC

class Visitor(ABC):

    def visit_expression_stmt(self, expr):
        raise NotImplementedError()

    def visit_if_stmt(self, expr):
        raise NotImplementedError()

    def visit_print_stmt(self, expr):
        raise NotImplementedError()

    def visit_var_stmt(self, expr):
        raise NotImplementedError()

    def visit_block_stmt(self, expr):
        raise NotImplementedError()

    def visit_while_stmt(self, expr):
        raise NotImplementedError()

    def visit_assert_stmt(self, expr):
        raise NotImplementedError()

class Stmt(ABC):

    def accept(visitor: Visitor):
        pass

class Expression(Stmt):

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visit_expression_stmt(self)


class If(Stmt):

    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def accept(self, visitor: Visitor):
        return visitor.visit_if_stmt(self)


class Print(Stmt):

    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visit_print_stmt(self)


class Var(Stmt):

    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: Visitor):
        return visitor.visit_var_stmt(self)


class Block(Stmt):

    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor: Visitor):
        return visitor.visit_block_stmt(self)


class While(Stmt):

    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def accept(self, visitor: Visitor):
        return visitor.visit_while_stmt(self)


class Assert(Stmt):

    def __init__(self, assert_token, expression):
        self.assert_token = assert_token
        self.expression = expression

    def accept(self, visitor: Visitor):
        return visitor.visit_assert_stmt(self)



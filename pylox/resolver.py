from pylox import expr, stmt
from pylox.token import Token
from enum import Enum, auto

from typing import Union, List

class FunctionType(Enum):

    NONE = auto()
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()

class ClassType(Enum):

    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()

class Resolver(expr.Visitor, stmt.Visitor):

    def __init__(self, interpreter, runtime):
        self.interpreter = interpreter
        self.runtime = runtime
        self.scopes = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE

    def visit_block_stmt(self, statement: stmt.Block) -> None:
        self.begin_scope()
        self.resolve(statement.statements)
        self.end_scope()
    
    # Since python doesn't have function overloading we have to merge a few jlox 
    # functions into one here. TODO: Clean this up and improve readability
    def resolve(self, expression: Union[stmt.Stmt, expr.Expr, List[stmt.Stmt]]) -> None:

        if isinstance(expression, List):
            for statement in expression:
                self.resolve(statement)

        else:
            expression.accept(self)
        
    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def visit_var_stmt(self, statement: stmt.Var):
        self.declare(statement.name)
        if statement.initializer is not None:
            self.resolve(statement.initializer)
        self.define(statement.name)

    def visit_variable_expr(self, expression: expr.Variable):
        if self.scopes and self.scopes[-1].get(expression.name.lexeme, None) == False:
            self.runtime.error(expression.name.line, "Can't read local variable in its own initializer.")

        self.resolve_local(expression, expression.name)

    def resolve_local(self, expression: expr.Expr, name: Token) -> None:
        for i in range(len(self.scopes)-1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expression, len(self.scopes)-1-i)
                return

    def visit_assign_expr(self, expression: expr.Assign) -> None:
        self.resolve(expression.value)
        self.resolve_local(expression, expression.name)

    def visit_function_stmt(self, statement: stmt.Function) -> None:
        self.declare(statement.name)
        self.define(statement.name)
        self.resolve_function(statement, FunctionType.FUNCTION)

    def resolve_function(self, function: stmt.Function, function_type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = function_type
        
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()
        self.current_function = enclosing_function

    def visit_expression_stmt(self, statement: stmt.Expression) -> None:
        self.resolve(statement.expression)

    def visit_if_stmt(self, statement: stmt.If) -> None:
        self.resolve(statement.condition)
        self.resolve(statement.then_branch)
        if statement.else_branch is not None:
            self.resolve(statement.else_branch)

    def visit_print_stmt(self, statement: stmt.Print) -> None:
        self.resolve(statement.expression)

    def visit_assert_stmt(self, statement: stmt.Assert) -> None:
        self.resolve(statement.expression)

    def visit_return_stmt(self, statement: stmt.Return) -> None:
        if self.current_function == FunctionType.NONE:
            self.runtime.error(statement.keyword.line, "Can't return from top-level code.")
        
        if statement.value is not None:
            if self.current_function == FunctionType.INITIALIZER:
                self.runtime.error(statement.keyword.line, "Can't return a value from an initialzier.")
            self.resolve(statement.value)

    def visit_class_stmt(self, statement: stmt.Class) -> None:
        enclosing_class = self.current_class
        self.current_class = ClassType.CLASS
        
        self.declare(statement.name)
        self.define(statement.name)

        if statement.superclass is not None:
            self.current_class = ClassType.SUBCLASS
            if statement.name.lexeme == statement.superclass.name.lexeme:
                self.runtime.error(statement.superclass.name, "A class can't inherit from itself")
            self.resolve(statement.superclass)

        if statement.superclass is not None:
            self.begin_scope()
            self.scopes[-1]["super"] = True

        self.begin_scope()
        self.scopes[-1]["this"] = True

        for method in statement.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            self.resolve_function(method, declaration)

        if statement.superclass is not None:
            self.end_scope()

        self.end_scope()
        self.current_class = enclosing_class

    def visit_super_expr(self, expression: expr.Super) -> None:
        if self.current_class == ClassType.NONE:
            self.runtime.error(expression.keyword, "Can't use 'super' outside of a class.")
        elif self.current_class != ClassType.SUBCLASS:
            self.runtime.error(expression.keyword, "Can't use 'super' in a class with no superclass.")

        self.resolve_local(expression, expression.keyword)

    def visit_get_expr(self, expression: expr.Get) -> None:
        self.resolve(expression.object)

    def visit_set_expr(self, expression: expr.Set) -> None:
        self.resolve(expression.value)
        self.resolve(expression.object)

    def visit_this_expr(self, expression: expr.This) -> None:
        
        if self.current_class != ClassType.CLASS:
            self.runtime.error(expression.keyword.line, "Can't use 'this' outside of a class.")
            return
        
        self.resolve_local(expression, expression.keyword)

    def visit_while_stmt(self, statement: stmt.While) -> None:
        self.resolve(statement.condition)
        self.resolve(statement.body)

    def visit_binary_expr(self, expression: expr.Binary) -> None:
        self.resolve(expression.left)
        self.resolve(expression.right)

    def visit_call_expr(self, expression: expr.Call) -> None:
        self.resolve(expression.callee)

        for argument in expression.arguments:
            self.resolve(argument)

    def visit_grouping_expr(self, expression: expr.Grouping) -> None:
        self.resolve(expression.expression)

    def visit_literal_expr(self, expression: expr.Literal) -> None:
        pass

    def visit_logical_expr(self, expression: expr.Logical) -> None:
        self.resolve(expression.left)
        self.resolve(expression.right)

    def visit_unary_expr(self, expression: expr.Unary) -> None:
        self.resolve(expr.right)

    def declare(self, name: Token) -> None:
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            self.runtime.error(name.line, f"Already declared variable {name.lexeme} in this scope.")
        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    

    



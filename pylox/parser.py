from pylox.token_type import TokenType, KEYWORDS
from pylox.token import Token
from pylox.exceptions import ParseError
from typing import List

from pylox import stmt
from pylox import expr

class Parser:
    def __init__(self, tokens, runtime):
        self.tokens = tokens
        self.current = 0
        self.runtime = runtime

    def parse(self) -> List[stmt.Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self) -> stmt.Stmt:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def expression(self) -> expr.Expr:
        return self.assignment()

    def assignment(self) -> expr.Expr:
        expression = self.equality()

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
        
            if isinstance(expression, expr.Variable):
                name = expression.name
                return expr.Assign(name, value)

            self.error(equals, "Invalid assignment target")
        
        return expression

    def equality(self) -> expr.Expr:
        expression = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expression = expr.Binary(expression, operator, right)

        return expression

    def statement(self) -> stmt.Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return stmt.Block(self.block())
        return self.expression_statement()

    def block(self) -> List[stmt.Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def print_statement(self) -> stmt.Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)

    def expression_statement(self) -> stmt.Stmt:
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(expression)

    def var_declaration(self) -> stmt.Var:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)

    def comparison(self) -> expr.Expr:

        expression = self.term()
        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expression = expr.Binary(expression, operator, right)
        return expression

    def match(self, *types) -> bool:

        for t in types:
            if self.check(t):
                self.advance()
                return True

        return False

    def term(self):

        expression = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expression = expr.Binary(expression, operator, right)

        return expression

    def factor(self):

        expression = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expression = expr.Binary(expression, operator, right)

        return expression

    def unary(self):

        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator, right)

        return self.primary()

    def primary(self) -> Token:

        if self.match(TokenType.FALSE):
            return expr.Literal(False)
        if self.match(TokenType.TRUE):
            return expr.Literal(True)
        if self.match(TokenType.NIL):
            return expr.Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expr.Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return expr.Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expression = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(expression)

        raise self.error(self.peek(), "Expect expression.")

    def check(self, t: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == t

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def consume(self, t: TokenType, message: str) -> Token:

        if self.check(t):
            return self.advance()

        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            self.runtime.report(token.line, "at end", message)
        else:
            self.runtime.report(token.line, f"at {token.lexeme}", message)
        return ParseError()

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in KEYWORDS:
                return

            self.advance()

from pylox.token_type import TokenType, KEYWORDS
from pylox.token import Token
from pylox.expr import Binary, Expr, Unary, Literal, Grouping
from pylox.exceptions import ParseError

class Parser():

    def __init__(self, tokens, runtime):
        self.tokens = tokens
        self.current = 0
        self.runtime = runtime

    def parse(self):
        try:
            return self.expression()
        except ParseError:
            return None

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self) -> Expr:

        expr = self.term()
        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def match(self, *types) -> bool:

        for t in types:
            if self.check(t):
                self.advance()
                return True

        return False

    def term(self):

        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr

    def factor(self):

        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        
        return expr

    def unary(self):

        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.primary()

    def primary(self) -> Token:

        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NIL): return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        raise self.error(self.peek(), "Expect expression.")

    def check(self, t: Token) -> bool:
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
            if self.previous().type == token.SEMICOLON:
                return
            if self.peek.type() in KEYWORDS:
                return
            
            self.advance()

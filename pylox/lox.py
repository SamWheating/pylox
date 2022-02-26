import sys

from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.interpreter import Interpreter
from pylox.ast_printer import ASTPrinter
from pylox.exceptions import LoxRuntimeError


class Lox:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter(self)

    def run_file(self, file_name: str):

        with open(file_name) as ifp:
            text = ifp.read()

        self.run(text)

        if self.had_error:
            sys.exit(65)
        if self.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):

        while True:
            line = input("> ")
            if line is None:
                break
            self.run(line)
            self.had_error = False

    def run(self, source: str):
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self)
        expression = parser.parse()

        if self.had_error:
            return

        # print(ASTPrinter().print(expression))
        self.interpreter.interpret(expression)

    def error(self, line: int, message: str):
        self.report(line, "", message)

    def runtime_error(self, error: LoxRuntimeError):
        print(str(error))
        print(f"[line: {error.token.line}]")
        self.had_runtime_error = True

    def report(self, line: int, where: str, message: str):
        print(f"[line: {line}] Error {where}: {message}")
        self.had_error = True


def main():

    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)

    lox = Lox()

    if len(sys.argv) == 2:
        lox.run_file(sys.argv[1])

    else:
        lox.run_prompt()

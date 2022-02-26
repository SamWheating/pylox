import sys

from pylox.scanner import Scanner
from pylox.parser import Parser
from pylox.ast_printer import ASTPrinter


class Lox:
    def __init__(self):
        self.hadError = False

    def run_file(self, file_name: str):

        with open(file_name) as ifp:
            text = ifp.read()

        self.run(text)

        if self.hadError():
            sys.exit(65)

    def run_prompt(self):

        while True:
            line = input("> ")
            if line is None:
                break
            self.run(line)
            self.hadError = False

    def run(self, source: str):
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()
        print([t.type for t in tokens])
        parser = Parser(tokens, self)
        expression = parser.parse()

        if self.hadError:
            return
    
        print(ASTPrinter().print(expression))



    def error(self, line: int, message: str):
        self.report(line, "", message)

    def report(self, line: int, where: str, message: str):
        print(f"[line: {line}] Error {where}: {message}")
        self.hadError = True


def main():

    if len(sys.argv) > 2:
        print("Usage: pylox [script]")
        sys.exit(64)

    lox = Lox()

    if len(sys.argv) == 2:
        lox.run_file(sys.argv[1])

    else:
        lox.run_prompt()

import sys
from typing import List


def define_ast(output_dir: str, base_name: str, types: List[str]):

    path = output_dir + "/" + base_name.lower() + ".py"
    contents = ""

    # Add top-level file contents
    contents += "# this file generated by tool/generate_ast.py\n"
    contents += "from abc import ABC\n\n"

    contents += define_visitor(base_name, types)

    contents += f"class {base_name}(ABC):\n\n"
    contents += "    def accept(visitor: Visitor):\n"
    contents += "        pass\n\n"

    for t in types:
        class_name = t.split(":")[0].strip()
        fields = t.split(":")[1].strip()
        contents += define_type(base_name, class_name, fields)
        contents += "\n\n"

    with open(path, "w+") as ofp:
        ofp.write(contents)


def define_visitor(base_name, types):

    visitor_contents = "class Visitor(ABC):\n\n"
    for t in types:

        class_name = t.split(":")[0].strip()
        fields = t.split(":")[1].strip()

        visitor_contents += (
            f"    def visit_{class_name.lower()}_{base_name.lower()}(self, expr):\n"
        )
        visitor_contents += "        pass\n\n"

    return visitor_contents


def define_type(base_name, class_name, fields):

    class_contents = f"class {class_name}({base_name}):\n\n"

    # constructor
    class_contents += f"    def __init__(self, {fields}):\n"
    for field in fields.split(","):
        field_name = field.strip()
        class_contents += f"        self.{field_name} = {field_name}\n"

    class_contents += "\n    def accept(self, visitor: Visitor):\n"
    class_contents += (
        f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n"
    )
    return class_contents


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python generate_ast.py <output directory>")
        sys.exit(64)

    output_dir = sys.argv[1]

    # TODO: expand these lists to include proper type annotations
    define_ast(output_dir, "Expr", [
        "Binary   : left, operator, right",
        "Grouping : expression",
        "Literal  : value",
        "Variable : name",
        "Unary    : operator, right",
        "Assign   : name, value"
    ])

    define_ast(output_dir, "Stmt", [
        "Expression   : expression",
        "Print        : expression",
        "Var          : name, initializer"
    ])

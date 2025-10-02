import json
from pycparser import c_parser, c_ast

# -------------------------------
# VPL JSON IR Generator
# -------------------------------

class VPLIRGenerator(c_ast.NodeVisitor):
    def __init__(self):
        self.ir = {"functions": [], "variables": {}, "operations": []}
        self.current_function = None

    def visit_FuncDef(self, node):
        func_name = node.decl.name
        self.current_function = {
            "name": func_name,
            "params": [],
            "body": []
        }
        # Process parameters
        if isinstance(node.decl.type, c_ast.FuncDecl) and node.decl.type.args:
            for param in node.decl.type.args.params:
                if isinstance(param, c_ast.Decl):
                    self.current_function["params"].append(param.name)

        # Process function body
        self.visit(node.body)

        self.ir["functions"].append(self.current_function)
        self.current_function = None

    def visit_Compound(self, node):
        for stmt in node.block_items or []:
            self.visit(stmt)

    def visit_Assignment(self, node):
        target = self.get_name(node.lvalue)
        expr = self.get_expr(node.rvalue)
        op = {
            "type": "assignment",
            "target": target,
            "value": expr
        }
        self.ir["operations"].append(op)
        if self.current_function is not None:
            self.current_function["body"].append(op)

    def visit_If(self, node):
        cond = self.get_expr(node.cond)
        if_op = {"type": "if", "condition": cond, "then": [], "else": []}
        if node.iftrue:
            prev_ops = self.ir["operations"]
            self.ir["operations"] = []
            self.visit(node.iftrue)
            if_op["then"] = self.ir["operations"]
            self.ir["operations"] = prev_ops
        if node.iffalse:
            prev_ops = self.ir["operations"]
            self.ir["operations"] = []
            self.visit(node.iffalse)
            if_op["else"] = self.ir["operations"]
            self.ir["operations"] = prev_ops
        self.ir["operations"].append(if_op)
        if self.current_function is not None:
            self.current_function["body"].append(if_op)

    def visit_While(self, node):
        cond = self.get_expr(node.cond)
        while_op = {"type": "while", "condition": cond, "body": []}
        prev_ops = self.ir["operations"]
        self.ir["operations"] = []
        self.visit(node.stmt)
        while_op["body"] = self.ir["operations"]
        self.ir["operations"] = prev_ops
        self.ir["operations"].append(while_op)
        if self.current_function is not None:
            self.current_function["body"].append(while_op)

    def get_name(self, node):
        if isinstance(node, c_ast.ID):
            return node.name
        return str(node)

    def get_expr(self, node):
        if isinstance(node, c_ast.Constant):
            return {"type": "const", "value": node.value}
        elif isinstance(node, c_ast.ID):
            return {"type": "var", "name": node.name}
        elif isinstance(node, c_ast.BinaryOp):
            return {
                "type": "binop",
                "op": node.op,
                "left": self.get_expr(node.left),
                "right": self.get_expr(node.right)
            }
        elif isinstance(node, c_ast.UnaryOp):
            return {
                "type": "unary",
                "op": node.op,
                "expr": self.get_expr(node.expr)
            }
        elif isinstance(node, c_ast.FuncCall):
            return {
                "type": "call",
                "func": self.get_name(node.name),
                "args": [self.get_expr(arg) for arg in node.args.exprs] if node.args else []
            }
        return {"type": "unknown", "repr": str(node)}

# -------------------------------
# Example: Parse C code
# -------------------------------

c_code = r"""
int main() {
    int X;
    X = 0;
    while (X < 5) {
        X = X + 2;
    }
    return X;
}
"""

parser = c_parser.CParser()
ast = parser.parse(c_code)

# Generate IR
generator = VPLIRGenerator()
generator.visit(ast)

# Dump JSON IR
json_ir = json.dumps(generator.ir, indent=2)
print(json_ir)

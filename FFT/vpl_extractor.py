import json
from pycparser import c_parser, c_ast, parse_file

class VPLExtractor(c_ast.NodeVisitor):
    def __init__(self):
        self.ir = {"functions": []}

    def visit_FuncDef(self, node):
        func_name = node.decl.name
        #params = [p.name for p in node.decl.type.args.params]
        params = []
        body = []
        self._visit_block(node.body.block_items, body)
        self.ir["functions"].append({
            "name": func_name,
            "params": params,
            "body": body
        })

    def _visit_block(self, block_items, body):
        if block_items is None:
            return
        for stmt in block_items:
            self._visit_stmt(stmt, body)

    def _visit_stmt(self, stmt, body):
        if isinstance(stmt, c_ast.Decl):
            body.append({"decl": stmt.name})
        elif isinstance(stmt, c_ast.Assignment):
            body.append({
                "assign": {
                    "lvalue": self._expr(stmt.lvalue),
                    "rvalue": self._expr(stmt.rvalue)
                }
            })
        elif isinstance(stmt, c_ast.FuncCall):
            body.append({
                "call": {
                    "func": self._expr(stmt.name),
                    "args": [self._expr(arg) for arg in stmt.args.exprs]
                }
            })
        elif isinstance(stmt, c_ast.For):
            loop = {
                "for": {
                    "init": self._expr(stmt.init),
                    "cond": self._expr(stmt.cond),
                    "next": self._expr(stmt.next),
                    "body": []
                }
            }
            self._visit_block(stmt.stmt.block_items, loop["for"]["body"])
            body.append(loop)
        elif isinstance(stmt, c_ast.Compound):
            self._visit_block(stmt.block_items, body)
        else:
            body.append({"stmt": type(stmt).__name__})

    def _expr(self, expr):
        if expr is None:
            return None
        if isinstance(expr, c_ast.Constant):
            return {"const": expr.value}
        elif isinstance(expr, c_ast.ID):
            return {"id": expr.name}
        elif isinstance(expr, c_ast.BinaryOp):
            return {
                "binop": {
                    "op": expr.op,
                    "left": self._expr(expr.left),
                    "right": self._expr(expr.right)
                }
            }
        elif isinstance(expr, c_ast.FuncCall):
            return {
                "call": {
                    "func": self._expr(expr.name),
                    "args": [self._expr(arg) for arg in expr.args.exprs]
                }
            }
        elif isinstance(expr, c_ast.UnaryOp):
            return {"unop": {"op": expr.op, "expr": self._expr(expr.expr)}}
        elif isinstance(expr, c_ast.ID):
            return {"id": expr.name}
        elif isinstance(expr, c_ast.StructRef):
            return {
                "structref": {
                    "name": self._expr(expr.name),
                    "field": expr.field.name
                }
            }
        return {"expr": type(expr).__name__}

# ---------------------------
# Run extractor
# ---------------------------
if __name__ == "__main__":
    parser = c_parser.CParser()
    with open("fft_cooley_tukey.c", "r") as f:
        code = f.read()
    ast = parser.parse(code)

    extractor = VPLExtractor()
    extractor.visit(ast)

    print(json.dumps(extractor.ir, indent=2))

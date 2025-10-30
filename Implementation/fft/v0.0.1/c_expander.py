import json
import sys
import re

# -------- helpers --------

def substitute_index_vars(expr: str, index_map: dict, params: dict) -> str:
    """
    Replace loop indices and known parameters in expr with their numeric values.
    """
    if not expr:
        return expr

    # Replace loop indices
    for var, val in index_map.items():
        expr = re.sub(rf"\b{re.escape(var)}\b", str(val), expr)

    # Replace params (constants like N, N1, N2, half, etc.)
    for var, val in params.items():
        expr = re.sub(rf"\b{re.escape(var)}\b", str(val), expr)

    return expr


def expr_to_string(node) -> str:
    """
    Convert an IR expression node into a simple string.
    Handles ArrayRef, Id, Const, Call, BinOp, UnOp, StructRef etc.
    """
    if node is None:
        return ""

    if isinstance(node, str):
        return node

    if isinstance(node, dict):
        if "id" in node:
            return node["id"]
        if "const" in node:
            return str(node["const"])
        if "expr" in node:
            return expr_to_string(node["expr"])
        if "ArrayRef" in node.get("expr", ""):
            return "ArrayRef"
        if "call" in node:
            func = expr_to_string(node["call"]["func"])
            args = [expr_to_string(a) for a in node["call"].get("args", [])]
            return f"{func}({', '.join(args)})"
        if "binop" in node:
            left = expr_to_string(node["binop"]["left"])
            right = expr_to_string(node["binop"]["right"])
            op = node["binop"]["op"]
            return f"({left} {op} {right})"
        if "unop" in node:
            inner = expr_to_string(node["unop"]["expr"])
            op = node["unop"]["op"]
            return f"{inner}{op}"
        if "structref" in node:
            name = expr_to_string(node["structref"]["name"])
            field = node["structref"]["field"]
            return f"{name}.{field}"

    return str(node)


# -------- Expander --------

class Expander:
    def __init__(self, ir_json, params=None, assume_lengths=None):
        self.blocks = ir_json.get("blocks", [])
        self.connections = ir_json.get("connections", [])
        self.params = params or {}
        self.assume_lengths = assume_lengths or {}
        self.atomic_ops = []
        self.addr_list = []  # concrete addresses discovered
        self.addr_map = {}   # map addr string -> index

    def normalize_expr_string(self, node) -> str:
        s = expr_to_string(node) if not isinstance(node, str) else node
        return str(s) if s else ""

    def register_addresses_in_string(self, s: str):
        if not s:
            return
        matches = re.findall(r"[A-Za-z_][A-Za-z0-9_]*(\[[0-9]+\])+", s)
        for addr in matches:
            if addr not in self.addr_map:
                idx = len(self.addr_list)
                self.addr_list.append(addr)
                self.addr_map[addr] = idx

    # --- recursive block expander ---
    def expand_block(self, body, outer_index_map):
        for stmt in body:
            if "assign" in stmt:
                lhs = self.normalize_expr_string(stmt["assign"].get("lvalue"))
                rhs = self.normalize_expr_string(stmt["assign"].get("rvalue"))
                lhs_c = substitute_index_vars(lhs, outer_index_map, self.params)
                rhs_c = substitute_index_vars(rhs, outer_index_map, self.params)
                self.atomic_ops.append({
                    "type": "assign",
                    "lhs": lhs_c,
                    "rhs": rhs_c,
                    "loop_context": dict(outer_index_map)
                })
                self.register_addresses_in_string(lhs_c)
                self.register_addresses_in_string(rhs_c)

            elif "call" in stmt:
                call = stmt["call"]
                func = expr_to_string(call["func"])
                args_c = []
                for a in call.get("args", []):
                    arg_s = self.normalize_expr_string(a)
                    arg_c = substitute_index_vars(arg_s, outer_index_map, self.params)
                    args_c.append(arg_c)
                    self.register_addresses_in_string(arg_c)
                self.atomic_ops.append({
                    "type": "call",
                    "func": func,
                    "args": args_c,
                    "loop_context": dict(outer_index_map)
                })

            elif "for" in stmt:
                self.expand_for(stmt["for"], outer_index_map)

            else:
                self.atomic_ops.append({
                    "type": "raw",
                    "stmt": stmt,
                    "loop_context": dict(outer_index_map)
                })

    # --- expand a for loop (with recursion) ---
    def expand_for(self, for_node, outer_index_map=None):
        outer_index_map = outer_index_map or {}

        cond = for_node.get("cond")
        loop_var = None
        upper = None

        if cond and "binop" in cond:
            left = cond["binop"]["left"]
            right = cond["binop"]["right"]
            if "id" in left:
                loop_var = left["id"]

            if "id" in right:
                sym = right["id"]
                if sym in self.assume_lengths:
                    upper = int(self.assume_lengths[sym])
                elif sym in self.params:
                    upper = int(self.params[sym])
                else:
                    raise KeyError(f"Missing bound for '{sym}'")
            elif "const" in right:
                upper = int(right["const"])

        if loop_var is None or upper is None:
            raise ValueError(f"Bad for-loop header: {for_node}")

        body = for_node.get("body", [])
        for iv in range(upper):
            index_map = dict(outer_index_map)
            index_map[loop_var] = iv
            self.expand_block(body, index_map)

    def run(self):
        for blk in self.blocks:
            if blk["type"] == "raw_stmt" and "for" in blk["params"]:
                self.expand_for(blk["params"]["for"])
            elif blk["type"] == "raw_stmt" and "call" in blk["params"]:
                call = blk["params"]["call"]
                func = expr_to_string(call["func"])
                args_c = []
                for a in call.get("args", []):
                    arg_s = self.normalize_expr_string(a)
                    arg_c = substitute_index_vars(arg_s, {}, self.params)
                    args_c.append(arg_c)
                    self.register_addresses_in_string(arg_c)
                self.atomic_ops.append({"type": "call", "func": func, "args": args_c})
            elif blk["type"] == "var_decl":
                name = blk["params"].get("name")
                self.atomic_ops.append({"type": "var_decl", "name": name})
            elif blk["type"] == "expr":
                expr_s = self.normalize_expr_string(blk["params"].get("expr"))
                expr_c = substitute_index_vars(expr_s, {}, self.params)
                self.atomic_ops.append({"type": "expr", "expr": expr_c})
                self.register_addresses_in_string(expr_c)
            else:
                self.atomic_ops.append({"type": blk["type"], "params": blk.get("params", {})})

        return {
            "atomic_ops": self.atomic_ops,
            "addr_list": self.addr_list,
        }


# -------- CLI --------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python expander.py input.json [output.json]")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        ir_json = json.load(f)

    # Example parameters — adjust for your FFT test cases
    params = {"N": 4, "half": 2, "N1": 2, "N2": 2}
    assume_lengths = {"N": 4, "half": 2, "N1": 2, "N2": 2}

    expander = Expander(ir_json, params=params, assume_lengths=assume_lengths)
    result = expander.run()

    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            json.dump(result, f, indent=2)
    else:
        print(json.dumps(result, indent=2))


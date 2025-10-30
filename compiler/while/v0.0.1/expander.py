import json
import sys
import re

def load_translated(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def save_expanded(output_path, expanded):
    with open(output_path, 'w') as f:
        json.dump(expanded, f, indent=2)

def parse_expr(expr):
    """Extract variables used in an expression like 'x + 2'."""
    # crude parse for identifiers
    tokens = re.findall(r'[a-zA-Z_]\w*', expr)
    return tokens

def expand_blocks(translated):
    blocks = translated.get("blocks", [])
    connections = translated.get("connections", [])

    addr_list = []          # All variable names encountered
    M_global = []           # Control matrix rows
    c_global = []           # Constants or expressions
    atomic_ops = []         # Expanded low-level ops

    # Map each block ID to index for control matrix
    id_to_idx = {blk["id"]: idx for idx, blk in enumerate(blocks)}

    # Create initial variable space
    for blk in blocks:
        if blk["type"] == "init_var":
            varname = blk["params"]["name"]
            if varname not in addr_list:
                addr_list.append(varname)
            atomic_ops.append({
                "op": "init",
                "var": varname,
                "value": blk["params"]["init"]
            })

    # Now handle assign and while
    for blk in blocks:
        btype = blk["type"]
        bid = blk["id"]
        if btype == "assign":
            target = blk["params"]["target"]
            expr = blk["params"]["expr"]

            # ensure target in addr_list
            if target not in addr_list:
                addr_list.append(target)

            # ensure variables in expr in addr_list
            for v in parse_expr(expr):
                if v not in addr_list:
                    addr_list.append(v)

            atomic_ops.append({
                "op": "assign",
                "target": target,
                "expr": expr,
                "block": bid
            })

        elif btype == "while_loop":
            cond = blk["params"]["cond"]
            for v in parse_expr(cond):
                if v not in addr_list:
                    addr_list.append(v)
            atomic_ops.append({
                "op": "while_cond",
                "cond": cond,
                "block": bid
            })

        elif btype == "print":
            var = blk["params"]["var"]
            if var not in addr_list:
                addr_list.append(var)
            atomic_ops.append({
                "op": "print",
                "var": var,
                "block": bid
            })

    # Control matrix M_global construction
    n = len(blocks)
    M_global = [[0]*n for _ in range(n)]
    for conn in connections:
        src = id_to_idx[conn["from"]]
        dst = id_to_idx[conn["to"]]
        M_global[src][dst] = 1

    # c_global may store per block expressions or constants
    for blk in blocks:
        if blk["type"] == "assign":
            c_global.append(blk["params"]["expr"])
        elif blk["type"] == "while_loop":
            c_global.append(blk["params"]["cond"])
        else:
            c_global.append("")

    expanded = {
        "addr_list": addr_list,
        "M_global": M_global,
        "c_global": c_global,
        "atomic_ops": atomic_ops,
        "id_to_idx": id_to_idx
    }
    return expanded

def main():
    if len(sys.argv) != 3:
        print("Usage: python expander.py <translated.json> <expanded.json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    translated = load_translated(input_path)
    expanded = expand_blocks(translated)
    save_expanded(output_path, expanded)

    print(f"✅ Expansion completed. Output saved to {output_path}")

if __name__ == "__main__":
    main()


import json
import re
from sympy import sympify, Symbol
import sympy

def parse_linear_expr(expr_str, var_name):
    """
    Parse a simple linear expression like 'x + 2' or 'x - 3'.
    Returns (coeff_for_var, constant_term).
    """
    try:
        expr = sympify(expr_str)
        var = Symbol(var_name)
        coeff = expr.coeff(var)
        const = expr.subs(var, 0)
        return float(coeff), float(const)
    except Exception:
        # fallback: identity (no constant offset)
        return 0.0, 0.0

def transform_to_phasor(expanded_data):
    """
    Transform expanded.json (linear + control flow info)
    into full phasor vector space matrices and vectors.
    """
    id_to_idx = expanded_data["id_to_idx"]
    addr_list = expanded_data["addr_list"]
    M_global = expanded_data["M_global"]
    c_global = expanded_data["c_global"]
    atomic_ops = expanded_data["atomic_ops"]

    n_ctrl = len(M_global)
    n_data = len(addr_list)
    total_dim = n_ctrl + n_data

    # Build full M (control + data)
    M_full = [[0.0 for _ in range(total_dim)] for _ in range(total_dim)]
    c_full = [0.0 for _ in range(total_dim)]

    # Copy control block part
    for i in range(n_ctrl):
        for j in range(n_ctrl):
            M_full[i][j] = float(M_global[i][j])

    # Handle data updates from atomic_ops
    for op in atomic_ops:
        if op["op"] == "assign":
            target = op["target"]
            expr = op["expr"]

            if target in addr_list:
                data_idx = n_ctrl + addr_list.index(target)
                # Initialize default to identity
                M_full[data_idx][data_idx] = 1.0

                # Attempt to parse linear part
                coeff, const = parse_linear_expr(expr, target)
                if coeff != 0:
                    M_full[data_idx][data_idx] = coeff
                if const != 0:
                    c_full[data_idx] = const

        elif op["op"] == "init":
            target = op["var"]
            value = float(op["value"])
            if target in addr_list:
                data_idx = n_ctrl + addr_list.index(target)
                c_full[data_idx] = value

    # Build constraint vectors (phasor conditions)
    C_p = []
    c_p = []
    for op in atomic_ops:
        if op["op"] == "while_cond":
            cond = op["cond"]
            m = re.match(r"(\w+)\s*<\s*([0-9\.]+)", cond)
            if m:
                varname, threshold = m.group(1), float(m.group(2))
                if varname in addr_list:
                    vec = [0.0] * total_dim
                    data_idx = n_ctrl + addr_list.index(varname)
                    vec[data_idx] = 1.0
                    C_p.append(vec)
                    c_p.append(-threshold)
            else:
                # fallback if more complex condition
                pass

    metadata = {
        "note": "Transformed from expanded.json",
        "block_index": id_to_idx
    }

    phasor_data = {
        "addr_list": {
            "control_blocks": list(id_to_idx.keys()),
            "data_vars": addr_list
        },
        "total_dim": total_dim,
        "n_ctrl": n_ctrl,
        "n_data": n_data,
        "M_full": M_full,
        "c_full": c_full,
        "C_p": C_p,
        "c_p": c_p,
        "metadata": metadata
    }

    return phasor_data

if __name__ == "__main__":
    with open("expanded.json", "r") as f:
        expanded_data = json.load(f)

    phasor_data = transform_to_phasor(expanded_data)

    with open("phasor_transformed.json", "w") as f:
        json.dump(phasor_data, f, indent=2)

    print("✅ Phasor transformation complete -> phasor_transformed.json")


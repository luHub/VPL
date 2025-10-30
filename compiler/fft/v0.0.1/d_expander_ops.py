#!/usr/bin/env python3
"""
postprocess_atomic_ops.py

Reads expanded.json produced by expander_full.py (which contains atomic_ops),
substitutes loop_context and params into expressions, discovers concrete addresses,
and builds M_global and c_global matrices for simulation.

Usage:
    python postprocess_atomic_ops.py expanded.json

Outputs:
    - expanded_with_matrix.json  (addr_list, M_global, c_global, atomic_ops_checked)
"""

import json
import re
import sys
import math
import cmath
import numpy as np

# regex to find concrete array tokens like name[123] or name[12][3]
ADDR_RE = re.compile(r'([A-Za-z_]\w*)\s*\[\s*([0-9]+)\s*\](?:\s*\[\s*([0-9]+)\s*\])?')

def substitute_index_vars(s: str, index_map: dict, params: dict):
    """Replace identifiers present in index_map or params with numbers in string s."""
    if s is None:
        return None
    t = str(s)
    # tokens that look like identifiers
    tokens = re.findall(r'[A-Za-z_]\w*', t)
    # replace longer tokens first
    tokens = sorted(set(tokens), key=lambda x: -len(x))
    for tok in tokens:
        if tok in index_map:
            t = re.sub(r'\b' + re.escape(tok) + r'\b', str(index_map[tok]), t)
        elif tok in params:
            t = re.sub(r'\b' + re.escape(tok) + r'\b', str(params[tok]), t)
    return t

def find_addresses(s: str):
    """Return list of concrete address strings found in s."""
    if s is None:
        return []
    lst = []
    for m in ADDR_RE.finditer(s):
        name = m.group(1)
        i0 = m.group(2)
        i1 = m.group(3)
        if i1 is None:
            addr = f"{name}[{int(i0)}]"
        else:
            addr = f"{name}[{int(i0)}][{int(i1)}]"
        lst.append(addr)
    return lst

def eval_theta_expr(expr, params):
    """
    Evaluate a theta expression string (like '-2.0*PI*k1*k2/N') using params only.
    Note: loop variables should already be substituted into concrete numbers before calling.
    """
    env = {}
    env.update(params or {})
    env['math'] = math
    env['cmath'] = cmath
    if 'PI' not in env:
        env['PI'] = math.pi
    try:
        return eval(str(expr), {"__builtins__": {}}, env)
    except Exception as e:
        raise ValueError(f"Failed to eval theta '{expr}': {e}")

def build_matrices_from_atomic_ops(atomic_ops, params):
    """
    atomic_ops: list as produced by expander_full.atomic_ops
    params: dict of numeric params (N,N1,N2,...)
    Returns: addr_list, M_global (numpy array), c_global (numpy vector), ops_checked
    """
    # 1) Discover concrete addresses (walk ops in order, substitute loop_context)
    addr_order = []
    addr_index = {}
    def register(addr):
        if addr not in addr_index:
            addr_index[addr] = len(addr_order)
            addr_order.append(addr)

    # first pass: substitute and collect addresses
    processed_ops = []
    for op in atomic_ops:
        # copy op and create textual fields
        op2 = dict(op)
        # collect loop_context if any
        index_map = op.get('loop_context', {}) or {}
        # if op is assign or call, take lhs/rhs/args
        if op.get('type') == 'assign':
            lhs = op.get('lhs')
            rhs = op.get('rhs')
            lhs_c = substitute_index_vars(lhs, index_map, params)
            rhs_c = substitute_index_vars(rhs, index_map, params)
            op2['lhs_concrete'] = lhs_c
            op2['rhs_concrete'] = rhs_c
            for a in find_addresses(lhs_c) + find_addresses(rhs_c):
                register(a)
        elif op.get('type') == 'call':
            # args already in list of strings; substitute each
            args_conc = []
            for a in op.get('args', []):
                a_c = substitute_index_vars(a, index_map, params)
                args_conc.append(a_c)
                # if arg is array token with numeric index register it
                for addr in find_addresses(a_c):
                    register(addr)
            op2['args_concrete'] = args_conc
        elif op.get('type') == 'expr':
            expr_s = substitute_index_vars(op.get('expr'), index_map, params)
            op2['expr_concrete'] = expr_s
            for addr in find_addresses(expr_s):
                register(addr)
        else:
            # other types: register any textual tokens we can
            # try to find addresses in any string fields
            for k,v in op.items():
                if isinstance(v, str):
                    for addr in find_addresses(v):
                        register(addr)
        processed_ops.append(op2)

    # if no addresses found, nothing to build
    if len(addr_order) == 0:
        return addr_order, np.zeros((0,0), dtype=complex), np.zeros((0,), dtype=complex), processed_ops

    K = len(addr_order)
    M_global = np.eye(K, dtype=complex)   # start as identity
    c_global = np.zeros((K,), dtype=complex)

    # helper to map token like "rows[1][0]" -> integer index in addr_order
    def resolve_addr_token(token):
        m = ADDR_RE.search(token)
        if not m:
            return None
        name = m.group(1)
        i0 = int(m.group(2))
        i1 = m.group(3)
        if i1 is None:
            addr = f"{name}[{i0}]"
        else:
            addr = f"{name}[{i0}][{int(i1)}]"
        return addr_index.get(addr)

    # 2) Build M_global by composing per-op M_assign
    for op in processed_ops:
        if op['type'] == 'assign':
            lhs = op.get('lhs_concrete')
            rhs = op.get('rhs_concrete')
            tgt_idx = resolve_addr_token(lhs)
            if tgt_idx is None:
                # skip non-address assignments
                continue
            # create M_assign
            M_assign = np.eye(K, dtype=complex)
            M_assign[tgt_idx, :] = 0.0
            # handle rhs patterns:
            rhs_s = (rhs or "").strip()
            # pattern multiply(conv_from_polar(1, theta), ARR)
            m = re.match(r'\s*multiply\s*\(\s*conv_from_polar\s*\(\s*1\s*,\s*(.+?)\s*\)\s*,\s*([A-Za-z_]\w*(?:\s*\[\s*\d+\s*\])(?:\s*\[\s*\d+\s*\])?)\s*\)\s*$', rhs_s)
            if m:
                theta_expr = m.group(1)
                arr_token = m.group(2)
                src_idx = resolve_addr_token(arr_token)
                if src_idx is not None:
                    theta_val = eval(substitute_index_vars(theta_expr, {}, params), {"__builtins__": {}}, {'math': math, 'PI': math.pi, **params})
                    mult_val = cmath.exp(1j * theta_val)
                    M_assign[tgt_idx, src_idx] += mult_val
            else:
                # try direct array copy
                m2 = re.match(r'^\s*([A-Za-z_]\w*(?:\s*\[\s*\d+\s*\])(?:\s*\[\s*\d+\s*\])?)\s*$', rhs_s)
                if m2:
                    arr_token = m2.group(1)
                    src_idx = resolve_addr_token(arr_token)
                    if src_idx is not None:
                        M_assign[tgt_idx, src_idx] += 1.0
                else:
                    # try c_add/c_sub pattern: find first concrete array token in rhs and map it
                    arrm = re.search(r'([A-Za-z_]\w*\s*\[\s*\d+\s*\](?:\s*\[\s*\d+\s*\])?)', rhs_s)
                    if arrm:
                        src_idx = resolve_addr_token(arrm.group(1))
                        if src_idx is not None:
                            # for simplicity assume coefficient 1
                            M_assign[tgt_idx, src_idx] += 1.0
                    else:
                        # RHS unsupported; skip
                        continue
            # compose M_global = M_assign @ M_global ; c_global likewise
            M_global = M_assign @ M_global
            c_global = M_assign @ c_global
        else:
            # calls/expr/other: no direct matrix effect (printf/free), so skip
            continue

    return addr_order, M_global, c_global, processed_ops

def main():
    if len(sys.argv) < 2:
        print("Usage: python postprocess_atomic_ops.py expanded.json")
        sys.exit(1)
    infile = sys.argv[1]
    with open(infile, 'r') as f:
        expanded = json.load(f)

    atomic_ops = expanded.get('atomic_ops', [])
    # Provide numeric parameters and assume lengths for your run:
    params = {
        'N': 8,
        'N1': 2,
        'N2': 4,
        'PI': math.pi,
        # add other constants as needed
    }

    addr_list, M_global, c_global, processed_ops = build_matrices_from_atomic_ops(atomic_ops, params)

    # serialize M_global into JSON-friendly form
    M_ser = []
    for row in M_global:
        r = []
        for v in row:
            if abs(v.imag) < 1e-12:
                r.append(v.real)
            else:
                r.append([v.real, v.imag])
        M_ser.append(r)
    c_ser = []
    for v in c_global:
        if abs(v.imag) < 1e-12:
            c_ser.append(v.real)
        else:
            c_ser.append([v.real, v.imag])

    out = {
        'addr_list': addr_list,
        'M_global': M_ser,
        'c_global': c_ser,
        'atomic_ops_checked': processed_ops
    }
    with open('expanded_with_matrix.json', 'w') as f:
        json.dump(out, f, indent=2)
    print("Wrote expanded_with_matrix.json")
    print("Addresses:", len(addr_list))
    print("M_global shape:", M_global.shape)

if __name__ == "__main__":
    main()

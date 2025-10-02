# vpl_translator.py
# Requires: pip install numpy
import json
import math
import cmath
import numpy as np
from itertools import product
from collections import OrderedDict

# ---------------------------
# Utilities for affine index evaluation
# ---------------------------
def evaluate_affine_index(coeffs: dict, offset: int, index_map: dict) -> int:
    """
    coeffs: dict of loop_var -> integer coefficient
    offset: integer offset
    index_map: mapping loop_var -> integer current value
    returns integer index
    """
    s = offset
    for var, c in coeffs.items():
        if var not in index_map:
            raise KeyError(f"Index var {var} missing in index_map")
        s += c * int(index_map[var])
    return int(s)

# ---------------------------
# Safe multiplier evaluator
# ---------------------------
def make_multiplier_eval(multiplier_str: str, params: dict, local_symbols: dict):
    """
    Return a callable f(index_map) -> complex that evaluates multiplier_str.
    multiplier_str may be:
      - a plain numeric literal: '2.0', '-1'
      - a parameter name: 'alpha'
      - a python expression involving loop indices and params, e.g. 'cmath.exp(-2j*math.pi*k1*k2/N)'
    To remain flexible, we allow Python eval with a safe environment.
    """
    if multiplier_str is None or multiplier_str == "" or multiplier_str == "1":
        return lambda index_map: 1.0
    # try numeric parse first
    try:
        val = complex(float(multiplier_str))
        return lambda index_map: val
    except Exception:
        pass

    # If multiplier is like '-W' treat sign
    if multiplier_str.startswith('+') or multiplier_str.startswith('-'):
        # we'll still eval general expr below
        pass

    # build safe eval environment
    def eval_fn(index_map):
        env = {}
        # math, cmath, builtins
        env['math'] = math
        env['cmath'] = cmath
        # params (user-supplied constants)
        if params:
            for k,v in params.items():
                env[k] = v
        # local symbols: sometimes constants like 'W' will be precomputed in local_symbols mapping
        if local_symbols:
            for k,v in local_symbols.items():
                env[k] = v
        # index variables
        for k,v in index_map.items():
            env[k] = v
        try:
            val = eval(multiplier_str, {"__builtins__":{}}, env)
            return complex(val)
        except Exception as e:
            raise ValueError(f"Failed to eval multiplier '{multiplier_str}' with env indices {index_map} and params {params}: {e}")
    return eval_fn

# ---------------------------
# Helpers to flatten loop order and ranges from IR
# ---------------------------
def collect_loop_order_and_ranges(ir):
    """
    Given the top-level loop IR (a nested dict with 'op':'loop'), traverse to collect loop_vars
    in outer->inner order and their ranges expressed as Python values or symbols.
    It expects typical structure produced earlier.
    """
    loop_order = []
    ranges = OrderedDict()
    node = ir
    # node may be a 'program' with body list; find first loop or treat node as loop
    if isinstance(node, dict) and node.get('op') == 'program':
        # flatten top-level body: search for a main nested loop (we handle the first)
        found = None
        for item in node.get('body', []):
            if item.get('op') == 'loop':
                found = item
                break
        if found is None:
            raise RuntimeError("No loop found in program body")
        node = found

    # now descend nested loops
    while isinstance(node, dict) and node.get('op') == 'loop':
        var = node.get('var')
        rng = node.get('range')  # expected [start,end] - end may be expression
        loop_order.append(var)
        ranges[var] = rng
        # find nested loop in body if present
        inner = None
        for s in node.get('body', []):
            if isinstance(s, dict) and s.get('op') == 'loop':
                inner = s
                break
        if inner is None:
            break
        node = inner
    # Also collect innermost body statements (list)
    innermost = node if node.get('op') == 'loop' else None
    # If innermost is loop, get its body statements (assignments, calls)
    body = []
    if innermost:
        for s in innermost.get('body', []):
            body.append(s)
    return loop_order, ranges, body

# ---------------------------
# Build concrete per-block local matrix for a given multi-index
# ---------------------------
def build_local_matrix_for_block(assignments, loop_order, index_map, params, local_symbols=None):
    """
    assignments: list of assign dicts (lhs + rhs terms) from IR at innermost level
    loop_order: list of loop vars outer->inner (we may only need innermost vars referenced in coeffs)
    index_map: mapping loop var -> integer current values for this block
    params: dict of numeric params (e.g. N, alpha). Used to eval multipliers
    local_symbols: optional precomputed local symbol values (unused normally)
    Returns:
       var_list: ordered list of concrete addresses (strings) naming local state elements (e.g. 'X[3]')
       M_local: k x k numpy array (float or complex)
       c_local: k-dim numpy array (constants)
    """
    # collect concrete address names used in this block in occurrence order
    local_vars = []
    def concrete_address(varname, coeffs, offset):
        idx = evaluate_affine_index(coeffs, offset, index_map)
        # For simplicity produce "var[idx]" even if original was multi-dim; that's fine as a unique key
        return f"{varname}[{idx}]"

    # scan all assignments and their terms in order to collect var names
    for asg in assignments:
        # lhs
        lhs = asg['lhs']
        lhs_addr = concrete_address(lhs['var'], lhs['coeffs'], int(lhs.get('offset',0) or 0))
        if lhs_addr not in local_vars:
            local_vars.append(lhs_addr)
        # rhs terms
        for term in asg['rhs']:
            addr = concrete_address(term['var'], term['coeffs'], int(term.get('offset',0) or 0))
            if addr not in local_vars:
                local_vars.append(addr)

    k = len(local_vars)
    M_local = np.eye(k, dtype=complex)   # start with identity; assignments will replace rows
    c_local = np.zeros(k, dtype=complex)

    # function to eval multiplier for a term
    # We'll prepare evaluators for each unique multiplier string to avoid repeated eval parsing
    multiplier_cache = {}
    def get_multiplier_fn(mult_str):
        if mult_str is None:
            return lambda idx_map: 1.0
        # Normalize "-W" to "-1*W" handled by eval
        ms = mult_str.strip()
        if ms == "":
            return lambda idx_map: 1.0
        if ms not in multiplier_cache:
            multiplier_cache[ms] = make_multiplier_eval(ms, params, local_symbols or {})
        return multiplier_cache[ms]

    # Apply assignments sequentially (source order).
    # For each assignment, produce a M_assign and c_assign, then compose:
    # new_state = M_assign * old_state + c_assign
    # and update M_local, c_local via: M_local = M_assign @ M_local ; c_local = M_assign @ c_local + c_assign
    for asg in assignments:
        # create M_assign identity
        M_assign = np.eye(k, dtype=complex)
        c_assign = np.zeros(k, dtype=complex)
        # lhs target row index
        lhs = asg['lhs']
        lhs_addr = concrete_address(lhs['var'], lhs['coeffs'], int(lhs.get('offset',0) or 0))
        if lhs_addr not in local_vars:
            raise RuntimeError(f"LHS address {lhs_addr} not recorded in local_vars")
        lhs_idx = local_vars.index(lhs_addr)
        # zero out that row
        M_assign[lhs_idx, :] = 0.0
        # fill RHS terms
        for term in asg['rhs']:
            addr = concrete_address(term['var'], term['coeffs'], int(term.get('offset',0) or 0))
            if addr not in local_vars:
                # this can happen if RHS references an element not in LHS/RHS scan earlier; add
                local_vars.append(addr)
                # enlarge M_assign, M_local, c_assign, M_local etc. --- simpler approach: raise error
                raise RuntimeError(f"Encountered new addr {addr} not found in local_vars; the scanner should have included it")
            coeff_idx = local_vars.index(addr)
            multiplier = term.get('multiplier', '1')
            fn = get_multiplier_fn(multiplier)
            val = fn(index_map)  # numeric complex
            # add contribution to lhs row
            M_assign[lhs_idx, coeff_idx] += val
        # constants in RHS? If any term includes numeric constants without var, not supported here. Could be extended.
        # Now compose M_assign into accumulator
        M_local = M_assign @ M_local
        c_local = M_assign @ c_local + c_assign

    return local_vars, M_local, c_local

# ---------------------------
# Build full global matrix by iterating over all multi-indices
# ---------------------------
def build_global_matrix_from_ir(ir, assume_lengths: dict, params: dict):
    """
    ir: either a program dict containing loops or a single loop dict
    assume_lengths: dict mapping loop var -> integer length (e.g. {'k':4, 'm':2})
    params: dict of numeric parameters for multiplier evaluation (e.g. {'N':8})
    Returns:
       result: dict with keys:
         - loop_order: list of loop vars
         - per_block_var_list: canonical local var list (may vary per block)
         - M_global: big numpy array (complex)
         - var_index_map: mapping global index -> variable address name (for diagnostics)
    """
    # get loop order and innermost assignments
    loop_order, ranges, innermost_body = collect_loop_order_and_ranges(ir)
    if not loop_order:
        raise RuntimeError("No nested loop structure found in IR")

    # verify assume_lengths contain needed variables
    for v in loop_order:
        if v not in assume_lengths:
            raise KeyError(f"Missing assume_lengths entry for loop variable '{v}'")

    # compute sizes product
    lengths = [int(assume_lengths[v]) for v in loop_order]
    total_blocks = 1
    for L in lengths:
        total_blocks *= L

    # For each block we will compute local_vars and its M_local. Local var ordering may vary,
    # but we want a canonical global ordering of state variables across all blocks.
    # We'll collect global addresses across all blocks in lexicographic order of blocks and local_vars order.
    # Then the global state vector is concatenation of each block's local_vars in block order.

    block_local_vars_list = []  # list of lists
    block_M_locals = []
    block_c_locals = []

    # Iterate over all multi-indices lexicographically (outer->inner)
    loop_ranges = [range(int(assume_lengths[v])) for v in loop_order]
    for multi_idx in product(*loop_ranges):
        index_map = {loop_order[i]: int(multi_idx[i]) for i in range(len(loop_order))}
        # build local for this block
        # innermost_body may include various statements; filter only assignments for now
        assignments = [s for s in innermost_body if s.get('op') == 'assign']
        local_vars, M_local, c_local = build_local_matrix_for_block(assignments, loop_order, index_map, params)
        block_local_vars_list.append(local_vars)
        block_M_locals.append(M_local)
        block_c_locals.append(c_local)

    # Now create global mapping: flatten blocks in block order and local var order
    # compute global dimension
    k_sizes = [len(vs) for vs in block_local_vars_list]
    if not k_sizes:
        raise RuntimeError("No blocks found or no local variables")
    # We require that all blocks have the same local dimension k; if not, translator can pad but for now assert
    k0 = k_sizes[0]
    for idx,k in enumerate(k_sizes):
        if k != k0:
            raise RuntimeError(f"Inconsistent local dimension across blocks: block 0 has {k0}, block {idx} has {k}")

    k = k0
    K = k * total_blocks
    M_global = np.zeros((K, K), dtype=complex)
    c_global = np.zeros(K, dtype=complex)
    global_addr = []  # list of strings naming each slot

    for b_idx in range(total_blocks):
        block_off = b_idx * k
        M_global[block_off:block_off+k, block_off:block_off+k] = block_M_locals[b_idx]
        c_global[block_off:block_off+k] = block_c_locals[b_idx]
        # append addresses
        global_addr.extend(block_local_vars_list[b_idx])

    result = {
        'loop_order': loop_order,
        'lengths': {v:int(assume_lengths[v]) for v in loop_order},
        'total_blocks': total_blocks,
        'k_local': k,
        'M_global': M_global,
        'c_global': c_global,
        'global_addr': global_addr,
        'block_local_vars_list': block_local_vars_list,
        'block_M_locals': block_M_locals
    }
    return result

# ---------------------------
# Helper: collect loop order and innermost body (copied here for completeness)
# ---------------------------
def collect_loop_order_and_ranges(ir):
    loop_order = []
    ranges = OrderedDict()
    node = ir
    if isinstance(node, dict) and node.get('op') == 'program':
        found = None
        for item in node.get('body', []):
            if item.get('op') == 'loop':
                found = item
                break
        if found is None:
            raise RuntimeError("No loop found in program body")
        node = found

    while isinstance(node, dict) and node.get('op') == 'loop':
        var = node.get('var')
        rng = node.get('range')
        loop_order.append(var)
        ranges[var] = rng
        inner = None
        for s in node.get('body', []):
            if isinstance(s, dict) and s.get('op') == 'loop':
                inner = s
                break
        if inner is None:
            break
        node = inner
    body = []
    if node and isinstance(node, dict):
        for s in node.get('body', []):
            body.append(s)
    return loop_order, ranges, body

# ---------------------------
# JSON serialization helpers
# ---------------------------
def serialize_complex_matrix(mat: np.ndarray):
    """Convert numpy complex matrix to nested lists with pairs [real, imag]"""
    out = []
    for row in mat:
        out_row = []
        for val in row:
            if abs(val.imag) < 1e-12:
                out_row.append(val.real)
            else:
                out_row.append([val.real, val.imag])
        out.append(out_row)
    return out

# ---------------------------
# Demo usage: small FFT butterfly example
# ---------------------------
if __name__ == "__main__":
    # Example IR for a nested FFT-like butterfly stage:
    # outer loop is over m, inner loop over k, but here we build program->loop(k) for simplicity
    # We'll craft a small program dict consistent with earlier JSON IR format
    program_ir = {
        "op": "program",
        "body": [
            {
                "op": "loop",
                "var": "k",
                "range": [0, "N1-1"],
                "body": [
                    {
                        "op": "assign",
                        "lhs": {"var":"X", "coeffs":{"k":1, "m":0}, "offset":0},
                        "rhs": [
                            {"var":"X", "coeffs":{"k":1,"m":0}, "offset":0, "multiplier":"1"},
                            {"var":"X", "coeffs":{"k":1,"m":1}, "offset":0, "multiplier":"W"}
                        ]
                    },
                    {
                        "op": "assign",
                        "lhs": {"var":"X", "coeffs":{"k":1,"m":1}, "offset":0},
                        "rhs": [
                            {"var":"X", "coeffs":{"k":1,"m":0}, "offset":0, "multiplier":"1"},
                            {"var":"X", "coeffs":{"k":1,"m":1}, "offset":0, "multiplier":"-W"}
                        ]
                    }
                ]
            }
        ]
    }

    # We need both 'k' and 'm' lengths to be present in assume_lengths since coefficients reference both.
    assume_lengths = {'k':2, 'm':2}  # tiny example: k in [0,1], m in [0,1]
    # params: supply numeric values for N and define W as function using python expression
    N = 4
    params = {'N': N}
    # We'll not predefine W; in multiplier expressions, we use an expression string.
    # For this demo, our multiplier strings are "W" and "-W" which must be in local_symbols or params.
    # Provide a local_symbols function: for each block, W may depend on k,m,N -> use expression when building
    # So we will instead replace "W" by explicit expression string using k and m inside multiplier: e.g. 'cmath.exp(-2j*math.pi*k*m/N)'
    # Let's update program_ir multipliers accordingly:
    for stmt in program_ir['body'][0]['body']:
        for term in stmt['rhs']:
            if term['multiplier'] == "W":
                term['multiplier'] = "cmath.exp(-2j*math.pi*k*m/N)"
            if term['multiplier'] == "-W":
                term['multiplier'] = "-cmath.exp(-2j*math.pi*k*m/N)"

    # Build global matrix
    result = build_global_matrix_from_ir(program_ir, assume_lengths, params)

    M_global = result['M_global']
    c_global = result['c_global']
    addr = result['global_addr']
    print("Loop order:", result['loop_order'])
    print("Assumed lengths:", result['lengths'])
    print("k local:", result['k_local'])
    print("Total global dimension:", M_global.shape)
    print("\nGlobal address mapping (first few):")
    for i,a in enumerate(addr[:min(12,len(addr))]):
        print(i, a)
    # print global matrix (compact)
    print("\nM_global (dense) rows 0..min(8):")
    for r in range(min(8, M_global.shape[0])):
        row = M_global[r]
        # print as readable numbers
        pretty = ["{:.3f}{:+.3f}j".format(val.real, val.imag) if abs(val.imag)>1e-12 else "{:.3f}".format(val.real) for val in row[:min(12, len(row))]]
        print(r, pretty)
    # serialize to JSON file
    out_ir = OrderedDict()
    out_ir['generated_from'] = 'demo_fft_butterfly'
    out_ir['loop_order'] = result['loop_order']
    out_ir['lengths'] = result['lengths']
    out_ir['k_local'] = result['k_local']
    out_ir['global_dim'] = M_global.shape[0]
    out_ir['global_addr'] = result['global_addr']
    out_ir['M_global'] = serialize_complex_matrix(M_global)
    out_ir['c_global'] = [ (v.real if abs(v.imag)<1e-12 else [v.real, v.imag]) for v in c_global ]

    with open("vpl_translated_demo_fft.json", "w") as f:
        json.dump(out_ir, f, indent=2)

    print("\nWrote vpl_translated_demo_fft.json")

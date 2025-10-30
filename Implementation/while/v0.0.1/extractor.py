#!/usr/bin/env python3
"""
extractor.py (fixed)
Reads input C file and writes structured JSON (variables + statements).

Usage:
    python extractor.py input.c extracted.json

Output format:
{
  "variables": [{"name":"x","type":"int","init":"0"}, ...],
  "statements": [
    {"id":"s0","type":"while","cond":"x < 5","body":[ ... ]},
    {"id":"s1","type":"print","args":["x"]}
  ]
}
"""
import re
import json
import sys

# -----------------------
# Utilities
# -----------------------
def remove_comments_and_directives(code: str) -> str:
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.S)   # block comments
    code = re.sub(r'//.*?$', '', code, flags=re.M)      # line comments
    lines = [ln for ln in code.splitlines() if not ln.strip().startswith('#')]
    return "\n".join(lines)

def find_matching(code: str, start_idx: int, open_ch: str, close_ch: str) -> int:
    depth = 0
    L = len(code)
    for i in range(start_idx, L):
        ch = code[i]
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
    raise ValueError(f"No match for {open_ch} starting at {start_idx}")

class IDGen:
    def __init__(self, prefix="s"):
        self.n = 0
        self.pref = prefix
    def next(self):
        val = f"{self.pref}{self.n}"
        self.n += 1
        return val

# -----------------------
# Parsing primitives
# -----------------------
def extract_main_body(code: str) -> str:
    """
    Try to find the main() function body. If found, return the interior of braces.
    Otherwise return the whole code.
    """
    m = re.search(r'\bint\s+main\b[^{]*\{', code)
    if not m:
        m = re.search(r'\bmain\b[^{]*\{', code)
    if not m:
        return code
    brace_start = code.find('{', m.start())
    brace_end = find_matching(code, brace_start, '{', '}')
    return code[brace_start+1:brace_end]

def collect_var_decls(body: str):
    """
    Collect declarations inside body like:
      int x;
      int x = 0;
    Returns list of var dicts and body with these declarations removed.
    """
    vars_found = []
    # Match simple single declarations only (no comma lists)
    pat = re.compile(r'\b(int|float|double)\s+([A-Za-z_]\w*)(\s*=\s*([^;]+))?\s*;')
    def repl(m):
        typ = m.group(1)
        name = m.group(2)
        init = m.group(4)
        entry = {"name": name, "type": typ}
        if init is not None:
            entry["init"] = init.strip()
        vars_found.append(entry)
        return ''  # remove declaration from body
    new_body = pat.sub(repl, body)
    return vars_found, new_body

def parse_simple_statement(piece: str):
    piece = piece.strip()
    # increment/decrement
    m = re.match(r'^([A-Za-z_]\w*)\s*(\+\+|--)\s*$', piece)
    if m:
        return {"type": "increment", "target": m.group(1), "op": m.group(2)}

    # print / printf
    m = re.match(r'^(printf|print)\s*\((.*)\)\s*$', piece, flags=re.S)
    if m:
        args = m.group(2).strip()
        if args == "":
            return {"type": "print", "args": []}
        # naive split on commas (good for simple cases)
        args_list = [a.strip() for a in re.split(r'\s*,\s*', args)]
        return {"type": "print", "args": args_list}

    # assignment (ensure it's not == or <= etc.)
    if ('==' in piece) or ('!=' in piece) or ('<=' in piece) or ('>=' in piece):
        return {"type": "raw", "stmt": piece}
    m = re.match(r'^([A-Za-z_]\w*)\s*=\s*(.+)$', piece)
    if m:
        target = m.group(1)
        expr = m.group(2).strip()
        return {"type": "assign", "target": target, "expr": expr}

    # fallback raw
    return {"type": "raw", "stmt": piece}

def tokenize_statements(code: str, idgen: IDGen):
    """
    Tokenize the code inside a function body into sequential statements.
    This handles:
      - while (...) { ... } (nested)
      - for (...) { ... } (skeleton)
      - semicolon-terminated statements (respecting parentheses and string quotes)
    Returns a list of statement dicts with 'id' fields assigned.
    """
    stmts = []
    i = 0
    L = len(code)
    while i < L:
        # skip whitespace
        while i < L and code[i].isspace():
            i += 1
        if i >= L:
            break

        # detect 'while' keyword
        if code.startswith('while', i) and (i+5==L or not code[i+5].isalnum()):
            paren_start = code.find('(', i)
            if paren_start == -1:
                raise SyntaxError("Malformed while: missing '('")
            paren_end = find_matching(code, paren_start, '(', ')')
            cond = code[paren_start+1:paren_end].strip()
            # find body '{...}'
            brace_start = code.find('{', paren_end)
            if brace_start == -1:
                raise SyntaxError("Malformed while: missing '{'")
            brace_end = find_matching(code, brace_start, '{', '}')
            body_code = code[brace_start+1:brace_end]
            body_stmts = tokenize_statements(body_code, idgen)
            stmts.append({"id": idgen.next(), "type": "while", "cond": cond, "body": body_stmts})
            i = brace_end + 1
            continue

        # detect 'for' keyword (simple handling)
        if code.startswith('for', i) and (i+3==L or not code[i+3].isalnum()):
            paren_start = code.find('(', i)
            if paren_start == -1:
                raise SyntaxError("Malformed for: missing '('")
            paren_end = find_matching(code, paren_start, '(', ')')
            header = code[paren_start+1:paren_end].strip()
            brace_start = code.find('{', paren_end)
            if brace_start == -1:
                raise SyntaxError("Malformed for: missing '{'")
            brace_end = find_matching(code, brace_start, '{', '}')
            body_code = code[brace_start+1:brace_end]
            body_stmts = tokenize_statements(body_code, idgen)
            stmts.append({"id": idgen.next(), "type": "for", "header": header, "body": body_stmts})
            i = brace_end + 1
            continue

        # otherwise find semicolon that is top-level (not inside parentheses or string)
        j = i
        paren_depth = 0
        in_string = False
        string_char = ''
        while j < L:
            ch = code[j]
            if in_string:
                if ch == string_char:
                    in_string = False
                    string_char = ''
                # support escaped quotes "\""
                elif ch == '\\' and j+1 < L:
                    j += 2
                    continue
            else:
                if ch == '"' or ch == "'":
                    in_string = True
                    string_char = ch
                elif ch == '(':
                    paren_depth += 1
                elif ch == ')':
                    if paren_depth > 0:
                        paren_depth -= 1
                elif ch == ';' and paren_depth == 0:
                    break
            j += 1

        if j >= L:
            # trailing piece without semicolon
            piece = code[i:].strip()
            i = L
        else:
            piece = code[i:j].strip()
            i = j + 1  # skip the semicolon

        if piece:
            parsed = parse_simple_statement(piece)
            parsed["id"] = idgen.next()
            stmts.append(parsed)
        # continue loop
    return stmts

# -----------------------
# Top-level extract
# -----------------------
def extract_from_file(inpath: str):
    with open(inpath, 'r') as f:
        raw = f.read()
    cleaned = remove_comments_and_directives(raw)
    main_body = extract_main_body(cleaned)

    # collect variable declarations and remove them from main body
    vars_found, body_no_decls = collect_var_decls(main_body)

    # tokenize statements with id generator
    idgen = IDGen()
    stmts = tokenize_statements(body_no_decls, idgen)

    # Ensure variables include assignment targets not declared
    names = {v["name"] for v in vars_found}
    for s in stmts:
        if s["type"] == "assign":
            if s["target"] not in names:
                vars_found.append({"name": s["target"], "type": "int"})
                names.add(s["target"])
        if s["type"] == "increment":
            if s["target"] not in names:
                vars_found.append({"name": s["target"], "type": "int"})
                names.add(s["target"])

    program = {"variables": vars_found, "statements": stmts}
    return program

# -----------------------
# CLI
# -----------------------
if __name__ == "__main__":
    infile = "input.c"
    outfile = "extracted.json"
    if len(sys.argv) >= 2:
        infile = sys.argv[1]
    if len(sys.argv) >= 3:
        outfile = sys.argv[2]

    try:
        prog = extract_from_file(infile)
        with open(outfile, "w") as f:
            json.dump(prog, f, indent=2)
        print(f"[extractor] ✅ Wrote {outfile} (variables: {len(prog['variables'])}, statements: {len(prog['statements'])})")
    except Exception as e:
        print(f"[extractor] ❌ Parse error: {e}")
        raise


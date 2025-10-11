import json
import sys

def load_extracted_json(file_path):
    """Load the JSON file produced by the extractor stage."""
    with open(file_path, 'r') as f:
        return json.load(f)

def create_block(block_id, block_type, params):
    """Create a block dictionary with a unique ID, type, and parameters."""
    return {"id": block_id, "type": block_type, "params": params}

def translate_statement(stmt_obj, blocks, connections, prev_block_id=None):
    """
    Recursively translate statements into block graph.
    Returns the ID of the last block generated in this sequence.
    """
    stmt_type = stmt_obj.get("type")
    stmt_id = stmt_obj.get("id", f"auto_{len(blocks)}")
    last_id = None

    # Assignment
    if stmt_type == "assign":
        b = create_block(f"b_{stmt_id}", "assign", {
            "target": stmt_obj["target"],
            "expr": stmt_obj["expr"]
        })
        blocks.append(b)
        if prev_block_id:
            connections.append({"from": prev_block_id, "to": b["id"]})
        last_id = b["id"]

    # Print
    elif stmt_type == "print":
        args = stmt_obj.get("args", [])
        varname = args[-1] if len(args) > 0 else ""
        b = create_block(f"b_{stmt_id}", "print", {"var": varname})
        blocks.append(b)
        if prev_block_id:
            connections.append({"from": prev_block_id, "to": b["id"]})
        last_id = b["id"]

    # While loop
    elif stmt_type == "while":
        cond = stmt_obj.get("cond", "")
        loop_block = create_block(f"b_{stmt_id}", "while_loop", {"cond": cond})
        blocks.append(loop_block)
        if prev_block_id:
            connections.append({"from": prev_block_id, "to": loop_block["id"]})

        # Translate body recursively
        body_stmts = stmt_obj.get("body", [])
        prev = loop_block["id"]
        last_body_id = loop_block["id"]
        for s in body_stmts:
            last_body_id = translate_statement(s, blocks, connections, prev)
            prev = last_body_id

        # Connect body back to while loop for iteration
        if last_body_id:
            connections.append({"from": last_body_id, "to": loop_block["id"]})

        last_id = loop_block["id"]

    # Raw (fallback)
    elif stmt_type == "raw":
        b = create_block(f"b_{stmt_id}", "raw", {"stmt": stmt_obj.get("stmt", "")})
        blocks.append(b)
        if prev_block_id:
            connections.append({"from": prev_block_id, "to": b["id"]})
        last_id = b["id"]

    else:
        # Unknown statement type — ignore or warn
        print(f"⚠️ Warning: Unrecognized statement type: {stmt_type}")

    return last_id

def translate_program(extracted):
    """Main translation function: converts extracted structure into block graph."""
    blocks = []
    connections = []

    # Handle variables
    for var in extracted.get("variables", []):
        b = create_block(f"init_{var['name']}", "init_var", {
            "name": var["name"],
            "type": var["type"],
            "init": var["init"]
        })
        blocks.append(b)

    # Translate statements
    prev_block_id = None
    # If there are variables, start after the last init block
    if blocks:
        prev_block_id = blocks[-1]["id"]

    for stmt in extracted.get("statements", []):
        prev_block_id = translate_statement(stmt, blocks, connections, prev_block_id)

    return {
        "blocks": blocks,
        "connections": connections
    }

def save_translated_json(output_path, translated):
    """Save the translated block graph to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(translated, f, indent=2)

def main():
    if len(sys.argv) != 3:
        print("Usage: python translator.py <input_extracted.json> <output_translated.json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    extracted = load_extracted_json(input_path)
    translated = translate_program(extracted)
    save_translated_json(output_path, translated)
    print(f"✅ Translation completed. Output saved to {output_path}")

if __name__ == "__main__":
    main()


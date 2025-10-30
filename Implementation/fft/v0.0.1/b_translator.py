import json

class VPLTranslator:
    def __init__(self, ir):
        self.ir = ir
        self.vpl = {"blocks": [], "connections": []}
        self.block_counter = 0

    def new_block(self, block_type, params=None):
        bid = f"b{self.block_counter}"
        self.block_counter += 1
        block = {"id": bid, "type": block_type, "params": params or {}}
        self.vpl["blocks"].append(block)
        return bid

    def connect(self, src, dst):
        if src and dst:
            self.vpl["connections"].append({"from": src, "to": dst})

    def translate(self):
        for func in self.ir["functions"]:
            self.translate_func(func)
        return self.vpl

    def translate_func(self, func):
        last_block = None
        for stmt in func["body"]:
            blk = self.translate_stmt(stmt)
            if last_block and blk:
                self.connect(last_block, blk)
            if blk:
                last_block = blk

    def translate_stmt(self, stmt):
        if stmt.get("type") == "assignment":
            return self.translate_assignment(stmt)
        elif stmt.get("type") == "for_loop":
            return self.translate_loop(stmt)
        elif stmt.get("type") == "funccall":
            return self.translate_funccall(stmt)
        elif "decl" in stmt:
            return self.new_block("var_decl", {"name": stmt["decl"]})
        else:
            return self.new_block("raw_stmt", stmt)

    def translate_assignment(self, stmt):
        src = self.new_block("expr", {"expr": stmt["value"]})
        dst = self.new_block("mem_write", {"target": stmt["target"]})
        self.connect(src, dst)
        return dst

    def translate_loop(self, stmt):
        loop_block = self.new_block("for_loop", {
            "var": stmt["var"],
            "init": stmt["init"],
            "cond": stmt["cond"],
            "next": stmt["next"]
        })

        last_child = None
        for s in stmt["body"]:
            child = self.translate_stmt(s)
            if last_child and child:
                self.connect(last_child, child)
            if child:
                last_child = child
        if last_child:
            self.connect(loop_block, last_child)
        return loop_block

    def translate_funccall(self, stmt):
        return self.new_block("funccall", {
            "name": stmt["name"],
            "args": stmt["args"]
        })

# ---------------------------
# Run extractor
# ---------------------------
if __name__ == "__main__":
 with open("ir.json", "r") as f:
        ir = json.load(f)
 translator = VPLTranslator(ir)
 vpl_ir = translator.translate()
 print(json.dumps(vpl_ir, indent=2))

import json

def generate_verilog(phasor_json, module_name="vpl_circuit"):
    addr_list = phasor_json["addr_list"]
    M_full = phasor_json["M_full"]
    c_full = phasor_json["c_full"]
    C_p = phasor_json["C_p"]
    c_p = phasor_json["c_p"]
    total_dim = phasor_json["total_dim"]
    n_ctrl = phasor_json["n_ctrl"]
    n_data = phasor_json["n_data"]

    control_blocks = addr_list["control_blocks"]
    data_vars = addr_list["data_vars"]

    # Only data variables become registers
    verilog = []
    verilog.append(f"module {module_name}(input clk, input reset, output reg halt);")
    verilog.append("")

    # Declare registers for data vars
    for var in data_vars:
        verilog.append(f"  reg [31:0] {var};")
    verilog.append("")

    # Internal signals for state updates
    for var in data_vars:
        verilog.append(f"  wire [31:0] next_{var};")
    verilog.append("")

    # Halt signal from phasor condition
    verilog.append("  wire halt_cond;")

    # Compute next-state logic from M and c for data vars only
    data_start = n_ctrl
    for i, var in enumerate(data_vars):
        row_idx = data_start + i
        expr_terms = []
        for j, col in enumerate(M_full[row_idx]):
            if col != 0.0:
                # Check if source is control or data
                if j < n_ctrl:
                    # Control block contribution (can be a trigger)
                    expr_terms.append(f"{int(col)}")
                else:
                    src_var = data_vars[j - n_ctrl]
                    if col == 1:
                        expr_terms.append(f"{src_var}")
                    else:
                        expr_terms.append(f"{int(col)}*{src_var}")
        if c_full[row_idx] != 0.0:
            expr_terms.append(str(int(c_full[row_idx])))
        rhs = " + ".join(expr_terms) if expr_terms else str(int(c_full[row_idx]))
        verilog.append(f"  assign next_{var} = {rhs};")
    verilog.append("")

    # Phasor condition
    # Example: C_p * X + c_p <= 0
    # We'll implement a single condition
    phasor_expr_terms = []
    for j, coef in enumerate(C_p[0]):
        if coef != 0.0:
            if j < n_ctrl:
                phasor_expr_terms.append(str(int(coef)))
            else:
                var = data_vars[j - n_ctrl]
                if coef == 1:
                    phasor_expr_terms.append(f"{var}")
                else:
                    phasor_expr_terms.append(f"{int(coef)}*{var}")
    if c_p[0] != 0.0:
        phasor_expr_terms.append(str(int(c_p[0])))
    phasor_rhs = " + ".join(phasor_expr_terms)
    verilog.append(f"  assign halt_cond = ({phasor_rhs}) >= 0;")
    verilog.append("")

    # Sequential block
    verilog.append("  always @(posedge clk or posedge reset) begin")
    verilog.append("    if (reset) begin")
    for var in data_vars:
        verilog.append(f"      {var} <= 0;")
    verilog.append("      halt <= 0;")
    verilog.append("    end else if (!halt) begin")
    verilog.append("      if (halt_cond) begin")
    verilog.append("        halt <= 1;")
    verilog.append("      end else begin")
    for var in data_vars:
        verilog.append(f"        {var} <= next_{var};")
    verilog.append("      end")
    verilog.append("    end")
    verilog.append("  end")

    verilog.append("endmodule")

    return "\n".join(verilog)


if __name__ == "__main__":
    with open("phasor_transformed.json", "r") as f:
        phasor_json = json.load(f)
    verilog_code = generate_verilog(phasor_json, "vpl_loop")
    with open("vpl_loop.v", "w") as f:
        f.write(verilog_code)
    print("[+] Verilog RTL generated: vpl_loop.v")


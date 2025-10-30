import json

def phasor_to_ngspice(phasor_file, netlist_file="circuit.sp"):
    # Load the phasor-transformed JSON
    with open(phasor_file, "r") as f:
        data = json.load(f)

    addr_list = data["addr_list"]
    control_blocks = addr_list["control_blocks"]
    data_vars = addr_list["data_vars"]
    M = data["M_full"]
    c_full = data["c_full"]
    C_p = data["C_p"]
    c_p = data["c_p"]

    n_ctrl = len(control_blocks)
    n_data = len(data_vars)
    total_dim = data["total_dim"]

    lines = []
    lines.append("* SPICE netlist auto-generated from VPL phasor representation")
    lines.append(".title VPL to SPICE Mapping")

    # Define voltage sources for control blocks
    for i, cb in enumerate(control_blocks):
        lines.append(f"V{cb} {cb} 0 DC 0")
    for i, dv in enumerate(data_vars):
        lines.append(f"V{dv} {dv} 0 DC 0")

    # M_full defines linear transformations: V_next = M*V + c
    # We model these as controlled sources
    lines.append("* Controlled sources implementing M_full")
    for row in range(total_dim):
        expr_terms = []
        for col in range(total_dim):
            coeff = M[row][col]
            if coeff != 0.0:
                node = control_blocks[col] if col < n_ctrl else data_vars[col - n_ctrl]
                expr_terms.append(f"{coeff}*V({node})")

        # Add constant offset if any
        const_val = c_full[row]
        expr_str = " + ".join(expr_terms) if expr_terms else "0"
        if const_val != 0.0:
            expr_str += f" + ({const_val})"

        # Output node for this equation
        node_out = control_blocks[row] if row < n_ctrl else data_vars[row - n_ctrl]
        lines.append(f"EBUF{row} {node_out}_next 0 VALUE={{ {expr_str} }}")

    # Phasor halting condition represented as a comparator
    lines.append("* Phasor halting condition")
    for i, cond_row in enumerate(C_p):
        terms = []
        for j, coeff in enumerate(cond_row):
            if coeff != 0.0:
                node = control_blocks[j] if j < n_ctrl else data_vars[j - n_ctrl]
                terms.append(f"{coeff}*V({node})")
        rhs = c_p[i]
        cond_expr = " + ".join(terms) if terms else "0"
        lines.append(f"* Halting when: {cond_expr} + ({rhs}) = 0")

    # Clock / iteration modeling
    lines.append("* Time stepping")
    lines.append("VCLK clk 0 PULSE(0 1 0 1n 1n 1u 2u)")

    # Control section
    lines.append(".control")
    lines.append("tran 1u 50u")
    for dv in data_vars:
        lines.append(f"plot V({dv})")
    lines.append(".endc")
    lines.append(".end")

    with open(netlist_file, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ NGSPICE netlist generated: {netlist_file}")


if __name__ == "__main__":
    # Example usage:
    phasor_to_ngspice("phasor_transformed.json", "circuit.sp")


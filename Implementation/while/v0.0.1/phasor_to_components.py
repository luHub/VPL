import json
import networkx as nx
import matplotlib.pyplot as plt

def phasor_to_components(phasor_file):
    """
    Translate a VPL phasor representation (phasor.json)
    into an abstract list of analog components.
    """

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
    total_dim = data["total_dim"]

    components = []

    # --- 1. Ground reference
    components.append({
        "type": "node_ref",
        "nodes": ["GND"],
        "params": {"desc": "Reference ground"}
    })

    # --- 2. DC sources for initialization
    for cb in control_blocks:
        components.append({
            "type": "vsource",
            "name": f"V_{cb}",
            "nodes": [cb, "GND"],
            "params": {"DC": 0.0}
        })
    for dv in data_vars:
        components.append({
            "type": "vsource",
            "name": f"V_{dv}",
            "nodes": [dv, "GND"],
            "params": {"DC": 0.0}
        })

    # --- 3. VCVS for each equation in M_full
    for row in range(total_dim):
        expr_terms = []
        for col in range(total_dim):
            coeff = M[row][col]
            if coeff != 0.0:
                node = control_blocks[col] if col < n_ctrl else data_vars[col - n_ctrl]
                expr_terms.append((coeff, node))

        const_val = c_full[row]
        node_out = control_blocks[row] if row < n_ctrl else data_vars[row - n_ctrl]

        components.append({
            "type": "vcvs",
            "name": f"E_buf_{row}",
            "nodes": [f"{node_out}_next", "GND"],
            "params": {
                "expr_terms": expr_terms,
                "offset": const_val
            }
        })

    # --- 4. Comparator for halting conditions
    for i, cond_row in enumerate(C_p):
        terms = []
        for j, coeff in enumerate(cond_row):
            if coeff != 0.0:
                node = control_blocks[j] if j < n_ctrl else data_vars[j - n_ctrl]
                terms.append((coeff, node))
        components.append({
            "type": "comparator",
            "name": f"C_halt_{i}",
            "nodes": ["halt", "GND"],
            "params": {
                "terms": terms,
                "threshold": -c_p[i],
                "desc": "Phasor halting condition"
            }
        })

    # --- 5. Clock
    components.append({
        "type": "clock",
        "name": "CLK",
        "nodes": ["clk", "GND"],
        "params": {"amplitude": 1.0, "period": 2e-6}
    })

    return components


def build_graph_from_components(components):
    """
    Build a NetworkX graph representing the schematic
    from the analog component list.
    """
    G = nx.MultiDiGraph()

    for comp in components:
        ctype = comp["type"]
        name = comp.get("name", ctype)
        nodes = comp["nodes"]

        # Add component as a node
        G.add_node(name, label=f"{ctype}\n{name}", shape="box", color="lightblue")

        # Add edges between component and its electrical nodes
        for n in nodes:
            if not G.has_node(n):
                G.add_node(n, label=n, shape="ellipse", color="lightgray")
            G.add_edge(name, n)
            G.add_edge(n, name)

    return G


def draw_schematic_graph(G):
    """
    Draw the graph with nicer styling
    """
    pos = nx.spring_layout(G, seed=42, k=0.7)

    comp_nodes = [n for n, d in G.nodes(data=True) if "\n" in d["label"]]
    term_nodes = [n for n, d in G.nodes(data=True) if "\n" not in d["label"]]

    nx.draw_networkx_nodes(G, pos, nodelist=term_nodes, node_shape='o', node_size=800,
                           node_color='lightgray', edgecolors='black')
    nx.draw_networkx_nodes(G, pos, nodelist=comp_nodes, node_shape='s', node_size=1200,
                           node_color='skyblue', edgecolors='black')

    nx.draw_networkx_labels(G, pos, labels=nx.get_node_attributes(G, "label"), font_size=8)
    nx.draw_networkx_edges(G, pos, arrows=False, alpha=0.5)

    plt.title("Analog Schematic Graph from VPL Phasor Model")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # 1. Convert phasor to component list
    components = phasor_to_components("phasor_transformed.json")

    # 2. Print components to inspect
    for comp in components:
        print(comp)

    # 3. Build and draw schematic
    G = build_graph_from_components(components)
    draw_schematic_graph(G)


import json
import numpy as np

def pretty_vector(vec, names):
    """Helper: format vector with labels."""
    return " | ".join([f"{name}:{val:.3f}" for name, val in zip(names, vec)])

def math_simulator_phasor_verbose(trace_file="phasor_output.json", max_steps=50):
    # Load phasor transformer output
    with open(trace_file, "r") as f:
        data = json.load(f)

    control_blocks = data["addr_list"]["control_blocks"]
    data_vars = data["addr_list"]["data_vars"]
    n_ctrl = data["n_ctrl"]
    n_data = data["n_data"]
    total_dim = data["total_dim"]

    # Convert lists to NumPy arrays
    M_full = np.array(data["M_full"], dtype=float)
    c_full = np.array(data["c_full"], dtype=float).reshape((total_dim,))
    C_p = np.array(data["C_p"], dtype=float)
    c_p = np.array(data["c_p"], dtype=float).reshape((-1,))

    # Build names for labeling the vector space
    names = control_blocks + data_vars

    # Initialize X
    X = np.zeros((total_dim,))
    X[0] = 1.0  # start at init_x
    for i in range(n_data):
        X[n_ctrl + i] = 0.0

    print("\n===================================================")
    print("🔸 VPL PHASOR MATHEMATICAL SIMULATOR (FULL TRACE)")
    print("===================================================")
    print(f"Control blocks ({n_ctrl}): {control_blocks}")
    print(f"Data variables ({n_data}): {data_vars}")
    print(f"Total dimension of vector space: {total_dim}")
    print("\nInitial state vector:")
    print(f"X₀ = [{pretty_vector(X, names)}]")

    print("\nM_full (transition matrix):")
    print(M_full)
    print("\nc_full (offset vector):")
    print(c_full)
    print("\nC_p (phasor guard matrix):")
    print(C_p)
    print("\nc_p (phasor guard offset):")
    print(c_p)

    print("\n====================================")
    print("BEGIN SIMULATION")
    print("====================================\n")

    for step in range(max_steps):
        print(f"\n--- STEP {step} ---")
        print(f"Current state X_{step}:\n  {pretty_vector(X, names)}")

        # Active control block
        active_idx = np.argmax(X[:n_ctrl])
        active_block = control_blocks[active_idx]
        print(f"🧭 Active control block: {active_block} (index {active_idx})")

        # Phasor guard evaluation
        guard_val = C_p @ X + c_p
        print("\nGuard evaluation:")
        print(f"C_p * X_{step} = {C_p @ X}")
        print(f"C_p * X_{step} + c_p = {guard_val}")

        if np.any(guard_val > 0):
            print(f"⛔ Guard condition violated at step {step}. Halting.")
            break

        # Transition
        print("\nComputing next state:")
        print(f"M_full @ X_{step} = {M_full @ X}")
        print(f"(M_full @ X_{step}) + c_full = {M_full @ X + c_full}")
        X_next = M_full @ X + c_full
        print(f"X_{step+1} = {pretty_vector(X_next, names)}")

        # Stabilization check
        if np.allclose(X, X_next):
            print("\n✅ Reached steady state (no further evolution). Halting.")
            X = X_next
            break

        X = X_next

    print("\n====================================")
    print("🏁 FINAL STATE VECTOR")
    print("====================================")
    print(f"X_final = [{pretty_vector(X, names)}]")

    # Interpret final control state
    active_idx = np.argmax(X[:n_ctrl])
    active_block = control_blocks[active_idx]
    print(f"\nActive control block at halt: {active_block}")

    # Print data variables
    print("Final data variables:")
    for i, var in enumerate(data_vars):
        val = X[n_ctrl + i]
        print(f"  {var} = {val}")

    print("====================================\n")


if __name__ == "__main__":
    math_simulator_phasor_verbose("phasor_transformed.json")


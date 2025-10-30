import json
import numpy as np

def run_phasor_simulation(phasor_data, max_steps=1000, verbose=True):
    """
    Simulate execution using the linear phasor system:
        X_{t+1} = M_full @ X_t + c_full
    stopping when constraints in C_p, c_p are violated.
    """
    M_full = np.array(phasor_data["M_full"], dtype=float)
    c_full = np.array(phasor_data["c_full"], dtype=float)
    C_p = np.array(phasor_data["C_p"], dtype=float) if phasor_data["C_p"] else np.zeros((0, M_full.shape[0]))
    c_p = np.array(phasor_data["c_p"], dtype=float) if phasor_data["c_p"] else np.zeros(0)
    total_dim = phasor_data["total_dim"]

    control_blocks = phasor_data["addr_list"]["control_blocks"]
    data_vars = phasor_data["addr_list"]["data_vars"]

    # Initial state vector
    X = np.zeros(total_dim, dtype=float)
    X[0] = 1.0   # Start at init_x (control block 0)

    trajectory = [X.copy()]

    for step in range(max_steps):
        # Check constraints
        if C_p.shape[0] > 0:
            violation = np.any(C_p @ X + c_p > 0)
            if violation:
                if verbose:
                    print(f"⛔ Stopping at step {step} due to constraint violation.")
                break

        # Linear update
        X = M_full @ X + c_full
        trajectory.append(X.copy())

        if verbose:
            ctrl_state = X[:len(control_blocks)]
            data_state = X[len(control_blocks):]
            print(f"Step {step+1}: Control={ctrl_state}, Data={data_state}")

        # If control goes to terminal block (optional)
        if np.allclose(X, trajectory[-2]):
            # steady state reached
            if verbose:
                print(f"✅ Steady state reached at step {step+1}")
            break

    return np.array(trajectory)


if __name__ == "__main__":
    with open("phasor_transformed.json", "r") as f:
        phasor_data = json.load(f)

    traj = run_phasor_simulation(phasor_data, verbose=True)

    print("\nFinal State Vector:", traj[-1])
    print(f"Total Steps Simulated: {len(traj)-1}")


# VPL — Vector Phasor Language

**A mathematical framework and compiler Intermediate Representation (IR) for viewing programs as geometric motion—and compiling software directly into dedicated digital and analog circuits.**

[![License: GPL v3](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE.md)
[![Status: Research & PoC](https://img.shields.io/badge/Status-Research%20%26%20PoC-orange.svg)](#roadmap--demos)


---

## Core Intuition

Why represent computation solely as sequential text instructions on a general-purpose CPU when physical reality operates on vectors, fields, and oscillations?

**Vector Phasor Language (VPL)** models a program as a discrete-time **Vector Evolution Machine (VEM)**:
* **Program State** is a single unified vector combining control flow and data variables in orthogonal subspaces.
* **Loops (`while` / `for`)** are **phasors** ($e^{j\phi}$) rotating through phase states rather than imperative jumps.
* **Conditionals & Neural Activations (e.g., ReLU)** are **geometric hyperplane guards** clamping or redirecting trajectories in state space.
* **Parallelism** emerges naturally whenever the transition operator decomposes into block-diagonal submatrices—requiring no thread schedulers, locks, or operating system overhead.

Once lowered into **VPL IR**, high-level algorithms (such as Fast Fourier Transforms or neural network layers) can be synthesized directly into **Digital RTL (Verilog/FPGA)**, **Analog/Mixed-Signal Circuits (SPICE)**, or future **Quantum Circuits**.

---

## The 5 Governing Equations of VPL

Every VPL IR program is completely defined by the 5-tuple $\mathcal{P} = \langle \mathcal{H}, M, c, \mathcal{G}, P_{\mathrm{halt}} \rangle$:

### 1. Unified State Space Law (Kinematics)

$$
\mathcal{H} = \mathcal{H}_C \oplus \mathcal{H}_D,
\qquad
X(t) = \begin{bmatrix} C(t) \\ D(t) \end{bmatrix}
\in \mathbb{C}^{n_C} \oplus \mathbb{R}^{n_D}
$$

> Control flow $C(t)$ and program variables/tensors $D(t)$ occupy orthogonal subspaces of a single state vector $X(t)$. There is no external program counter or separate memory bus.

### 2. Evolution Law (Dynamics)

$$
X(t+1) = M X(t) + c,
\qquad
M = \begin{bmatrix}
M_{CC} & M_{CD} \\
M_{DC} & M_{DD}
\end{bmatrix}
$$

> Execution advances in discrete steps via a coupled affine operator: $M_{CC}$ drives control transitions, $M_{CD}$ handles data-dependent branching, $M_{DC}$ gates data writes, $M_{DD}$ performs intrinsic arithmetic/matrix multiplication, and $c$ injects constants/biases.

### 3. Phasor Control & Constraint Law (Iteration & Non-Linearity)

$$
C(t) = \sum_{i=1}^{n_C} a_i e^{j\phi_i(t)} e_{c_i},
\qquad
\Phi_{\mathrm{loop}} = \Phi_{\mathrm{cond}} \cdot \Phi_{\mathrm{body}} \cdot \Phi_{\mathrm{back}}
$$

Hyperplane guards are represented by

$$
\mathcal{G}: C_p X(t) + c_p \geq 0.
$$

> Iterative loops are cyclic phase rotations ($e^{j\phi_i}$), enabling spatial unrolling versus temporal folding (time-multiplexing). Non-linearities and branches act as hyperplane guards $\mathcal{G} = (C_p, c_p)$.

### 4. Structural Parallelism Law (Superposition without Threads)

$$
M = \bigoplus_{k=1}^{K} M_k
= \mathrm{diag}(M_1, M_2, \ldots, M_K)
$$

$$
X(t+1) = \sum_{i \in \mathcal{A}(t)} \alpha_i M_i X(t)
$$

> Independent operations decompose into block-diagonal submatrices, synthesizing directly into concurrent physical hardware datapaths.

### 5. Halting & Projection Law (Termination & Readout)

$$
P_{\mathrm{halt}} X(t) \neq 0,
\qquad
M_{CC} e_{\mathrm{halt}} = e_{\mathrm{halt}},
\qquad
Y_{\mathrm{out}} = P_D X(t)
$$

> Computation terminates when $C(t)$ enters an absorbing eigenstate $e_{\mathrm{halt}}$ ($\lambda = 1$), projecting the final result $Y_{\mathrm{out}}$ onto physical output pins.

---

## Compiler Architecture & Hardware Mapping

VPL bridges high-level code (Python / C / C++) and formal mathematics into physical hardware through a 6-stage pipeline:

```text
[ Python / C / Neural Graph ]
             │
             ▼
  1. Extractor & 2. Translator   ──► Lowers AST / computation graph to VPL primitives
             │
             ▼
  3. Expander & 4. Phasor Pass   ──► Builds block-sparse M, folds phasor cycles, permutes block-diagonals
             │
             ▼
       5. VEM Simulator          ──► Verifies X(t+1) = M X(t) + c algebraically
             │
             ▼
     6. Physical Mapping         ──► Emits Digital Verilog (.v) or Analog SPICE (.cir)
```

### Physical Synthesis Mapping

| VPL IR Primitive | Digital RTL (`Verilog` / FPGA) | Analog / Mixed-Signal (`NGSPICE`) |
| :--- | :--- | :--- |
| **State Vector $X(t)$** | Clocked D-Flip-Flop registers | Sample-and-hold capacitors / node voltages |
| **Operator $M_{DD} X + c$** | Combinational DSP multipliers & adder trees | Conductance crossbar ($G = 1/R$) + bias sources |
| **Phasor Control $C(t)$** | One-hot / phase-encoded Finite State Machine | Multi-phase non-overlapping clock generator |
| **Hyperplane Guard $\mathcal{G}$** | Signed comparator + 2:1 multiplexer (ReLU) | Op-amp comparator / precision diode clamp |
| **Block Diagonal $\bigoplus M_k$** | Parallel independent hardware modules | Decoupled analog sub-circuits |
| **Projection $P_{\mathrm{halt}}, P_D$** | `done` status wire + output data bus | Threshold detector + output buffer amplifier |

---

## Quickstart & Demos

### Prerequisites
* **Python 3.10+** with `numpy` (for IR lowering and algebraic VEM simulation)
* *(Optional)* **Icarus Verilog** (`iverilog`) or **Yosys** for digital RTL simulation & FPGA synthesis
* *(Optional)* **NGSPICE** (`ngspice`) for analog circuit waveform verification

### 1. Run the 2-Layer XOR Neural Circuit Demo

Lowers a 2-layer ReLU MLP into the 5-tuple `VPLProgramIR`, verifies the truth table in the algebraic VEM simulator, and emits both Verilog and SPICE netlists:

```bash
python examples/xor_vem.py
```

* **Simulate Digital RTL (Icarus Verilog):**
  ```bash
  iverilog -o build/xor_sim generated/vpl_xor_vem.v && vvp build/xor_sim
  ```
* **Simulate Analog Circuit (NGSPICE):**
  ```bash
  ngspice -b generated/vpl_xor_analog.cir
  ```

### 2. Run the 8-Point Radix-2 FFT Demo

Demonstrates complex phasor twiddle rotations ($W_8^k = e^{-j 2\pi k / 8}$) and block-diagonal butterfly decomposition lowered into VPL IR:

```bash
python examples/fft8_vem.py
```

---

## Repository Structure

```text
VPL/
├── compiler/      # VPL IR dataclasses, AST/graph lowering, phasor optimizer, and Verilog/SPICE emitters
├── examples/      # Runnable PoC scripts (While loop, 8-point FFT, 2-layer XOR neural network)
├── paper/         # Mathematical formalism and proofs for the Vector Evolution Machine (VEM)
├── binnacle/      # Research logs, design notes, and architectural experiments
└── LICENSE.md     # GNU General Public License v3.0
```

---

## Roadmap & Demos

* [x] **Mathematical Foundation:** Vector Evolution Machine (VEM) state space, phasor control, and block-diagonal parallelism (`paper/`).
* [x] **Demo 1 — While Loop:** Basic iterative state evolution in VPL IR.
* [x] **Demo 2 — 2-Layer Neural Network (XOR):** Lowering affine layers + ReLU hyperplane guards into Verilog RTL and NGSPICE netlists.
* [ ] **Demo 3 — Fast Fourier Transform (FFT):** 8-point Radix-2 Cooley-Tukey FFT lowered to FPGA fabric via `Yosys`/`nextpnr`.
* [ ] **Demo 4 — `micrograd` / ONNX Frontend:** Automated ingestion of small trained neural networks with phasor time-multiplexing.
* [ ] **Future — Quantum Backend:** Mapping unitary phasor operators to OpenQASM circuits.

---

## Peer Review & Contributions

This project is actively evolving and open to mathematical and hardware engineering peer review. If you spot edge cases in the formalism, have suggestions for the IR schema, or want to test generated netlists on FPGA/SPICE toolchains, please open an **Issue** or submit a **Merge Request / Pull Request**.

* **Author:** Lucio Guerchi
* **License:** GPL-3.0 (see [LICENSE.md](LICENSE.md))
* *Transparency Note: Parts of the documentation, prototype code, and hardware emission scripts in this repository were drafted with AI assistance under the author's architectural direction.*

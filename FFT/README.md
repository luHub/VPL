# Fast Fourier Transform

## Description

## Compiler

```
C/C++ code
   |
   v
 C Parser (Clang / pycparser)
   |
   v
 AST  ---> Pass 1: Control Flow Extraction
   |
   v
 Intermediate Graph (loops, calls, arrays)
   |
   v
 VPL-IR JSON
   |
   +-- Option A: symbolic operators (Reshape, DFT, Twiddle)
   +-- Option B: expanded matrices for simulation
```

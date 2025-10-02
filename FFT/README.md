# Fast Fourier Transform

## Description

Small demo to evaluate VPL output depending on github public FFT implementations

## Inputs Sources

Small demo using as input https://github.com/jtfell/c-fft Cooley-Tukey FFT algorithm

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

## Contributions

Input from https://github.com/jtfell/c-fft 

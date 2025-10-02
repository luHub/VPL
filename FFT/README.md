# Fast Fourier Transform

## Description

Small demo to evaluate VPL output depending on github public FFT implementations

## Inputs Sources

Small demo using as input Cooley-Tukey FFT algorithm from chatGTP 
Nice small FFT from here https://github.com/lloydroc/arduino_fft/blob/master/fft.c

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

Input from chatGTP
Input from https://github.com/lloydroc/arduino_fft/blob/master/fft.c

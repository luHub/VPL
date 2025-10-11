# VPL (Vector Phasor Language)

VPL is a mathematical framework for seeing programs as geometric motion. The idea comes from a combination of electrical engineering, computer science, and mathematics. For years, I kept coming back to a simple thought: why not vectors? After all, we use them to describe almost everything. Later, when I studied compiler construction, everything was different; it was like watching another movie, but it was a good catch on semantics and linguistics. Still, the idea was in motion. So, how to connect this together? Translating semantics into something else, with some rules, so I start pairing stuff, so if with a "While" you can do almost anything. Let a while be a phasor because both go in circles. Typing well, let's have a Vector space for types, and so on.

With the advent of LLMs, such as ChatGPT, I prototyped something. One advantage of understanding electrical engineering, computer science, and math is that I know exactly what I want, or at least know when something is off.  The speed at which a PoC is quite low or impossible without LLMs; they are here to stay, so we must use them.

There is work to do. For example, math proving by humans, covering more cases in the model, and testing. I think it has a nice way to shift from "code" to "hardware". We need simpler machines once we know what we want; therefore, converting software to hardware sounds promising, especially in terms of performance  and  energy consumption. Finally, another reason is that we need to start reasoning in terms of quantum mechanics, which is already defined in terms of vectors, so it would be tempting to map as much as possible to quantum circuits.

I will evolve this mathematical framework as much as possible, and it is open for peer review.

# VPL as IR

VPL also is an intermediate representation language (IR) between software semantics and physical implementations, you can picture it as a translation tool. In a broad picture, once you cross to another domain you adjust and optimize in that domain as the inputs and outputs remain valid. The final test of this is a physical implementation of a complex software library.

# VPL Toolchain

From the master paper, there are 2 possible inputs one from mathematics formulations to VPL, mathematical translation to VPL or the other one is to 
bridge from highlevel programming to VPL.

Once in VPL, abstract semantics or mathematical formulations become part of the hardware domain. Here is possible to optimize in terms of engineering depending, that could be
electrical, quantic, any other physical representation.

### Limitations

- The tool chain will focus on Electrical Digital and Analog implementations since I need to finish studying Quantum Computing to have a basic understanding what I am doing. 
- Tool chain PoC will focus on small algorithms written in Python, C++, and C. As input.
- According to the master paper general purpose systems are out of scope.    

## The Abstract toolchain

This one is for mathematics and developed as papers with mathematical formulations

## The Bridging toolchain

This one is actual code to produce an intermediate representation and from there create hardware.

# Demo list 

- Fast Fourier Transform: From code to Hardware Implementation

# Peer Reviews

Create a MR with your comments and after review I will create a new version of it

# Contributors

Lucio Guerchi 









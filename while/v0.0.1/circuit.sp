* SPICE netlist auto-generated from VPL phasor representation
.title VPL to SPICE Mapping
Vinit_x init_x 0 DC 0
Vb_s1 b_s1 0 DC 0
Vb_s0 b_s0 0 DC 0
Vb_s2 b_s2 0 DC 0
Vb_s3 b_s3 0 DC 0
Vx x 0 DC 0
* Controlled sources implementing M_full
EBUF0 init_x_next 0 VALUE={ 1.0*V(b_s1) }
EBUF1 b_s1_next 0 VALUE={ 1.0*V(b_s0) + 1.0*V(b_s2) }
EBUF2 b_s0_next 0 VALUE={ 1.0*V(b_s1) }
EBUF3 b_s2_next 0 VALUE={ 1.0*V(b_s3) }
EBUF4 b_s3_next 0 VALUE={ 0 }
EBUF5 x_next 0 VALUE={ 1.0*V(x) + (2.0) }
* Phasor halting condition
* Halting when: 1.0*V(x) + (-5.0) = 0
* Time stepping
VCLK clk 0 PULSE(0 1 0 1n 1n 1u 2u)
.control
tran 1u 50u
plot V(x)
.endc
.end
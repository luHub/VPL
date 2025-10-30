module vpl_loop(input clk, input reset, output reg halt);

  reg [31:0] x;

  wire [31:0] next_x;

  wire halt_cond;
  assign next_x = x + 2;

  assign halt_cond = (x + -5) >= 0;

  always @(posedge clk or posedge reset) begin
    if (reset) begin
      x <= 0;
      halt <= 0;
    end else if (!halt) begin
      if (halt_cond) begin
        halt <= 1;
      end else begin
        x <= next_x;
      end
    end
  end
endmodule
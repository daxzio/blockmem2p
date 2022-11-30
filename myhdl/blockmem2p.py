from myhdl import *

@block
def blockmem2p(
    clka,
    ena,
    wea,
    addra,
    dina,
    clkb,
    enb,
    addrb,
    doutb,
    depth=32,
):

    #mem2p.verilog_code = \
   # """
#(* ram_style = "block" *)
    #"""    

    f_doutb    = [Signal(intbv(0)[len(dina):]) for i in range(depth)]   

    #mem2p.vhdl_code = \
    #"""
    #attribute ram_style : string;
    #attribute ram_style of $f_doutb : signal is "block";
    #"""

    @always(clka.posedge)
    def write():
        if ena:
            f_doutb[addra].next = f_doutb[addra]
            for i in range(len(wea)):
                if wea[i]:
                    f_doutb[addra].next[8*i:8] = dina[8*i:8]                    

    @always(clkb.posedge)
    def read():
        if enb:
            doutb.next = f_doutb[addrb]

    return write, read

#!/bin/env python
from myhdl import *
from blockmem2p import blockmem2p
import math

@block
def tb_blockmem2p():
    
    width = 32
    depth = 1024
    addra_width = math.ceil(math.log2(depth))
    addrb_width = math.ceil(math.log2(depth))
    wea_width = math.ceil(width/8)

    clka  = Signal(bool(0))
    ena   = Signal(bool(0))
    wea   = Signal(intbv(0)[wea_width:])
    addra = Signal(intbv(0)[addra_width:])
    dina  = Signal(intbv(0)[width:])
    clkb  = Signal(bool(0))
    enb   = Signal(bool(0))
    addrb = Signal(intbv(0)[addrb_width:])
    doutb = Signal(intbv(0)[width:])

        
    module = blockmem2p(
        clka,
        ena,
        wea,
        addra,
        dina,
        clkb,
        enb,
        addrb,
        doutb,
        depth,
    )

    #module.convert(hdl='VHDL')
    module.convert(hdl='Verilog', initial_values=True)
 
    return module 


def simulate(timesteps):

    tb = tb_blockmem2p()
    #tb.config_sim(trace=True)
    #tb.run_sim(timesteps)


simulate(2000)

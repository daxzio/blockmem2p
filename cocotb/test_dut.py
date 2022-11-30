import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotbext.uart import Mem2PDriver


class testbench:
    def __init__(self, clka, clkb, reset, reset_sense=0):
        self.clka = clka
        self.clkb = clkb
        self.reset = reset
        self.reset_sense = reset_sense

    async def wait_clkn(self, length=1):
        for i in range(length):
            await RisingEdge(self.clka)

    async def start_test(self, period=7, units="ns"):
        cocotb.start_soon(Clock(self.clka, period, units=units).start())
        cocotb.start_soon(Clock(self.clkb, 11, units=units).start())
 
        self.reset.setimmediatevalue(self.reset_sense)
        await self.wait_clkn(20)
        self.reset.value = 1    
        await self.wait_clkn(5)

    async def end_test(self, length=10):
        await self.wait_clkn(length)



@cocotb.test()
async def test_dut_simple(dut):
    
    tb = testbench(dut.clka, dut.clkb, dut.resetn)
    mem0 = Mem2PDriver(dut.clka, dut.ena, dut.wea, dut.addra, dut.dina, dut.clkb, dut.enb, dut.addrb, dut.doutb)

    await tb.start_test()
    
    await mem0.write(0x0000, 0x1234, 0xf)
    await mem0.write(0x0001, 0x5678, 0xf)

    await mem0.read(0x0000, 0x1234)
    await mem0.read(0x0001, 0x5678)
    
    await tb.wait_clkn(10)
   
    await mem0.write(0x0000, 0xabcf, 0x1) 
    await mem0.read(0x0000, 0x12cf)   
        
    await mem0.write(0x0001, 0xabcf, 0x2)
    await mem0.read(0x0001, 0xab78)   
 
    for j in range(4):
        for i in range(1024):
            await mem0.write() 
        for i in range(1024):    
            await mem0.read() 

    await tb.end_test()


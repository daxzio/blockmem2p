import logging
import random
import warnings
import cocotb
from cocotb.queue import Queue
from cocotb.triggers import Event, RisingEdge
     
class Mem2PDriver:
    
    def __init__(self, clka, ena, wea, addra, dina, clkb, enb, addrb, doutb, *args, **kwargs):
        self.log = logging.getLogger(f"cocotb.mem2p")
        self.log.level = logging.DEBUG
        self._clka = clka        
        self._ena = ena       
        self._wea = wea       
        self._addra = addra       
        self._dina = dina        
        self._clkb = clkb       
        self._enb = enb       
        self._addrb = addrb       
        self._doutb = doutb   
        self.din_mask = 2**len(self._dina)-1
        self.mask = 2**len(self._wea)-1
        

        self.log.debug("Setup Mem2P Configuration")
        self.log.debug(f"  Write Memory Width: {len(self._dina)}")
        self.log.debug(f"  Write Memory Depth: {2**len(self._addra)}")
        self.log.debug(f"  Read Memory Width:  {len(self._doutb)}")
        self.log.debug(f"  Read Memory Depth:  {2**len(self._addrb)}")
        
        self.mem_array = []
        for i in range(2**len(self._addra)):
            self.mem_array.append(0)
        
        self.wractive = False
        self.wrqueue = Queue()
        self.rdactive = False
        self.rdqueue = Queue()

        self._wridle = Event()
        self._wridle.set()
        self._rdidle = Event()
        self._rdidle.set()

        self._wrrun_cr = None
        self._rdrun_cr = None
        self._restart()

    def _restart(self):
        if self._wrrun_cr is not None:
            self._wrrun_cr.kill()
        self._wrrun_cr = cocotb.start_soon(self._wrrun())
        if self._rdrun_cr is not None:
            self._rdrun_cr.kill()
        self._rdrun_cr = cocotb.start_soon(self._rdrun())

    @property
    def doutb(self):
        return int(str(self._doutb.value), 2)
        
    def wrempty(self):
        return self.wrqueue.empty()

    def rdempty(self):
        return self.rdqueue.empty()
    
    def mask_entend(self, wea):
        mask = 0
        i = 0
        while not 0 == wea:
            if 1 == (wea & 0x1):
                mask |= 0xff << (i*8)
            wea = wea >> 1
            i += 1
        
        return mask

    async def _wrrun(self):
        self.wractive = False
        
        while True:
            await RisingEdge(self._clka)

            
            if self.wrempty():
                self.wractive = False
                self._wridle.set()
                self._addra.value = 0x0
                self._dina.value = 0x0
                self._ena.value = 0
                self._wea.value = 0
            else:
                self.wractive = True
                addr, data, wea = await self.wrqueue.get()
                self._addra.value = addr
                self._dina.value = data
                self._ena.value = 1
                self._wea.value = wea & self.mask
                mem_mask = self.mask_entend(wea & self.mask)
                self.mem_array[addr] = ((self.mem_array[addr] & ~mem_mask) | (data & mem_mask)) & self.din_mask
                self.log.info(f"Write Mem2p 0x{addr:04x}: 0x{data:04x}")

    
    async def _rdrun(self):
        self.rdactive = False
        
        self.check_read = None
        self.check_read_dly = None
        self.addr_dly1 = None
        self.addr_dly0 = None
        
        while True:
            await RisingEdge(self._clkb)
           
            if not self.check_read_dly is None and not self.doutb == self.check_read_dly:
                msg = f"Incorrect value returned, 0x{self.doutb:04x} 0x{self.check_read_dly:04x}"
                self.log.error(msg)
                warnings.simplefilter("ignore", category=FutureWarning)
                raise Exception(msg)
             
            if not self.addr_dly1  is None and not self.doutb == self.mem_array[self.addr_dly1] :
                msg = f"Incorrect value returned, 0x{self.addr_dly1:04x}"
                self.log.error(msg)
                warnings.simplefilter("ignore", category=FutureWarning)
                raise Exception(msg)
           
            self.check_read_dly = self.check_read
            self.check_read = None
            self.addr_dly1 = self.addr_dly0
            self.addr_dly0 = None
            if self.rdempty():
                self.rdactive = False
                self._rdidle.set()
                self._addrb.value = 0
                self._enb.value = 0
            else:
                self.rdactive = True
                addr, data = await self.rdqueue.get()
                self._addrb.value = addr
                self._enb.value = 1

                if data is None:
                    self.log.info(f"Read Mem2p 0x{addr:04x}: 0x{self.mem_array[addr]:04x}")
                    self.addr_dly0 = addr
                else:
                    self.log.info(f"Read Mem2p 0x{addr:04x}: 0x{data:04x}")
                    self.check_read = data
    
    async def write(self, addr=None, data=None, wea=None):
        if addr is None:
            addr = random.randint(0x0, 2**len(self._addra)-1)
        if data is None:
            data = random.randint(0x0, self.din_mask)
        if wea is None:
            wea = random.randint(0x0, 0xffffffff)
        await self.wrqueue.put([addr, data, wea])
        await RisingEdge(self._clka)
        self._wridle.clear()
        return data
    
    def write_nowait(self, addr=None, data=None, wea=None):
        if data is None:
            data = random.randint(0x0, self.din_mask)
        self.wrqueue.put_nowait([addr, data, wea])
        self._wridle.clear()
        return data
            
    async def read(self, addr=None, data=None):
        if addr is None:
            addr = random.randint(0x0, 2**len(self._addra)-1)
        await self.rdqueue.put([addr, data])
        await RisingEdge(self._clkb)
        self._rdidle.clear()

    def read_nowait(self, addr=0x0000, data=None):
        self.rdqueue.put_nowait([addr, data])
        self._rdidle.clear()


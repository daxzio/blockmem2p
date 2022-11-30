SIM ?= icarus
TOPLEVEL_LANG = verilog
VERILOG_SOURCES = \
    ./dut.sv 

ifeq ($(SRC), myhdl)
    VERILOG_SOURCES += \
        ../myhdl/blockmem2p.v 
else
    VERILOG_SOURCES += \
        ../verilog/blockmem2p.sv 
endif
   
TOPLEVEL = dut
MODULE = test_dut


include $(shell cocotb-config --makefiles)/Makefile.sim

waves:
	simvision -waves dut.vcd &
    
clean::
	rm -rf __pycache__/ .simvision/ .Xil/ results.xml *.trn *.dsn vivado* *.vcd core*

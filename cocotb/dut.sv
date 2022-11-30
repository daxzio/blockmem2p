module dut (
     clka
    ,resetn
    ,ena
    ,wea
    ,addra
    ,dina
    ,clkb
    ,enb
    ,addrb
    ,doutb
    );
    
    parameter  integer G_MEMWIDTH  = 32;
    parameter  integer G_MEMDEPTH  = 1024;
    parameter          G_INIT_FILE = "" ;
    localparam integer G_ADDRWIDTH = $clog2(G_MEMDEPTH);
    localparam integer G_WEWIDTH   = ((G_MEMWIDTH-1)/8)+1;

    input                    clka;
    input                    resetn;
    input                    ena;
    input  [G_WEWIDTH-1:0]   wea;
    input  [G_ADDRWIDTH-1:0] addra;
    input  [G_MEMWIDTH-1:0]  dina;
    input                    clkb;
    input                    enb;
    input  [G_ADDRWIDTH-1:0] addrb;
    output [G_MEMWIDTH-1:0]  doutb;
        
    
    blockmem2p 
    //#(
    //    .G_MEMWIDTH  (G_MEMWIDTH),
    //    .G_MEMDEPTH  (G_MEMDEPTH)
    //)    
    i_blockmem_2p (
        .*
    );

    `ifdef COCOTB_SIM
    initial begin
        $dumpfile ("dut.vcd");
        $dumpvars (0, dut);
        /* verilator lint_off STMTDLY */
        #1;
        /* verilator lint_on STMTDLY */
    end
    `endif    


endmodule


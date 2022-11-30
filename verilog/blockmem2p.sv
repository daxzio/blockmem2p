module blockmem2p (
     clka
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
    input                    ena;
    input  [G_WEWIDTH-1:0]   wea;
    input  [G_ADDRWIDTH-1:0] addra;
    input  [G_MEMWIDTH-1:0]  dina;
    input                    clkb;
    input                    enb;
    input  [G_ADDRWIDTH-1:0] addrb;
    output [G_MEMWIDTH-1:0]  doutb;

    (* ram_style = "block" *) reg [G_MEMWIDTH-1:0] f_ram [G_MEMDEPTH-1:0];
    //(* ram_style = "block" *) reg [G_MEMWIDTH-1:0] f_ram [G_MEMDEPTH];
    reg [G_MEMWIDTH-1:0] f_doutb;

    initial begin
        // synthesis translate_off
        for(integer x=0; x<G_MEMDEPTH; x=x+1) begin
            f_ram[x] = 0;
        end
        // synthesis translate_on
        if (G_INIT_FILE != "") begin
            $readmemh(G_INIT_FILE, f_ram);
        end
    end
    
    always @(posedge clka) begin
        integer i;
        if (ena) begin
            for (i=0; i<G_WEWIDTH; i=i+1) begin
                if (wea[i]) begin
                    f_ram[addra][(8 * i)+:8] <= dina[(8 * i)+:8];
                end
            end
        end
    end

    always @(posedge clkb) begin
        // synthesis translate_off
        f_doutb <= 0;
        // synthesis translate_on
        if (enb)
            f_doutb <= f_ram[addrb];
    end
    assign doutb = f_doutb;

endmodule


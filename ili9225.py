# ili9225.py by YouMakeTech
# MicroPython ILI9225 2.2" 176x220 TFT LCDdriver, SPI interface

from micropython import const
from machine import Pin, PWM, SPI
import framebuf
from time import sleep


# register definitions


# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class ILI9225(framebuf.FrameBuffer):
    def __init__(self, width=220, height=176, id_=0, clk=18, sdi=19,
                 rs=20, rst=21, cs=17, led=22, baudrate=32000000):
        self.width = width
        self.height = height
        # self.spi = SPI(id_, bits=16, sck=Pin(clk), mosi=Pin(sdi), baudrate=baudrate, polarity=0, phase=0, firstbit=SPI.MSB)
        self.spi = SPI(id_, sck=Pin(clk), mosi=Pin(sdi), baudrate=baudrate, polarity=0, phase=0)
        self.rs = Pin(rs, Pin.OUT)
        self.rst = Pin(rst, Pin.OUT)
        self.cs = Pin(cs, Pin.OUT)
        self.led = Pin(led, Pin.OUT)

        self.buffer = memoryview(bytearray(self.height * self.width * 2))
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        
        self.init_display()
        
    def write_cmd(self, cmd=None, data=None):
        self.cs(0)
        if cmd:
            self.rs(0) # command mode
            msb=((cmd & 0xFF00) >> 8).to_bytes(1,'big')
            lsb=(cmd & 0x00FF).to_bytes(1,'big')
            self.spi.write(msb)
            self.spi.write(lsb)
            #print("cmd="+str(msb)+str(lsb))
            
        if data:
            self.rs(1) # data mode
            msb=((data & 0xFF00) >> 8).to_bytes(1,'big')
            lsb=(data & 0x00FF).to_bytes(1,'big')
            self.spi.write(msb)
            self.spi.write(lsb)
            #print("data="+str(msb)+str(lsb))
        self.cs(1)

    def init_display(self):
        
        # Initial values
        self.rst.value(0)
        self.rs.value(0)
        self.cs.value(0)
        sleep(0.150)
        
        # Hardware reset
        self.rst.value(1)
        sleep(0.150)
        self.rst.value(0)
        sleep(0.150)
        self.rst.value(1)
        sleep(0.050)
        
        # Turn backlight off initially
        self.led.value(0) 
        
        # START Initial Sequence
        self.write_cmd(0x10,0x0000)
        self.write_cmd(0x11,0x0000)
        self.write_cmd(0x12,0x0000)
        self.write_cmd(0x13,0x0000)
        self.write_cmd(0x14,0x0000)
        sleep(0.040)
        self.write_cmd(0x11,0x0018)
        self.write_cmd(0x12,0x6121)
        self.write_cmd(0x13,0x006F)
        self.write_cmd(0x14,0x495F)
        self.write_cmd(0x10,0x0800)
        sleep(0.010)
        self.write_cmd(0x11,0x103B)
        sleep(0.050)
        self.write_cmd(0x01,0x011C)
        self.write_cmd(0x02,0x0100)
        self.write_cmd(0x03,0x1038)
        self.write_cmd(0x07,0x0000)
        self.write_cmd(0x08,0x0808)
        self.write_cmd(0x0B,0x1100)
        self.write_cmd(0x0C,0x0000)
        self.write_cmd(0x0F,0x0D01)
        self.write_cmd(0x15,0x0020)
        self.write_cmd(0x20,0x0000)
        self.write_cmd(0x21,0x0000)
        
        self.write_cmd(0x30,0x0000)
        self.write_cmd(0x31,0x00DB)
        self.write_cmd(0x32,0x0000)
        self.write_cmd(0x33,0x0000)
        self.write_cmd(0x34,0x00DB)
        self.write_cmd(0x35,0x0000)
        self.write_cmd(0x36,0x00AF)
        self.write_cmd(0x37,0x0000)
        self.write_cmd(0x38,0x00DB)
        self.write_cmd(0x39,0x0000)
        
        self.write_cmd(0x50,0x0000)
        self.write_cmd(0x51,0x0808)
        self.write_cmd(0x52,0x080A)
        self.write_cmd(0x53,0x000A)
        self.write_cmd(0x54,0x0A08)
        self.write_cmd(0x55,0x0808)
        self.write_cmd(0x56,0x0000)
        self.write_cmd(0x57,0x0A00)
        self.write_cmd(0x58,0x0710)
        self.write_cmd(0x59,0x0710)
        
        self.write_cmd(0x07,0x0012)
        sleep(0.050)
        self.write_cmd(0x07,0x1017)
        # END Initial Sequence

        self.fill(0)
        self.show()
        sleep(0.050)
        
        # Turn on backlight
        self.led.value(1)

    def power_off(self):
        pass

    def power_on(self):
        pass

    def contrast(self, contrast):
        pass

    def invert(self, invert):
        pass

    def rotate(self, rotate):
        pass

    def show(self):
        self.write_cmd(0x03,0x1018) # Entry Mode: Vertical, Horizontal=Increment, Vertical=Decrement
        self.write_cmd(0x36,0xAF)   # "Horizontal" End = 175 = 0xAF
        self.write_cmd(0x37,0x00)   # "Horizontal" Start = 0
        self.write_cmd(0x38,0xDB)   # "Vertical" End = 219 = 0xDB
        self.write_cmd(0x39,0x00)   # "Vertical" Start = 0
        
        self.write_cmd(0x20,0xAF)   # RAM Address Set
        self.write_cmd(0x21,0x00)   # RAM Address Set
        
        self.write_cmd(0x22, None)  # Write Data to GRAM
        self.cs(0)
        self.rs(1) # data mode
        self.spi.write(self.buffer)
        self.cs(1)
    
    def color(r, g, b):
        """
        color(r, g, b) returns a 16 bits integer color code for the ST7789 display


        where:
            r (int): Red value between 0 and 255
            g (int): Green value between 0 and 255
            b (int): Blue value between 0 and 255
        """
        # rgb (24 bits) -> rgb565 conversion (16 bits)
        # rgb = r(8 bits) + g(8 bits) + b(8 bits) = 24 bits
        # rgb565 = r(5 bits) + g(6 bits) + b(5 bits) = 16 bits
        r5 = (r & 0b11111000) >> 3
        g6 = (g & 0b11111100) >> 2
        b5 = (b & 0b11111000) >> 3
        rgb565 = (r5 << 11) | (g6 << 5) | b5
        
        # swap LSB and MSB bytes before sending to the screen
        lsb = (rgb565 & 0b0000000011111111)
        msb = (rgb565 & 0b1111111100000000) >> 8
        
        return ((lsb << 8) | msb)
    
    def load_image(self,filename):
        open(filename, "rb").readinto(self.buffer)

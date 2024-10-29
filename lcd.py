from machine import Pin
from time import sleep_us, sleep_ms
import asyncio

# LCD command constants
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# Flags for display entry mode
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTDECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_CURSORON = 0x02
LCD_BLINKON = 0x01

# Flags for function set
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_5x8DOTS = 0x00

class LCD1602:
    def __init__(self, rs, enable, d4, d5, d6, d7):
        self.rs = Pin(rs, Pin.OUT)
        self.enable = Pin(enable, Pin.OUT)
        
        # Data pins
        self.data_pins = [
            Pin(d4, Pin.OUT),
            Pin(d5, Pin.OUT),
            Pin(d6, Pin.OUT),
            Pin(d7, Pin.OUT)
        ]
        
        # LCD settings
        self.display_function = LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS
        self.display_control = LCD_DISPLAYON
        self.display_mode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        
        self.num_lines = 2
        self.init_lcd()

    def init_lcd(self):
        # Initialize 4-bit mode
        sleep_ms(50)
        self.write4bits(0x03)
        sleep_ms(5)
        self.write4bits(0x03)
        sleep_us(150)
        self.write4bits(0x03)
        self.write4bits(0x02)  # Set to 4-bit mode
        
        # Function set
        self.command(LCD_FUNCTIONSET | self.display_function)
        
        # Display control
        self.display()
        
        # Clear display
        self.clear()
        
        # Entry mode set
        self.command(LCD_ENTRYMODESET | self.display_mode)
        
    def clear(self):
        self.command(LCD_CLEARDISPLAY)
        sleep_ms(2)

    def home(self):
        self.command(LCD_RETURNHOME)
        sleep_ms(2)

    def set_cursor(self, col, row):
        row_offsets = [0x00, 0x40]
        if row > 1:
            row = 1
        self.command(LCD_SETDDRAMADDR | (col + row_offsets[row]))

    def display(self):
        self.display_control |= LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self.display_control)

    def no_display(self):
        self.display_control &= ~LCD_DISPLAYON
        self.command(LCD_DISPLAYCONTROL | self.display_control)

    def cursor(self):
        self.display_control |= LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self.display_control)

    def no_cursor(self):
        self.display_control &= ~LCD_CURSORON
        self.command(LCD_DISPLAYCONTROL | self.display_control)

    def blink(self):
        self.display_control |= LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self.display_control)

    def no_blink(self):
        self.display_control &= ~LCD_BLINKON
        self.command(LCD_DISPLAYCONTROL | self.display_control)

    def command(self, value):
        self.send(value, 0)

    def write(self, value):
        self.send(value, 1)

    def send(self, value, mode):
        self.rs.value(mode)
        self.write4bits(value >> 4)
        self.write4bits(value)

    def pulse_enable(self):
        self.enable.value(0)
        sleep_us(1)
        self.enable.value(1)
        sleep_us(1)
        self.enable.value(0)
        sleep_us(100)

    def write4bits(self, value):
        for i in range(4):
            self.data_pins[i].value((value >> i) & 0x01)
        self.pulse_enable()

    def write_string(self, text):
        for char in text:
            self.write(ord(char))

    def scroll_text(self, text, row, num_scrolls=1, delay=300):
        if row >= self.num_lines:
            row = self.num_lines - 1

        # Pad the text with spaces to create a smooth scrolling effect
        padded_text = text + " " * 16

        for _ in range(num_scrolls):
            for i in range(len(text)):
                # Clear the line
                self.set_cursor(0, row)
                self.write_string(" " * 16)

                # Write the current portion of the text
                self.set_cursor(0, row)
                self.write_string(padded_text[i:i+16])

                # Wait before scrolling to the next position
                sleep_ms(delay)

        # Clear the line after scrolling is complete
        self.set_cursor(0, row)
        self.write_string(" " * 16)
    async def scroll_text_async(self, text, row, num_scrolls=1, delay=300):
        if row >= self.num_lines:
            row = self.num_lines - 1

        # Pad the text with spaces to create a smooth scrolling effect
        padded_text = text + " " * 16

        for _ in range(num_scrolls):
            for i in range(len(text)):
                # Clear the line
                self.set_cursor(0, row)
                self.write_string(" " * 16)

                # Write the current portion of the text
                self.set_cursor(0, row)
                self.write_string(padded_text[i:i+16])

                # Wait before scrolling to the next position
                await asyncio.sleep_ms(delay)

        # Clear the line after scrolling is complete
        self.set_cursor(0, row)
        self.write_string(" " * 16)
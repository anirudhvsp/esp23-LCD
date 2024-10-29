import network
import time
import requests
from machine import Pin, SPI, PWM, RTC
from lcd import LCD1602
import ntptime
import socket
import asyncio

# Set D23 and D22 pins to low
#Pin(23, Pin.OUT).value(0)
#Pin(22, Pin.OUT).value(0)

pwm = PWM(Pin(4))
pwm.freq(1000)  # Set PWM frequency to 1kHz
pwm.duty(int(100 / 255 * 1023))

lcd = LCD1602(rs=13, enable=27, d4=26, d5=25, d6=33, d7=32)  # Update pins as needed
lcd.clear()
lcd.set_cursor(0, 0)
lcd.write_string("Hello, World!")
time.sleep(1)
lcd.clear()
# Wi-Fi credentials
SSID = "**"
PASSWORD = "**"

def get_text():
    url = "<lambda url>"
    try:
        response = requests.get(url)
        joke = ' | '.join(response.text.strip().split('\n'))
        return joke
    except Exception as e:
        return f"Error fetching joke: {str(e)}"

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    lcd.set_cursor(0, 0)
    lcd.write_string("Connecting...")
    time.sleep(1)
    lcd.clear()
    # Wait for connection
    print("Connecting to Wi-Fi...")
    dots = "."
    while not wlan.isconnected():
        time.sleep(1)
        # Display increasing dots while connecting
        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.write_string(dots)
        if len(dots) < 16:  # Limit to 16 characters (LCD width)
            dots += "."
        else:
            dots = "."
        print("Still connecting...")

    print("Connected to Wi-Fi!")
    print("Network config:", wlan.ifconfig())
    
    lcd.set_cursor(0, 0)
    lcd.write_string("Connected")
    time.sleep(1)
    lcd.clear()

    return wlan.ifconfig()[0]

def get_date():
    try:
        print("Syncing time with NTP server...")
        ntptime.settime()
        print("NTP sync successful")
        rtc = RTC()
        
        # Adjust for IST (UTC+5:30)
        current_time = list(rtc.datetime())
        current_time[4] += 5  # Add 5 hours
        current_time[5] += 30  # Add 30 minutes
        
        # Handle overflow
        if current_time[5] >= 60:
            current_time[4] += 1
            current_time[5] -= 60
        if current_time[4] >= 24:
            current_time[4] -= 24
            current_time[2] += 1  # Increment day
        
        # Update RTC with IST
        rtc.datetime(tuple(current_time))
        
        print(f"Current IST date and time: {current_time}")
        return "{:02d}/{:02d} {:02d}:{:02d}".format(current_time[2], current_time[1], current_time[4], current_time[5])  # DD/MM HH:MM format
    except Exception as e:
        print(f"Error getting IST date and time: {str(e)}")
        return "Date Time Error"

async def display_text(lcd):
    while True:
        joke = get_text()
        await lcd.scroll_text_async(joke, row=1, num_scrolls=3, delay=500)  # Wait 10 seconds before fetching a new joke


async def update_clock(lcd):
    while True:
        rtc = RTC()
        current_time = rtc.datetime()
        time_str = "{:02d}:{:02d}:{:02d} {:02d}-{:02d}".format(
            current_time[4], current_time[5], current_time[6],
            current_time[2], current_time[1]
        )
        lcd.set_cursor(0, 0)
        lcd.write_string(time_str)
        await asyncio.sleep(1)

async def main():
    connect_to_wifi()
    print("Getting date...")
    get_date()  # We still call this to ensure time is synced

    lcd.clear()
    
    clock_task = asyncio.create_task(update_clock(lcd))
    joke_task = asyncio.create_task(display_text(lcd)) # IP is no longer needed here

    await asyncio.gather(clock_task, joke_task)

# Run the event loop
asyncio.run(main())

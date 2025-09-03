"""
display.py - module for controlling TFT display connected to Raspberry Pi via SPI bus.
It shows menu with all functions of the toy and dinamically adds Stop button when
module is started. It also display sleep and processing screens and wraps and scroll
text.
"""

import time # Standard Python library for working with time 
import board, digitalio # Libraries for working with digital I/O pins and simplifying it
from PIL import Image, ImageDraw, ImageFont # Library for working with imges and drawing text and graphics
import adafruit_rgb_display.ili9341 as ili9341  # Library for controlling ILI9341 display via SPI
import config # Module with global settings and variables shared between all parts of the system

# DSPI bus initialization
spi = board.SPI() 
cs_pin = digitalio.DigitalInOut(board.D8) # Chip Select pin for SPI communication
dc_pin = digitalio.DigitalInOut(board.D27) # Data/Command pin
reset_pin = digitalio.DigitalInOut(board.D25) # Reset pin for screen

# Initialization of TFT display
display = ili9341.ILI9341(spi, cs=cs_pin, dc=dc_pin, rst=reset_pin, rotation=90)
WIDTH, HEIGHT = 320, 240 # Display resolution

# Font setup
try:
    # Loading font from system
    fontL = ImageFont.truetype("/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf", 32)
    fontM = ImageFont.truetype("/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf", 24)
    fontS = ImageFont.truetype("/usr/share/fonts/truetype/quicksand/Quicksand-Regular.ttf", 18)
except:
    # Loading default PIL font if try part failes
    fontL = fontM = fontS = ImageFont.load_default()

# Screen menu items
menu_items = ["Story Time", "Take a Picture", "Play a Song", "Fun Facts", "Sleep"]

# Function for drawing Stop button
def draw_stop_button(draw):
    y = HEIGHT - 50
    draw.rectangle((10, y, 310, y + 40), outline="black", fill="red") # Red button color 
    draw.text((120, y + 8), "STOP", fill="black", font=fontM)
    config.stop_button = (10, y, 310, y + 40)

# Function for wrapping long text
def wrap_text(text, font, max_width, draw):
    lines = []
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if font.getlength(test_line) <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)
    return lines

# Clearing screen bz filling it black
def clear_screen():
    image = Image.new("RGB", (WIDTH, HEIGHT), "black")
    display.image(image)

# Function for sleep screen
def draw_sleep_screen():
    config.STATE = "sleep"
    image = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(image)

    text = "Hello! Say Wake Up Teddy to wake me up."
    lines = wrap_text(text, fontL, WIDTH - 40, draw)

    y = 60
    for line in lines:
        draw.text((20, y), line, font=fontL, fill="pink")
        bbox = fontL.getbbox(line)
        height = bbox[3] - bbox[1]
        y += height + 5

    display.image(image)

# Function for drawing menu
def draw_menu():
    """
    Draws main menu with buttons for each toy function.
    """
    config.STATE = "menu"
    image = Image.new("RGB", (WIDTH, HEIGHT), "pink")
    draw = ImageDraw.Draw(image)

    for i, item in enumerate(menu_items):
        y = 10 + i * 40
        draw.rectangle((10, y, 310, y + 40), outline="#2B1C35", fill="#FFD8DC", width=3)
        draw.text((20, y + 8), item, font=fontM, fill="black", stroke_width=int(1))

    # Draw shutdown button as last menu item
    y = 10 + len(menu_items) * 40
    draw.rectangle((10, y, 310, y + 25), outline="black", fill="red", width=3)
    draw.text((20, y + 2), "SHUTDOWN", font=fontS, fill="white", stroke_width=int(1))
    config.shutdown_button = (10, y, 310, y + 25)

    display.image(image)

# Function for displaying messages
def show_message(text, delay=2):
    config.STATE = "processing"
    
    image = Image.new("RGB", (WIDTH, HEIGHT), "blue")
    draw = ImageDraw.Draw(image)
    
    # Set max width for the text area
    max_text_width = WIDTH - 20  # add padding
    lines = wrap_text(text, fontL, max_text_width, draw)
    
    # Calculate total text height
    line_height = fontL.getbbox("A")[3] - fontL.getbbox("A")[1] + 4  # 4px padding between lines
    total_text_height = line_height * len(lines)
    start_y = (HEIGHT - total_text_height) // 2
    
    for i, line in enumerate(lines):
        y = start_y + i * line_height
        draw.text((10, y), line.strip(), font=fontL, fill="white", stroke_width=int(1))

    display.image(image)
    time.sleep(delay)

    # Return to menu after recognized wake word
    if config.WAKE_FLAG and config.STATE != "sleep":
        draw_menu()
        STATE = "menu"

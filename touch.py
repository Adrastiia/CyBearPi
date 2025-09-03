"""
touch.py - module for handling touch input on display.
It manages all touch interaction including reading raw touch coordinates
from touch controller via SPI, mapping raw values to screen coordinates,
detecting button presses for menu items and stop button, triggering toy
features, running listener loop for continuous touch detection and waking
the toy from sleep with a touch.
"""

import os # Here used for shutting down Raspberry Pi
import time # Standard Python library for working with time 
import numpy as np # For mapping touch coordinates with interpolation
import RPi.GPIO as GPIO # Python module for controlling GPIO pins
import spidev # For SPI communication with touch controller
from display import WIDTH, HEIGHT, menu_items, draw_sleep_screen, draw_menu # Module for drawing on display
import config # Module with global settings and variables shared between all parts of the system
from camera import take_photo # Function for taking and saving photographs
from song import play_song # Function for reproduction of random song from local folder
from story import story_time # Function for telling story from API or local file
from funfact import fun_fact # Function for telling fun facts from API or local file
from tts import speak # Module for converting text to speech with espeak

# Touch setup
T_IRQ = 24 # GPIO pin for touch interrupt
GPIO.setmode(GPIO.BCM)
GPIO.setup(T_IRQ, GPIO.IN)

# SPI setup for touch controller
spi_touch = spidev.SpiDev()
spi_touch.open(0, 1)
spi_touch.max_speed_hz = 1000000

# Function for getting raw coordinates from touch controller
def get_touch():
    if GPIO.input(T_IRQ) == 0:
        rx = spi_touch.xfer2([0xD0, 0, 0])  # Raw X coordinate
        x = ((rx[1] << 8) | rx[2]) >> 3
        ry = spi_touch.xfer2([0x90, 0, 0])  # Raw Y coordinate
        y = ((ry[1] << 8) | ry[2]) >> 3
        # Swaping X and Y because of 90-degree screen rotation
        return y, x
    return None

# Function for mapping raw touch coordinates to calibrated screen coordinates
def map_touch_to_screen(x, y):
    # Calibrated raw touch boundaries
    raw_x_min, raw_x_max = 300, 3800
    raw_y_min, raw_y_max = 240, 3900

    # Fliping X axis and scaling raw values
    screen_x = int(np.interp(x, [raw_x_min, raw_x_max], [WIDTH, 0]))
    screen_y = int(np.interp(y, [raw_y_min, raw_y_max], [0, HEIGHT]))

    # For avoiding values getting outside screen
    screen_x = max(0, min(WIDTH - 1, screen_x))
    screen_y = max(0, min(HEIGHT - 1, screen_y))
    return screen_x, screen_y

# Function for handling touch event
def handle_touch(x_raw, y_raw):
    """
    Handles touch event by mapping coordinates and performing corresponding action.
    Checks menu, shutdown button and STOP button and ignores other touches when busy.
    """
    x, y = map_touch_to_screen(x_raw, y_raw)
    print(f"Touch at screen coords: x={x}, y={y}")

    # Check shutdown button in menu screen
    if config.STATE == "menu" and hasattr(config, "shutdown_button"):
        x0, y0, x1, y1 = config.shutdown_button
        if x0 <= x <= x1 and y0 <= y <= y1:
            print("Shutdown button pressed")
            speak("Shutting down. See you later!")
            time.sleep(2)
            GPIO.cleanup()
            os.system("sudo shutdown now")
            return  

    # Cheking if module is currently executed
    if config.STATE in ["story_time", "fun_fact", "play_song"]:
        # Checking if STOP button is pressed
        if config.stop_button:
            x0, y0, x1, y1 = config.stop_button
            if x0 <= x <= x1 and y0 <= y <= y1: # Inside STOP button
                print("Stop button pressed")
                config.STOP_FLAG = True

                # Terminating running speech proces
                if config.speak_process and config.speak_process.poll() is None:
                    config.speak_process.terminate()
                    config.speak_process = None
                return
        return  # Ignore other touches while busy

    # Menu interactions
    if config.STATE == "menu":
        index = (y - 10) // 40 
        if 0 <= index < len(menu_items):
            selected_item = menu_items[int(index)]
            print(f"Selected menu item: {selected_item}")
            # Triggering corresponding toy feature
            if selected_item == "Story Time":
                story_time()
            elif selected_item == "Take a Picture":
                take_photo()
            elif selected_item == "Play a Song":
                play_song()
            elif selected_item == "Fun Facts":
                fun_fact()
            elif selected_item == "Sleep":
                speak("Going to sleep...")
                config.WAKE_FLAG = False
                config.STATE = "sleep"
                draw_sleep_screen()

# Function for listener loop that continuously checks for touch
def touch_listener():
    """
    If awake handles touch normally, if asleep any touch on screen wakes
    the toy and redraws menu.
    """
    while True:
        coords = get_touch()
        if config.WAKE_FLAG: # Awake state
            if coords:
                handle_touch(*coords)
        else: # Sleep state
            if coords:
                print("Touch detected - waking up!")
                config.WAKE_FLAG = True
                config.STATE = "menu"
                speak("Hello, I'm awake! What do you want to do?")
                draw_menu()
        time.sleep(0.1)  # Debounce
            
# Function for checking if STOP button is pressed
def check_stop_button(x, y):
    if config.stop_button:
        x0, y0, x1, y1 = config.stop_button
        if x0 <= x <= x1 and y0 <= y <= y1:
            config.STOP_FLAG = True
            print("Stop is pressed.")

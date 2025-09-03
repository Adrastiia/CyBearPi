"""
funfact.py - module for telling fun facts
This module allows retrieving fun facts from API or local txt file, displaying text on screen using
scrolling if text is long and simultaneously reading fun fact using TTS.
If API is not available, local fun fact file is used.
User can stop reading at any time.
"""

import os, time, threading # Standard Python library for working with files, time and running in separate thread
from PIL import Image, ImageDraw # Library for working with imges and drawing text and graphics
import adafruit_rgb_display.ili9341 as ili9341 # Library for controlling ILI9341 display via SPI
import requests # HTTP request for retrieving fun fact from API 
import random # Standard Python library, here used for randomly retrieving fun fact
import re # Regular expresions, here used for separating text to sentences
import config # Module with global settings and variables shared between all parts of the system
from tts import speak # Module for converting text to speech with espeak
from display import display, wrap_text, fontM, WIDTH, HEIGHT, draw_stop_button, show_message, draw_menu # Module for drawing on display

# Function for getting random fun fact from the local file
def read_local_fun_facts():
    if not os.path.exists(config.FACT_FILE):
        return "No fun facts available."
    with open(config.FACT_FILE, "r") as f:
        facts = f.readlines()
    return random.choice(facts).strip()

# Scrolling long text on screen using scroll effect
def scroll_text_on_screen(text):
    image_height = 1000  
    scroll_speed = 5      # Scrolling speed - pixels per frame
    frame_delay = 0.005    # Pause between frames

    # Preparing full image
    full_image = Image.new("RGB", (WIDTH, image_height), "black")
    draw = ImageDraw.Draw(full_image)

    lines = wrap_text(text, fontM, WIDTH - 20, draw)
    y = 10
    for line in lines:
        draw.text((10, y), line, font=fontM, fill="white")
        y += fontM.getbbox(line)[3] - fontM.getbbox(line)[1] + 4

    # Scrolling the image upward
    for offset in range(0, max(1, y - HEIGHT + 50), scroll_speed):
        if config.STOP_FLAG:
            break

        frame = full_image.crop((0, offset, WIDTH, offset + HEIGHT))
        draw = ImageDraw.Draw(frame)
        draw_stop_button(draw)
        display.image(frame)
        time.sleep(frame_delay)

# Function for reading fun facts
def fun_fact():
    """
    Tries to retrieve fun fact from API, if API is not available it uses local txt file instead.
    Smultaneously showing text with scroll effect and reading it using TTS.
    It can be interrupted by pressing Stop button and when fun fact is finished either by
    getting to the end or being interrupted user is returned to menu.

    """
    if config.STATE == "fun_fact":
        return # Prevent multiple starts
    
    config.STOP_FLAG = False
    config.STATE = "fun_fact"
    config.stop_button = None

    def fun_fact_thread():

        # Early exit if stopped
        if config.STOP_FLAG:
            return

        speak("Here's a fun fact for you!")

        # Early exit after speaking if stopped
        if config.STOP_FLAG:
            if config.speak_process and config.speak_process.poll() is None:
                config.speak_process.terminate()
            return

        # Fetch fun fact from API or local fallback file
        fact_text = None

        try:
            response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en", timeout=5)
            if response.status_code == 200:
                fact_text = response.json().get("text", "").strip()
        except Exception as e:
            print(f"Fun fact API error: {e}")
            fact_text = None

        if not fact_text:
            fact_text = read_local_fun_facts()

        # Starting scroll and reading in paralel threads
        def scroll_task():
            scroll_text_on_screen(fact_text)

        def speak_task():
            sentences = re.split(r'(?<=[.!?]) +', fact_text.strip())
            for sentence in sentences:
                if config.STOP_FLAG:
                    if config.speak_process and config.speak_process.poll() is None:
                        config.speak_process.terminate()
                    break
                speak(sentence.strip())

        # Start both threads
        scroll_thread = threading.Thread(target=scroll_task)
        speak_thread = threading.Thread(target=speak_task)
        scroll_thread.start()
        speak_thread.start()
        scroll_thread.join()
        speak_thread.join()

        # Prepare display with Stop button
        image = Image.new("RGB", (WIDTH, HEIGHT), "black")
        draw = ImageDraw.Draw(image)
        draw_stop_button(draw)
        display.image(image)

        # Show message based on STOP or finish
        if config.STOP_FLAG:
            show_message("Fun fact stopped", delay=1)
        else:
            show_message("Fun fact done", delay=2)

        config.STOP_FLAG = False
        config.STATE = "menu"
        draw_menu()

    # Starting fun fact thread
    threading.Thread(target=fun_fact_thread, daemon=True).start()

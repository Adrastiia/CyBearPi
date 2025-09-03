"""
story.py - module for telling stories
This module allows retrieving story from API or local file, displaying text on screen using
scrolling if text is long and simultaneously reading story using TTS.
If API is not available, local story file is used.
User can stop reading at any time.
"""

import os, time, threading # Standard Python library for working with files, time and running in separate thread
from PIL import Image, ImageDraw # Library for working with imges and drawing text and graphics
import adafruit_rgb_display.ili9341 as ili9341 # Library for controlling ILI9341 display via SPI
import requests # HTTP request for retrieving story from API 
import random # Standard Python library, here used for randomly retrieving story
import re # Regular expresions, here used for separating text to sentences
import config # Module with global settings and variables shared between all parts of the system
from display import display, WIDTH, HEIGHT, wrap_text, fontS, draw_stop_button, show_message, draw_menu # Module for drawing on display
from tts import speak # Module for converting text to speech with espeak

# Function for getting random story from the local file
def read_local_story():
    files = [f for f in os.listdir(config.STORY_FOLDER) if f.lower().endswith(".txt")]
    if not files:
        return "No local stories found."
    chosen_file = random.choice(files)
    with open(os.path.join(config.STORY_FOLDER, chosen_file), "r") as f:
        return f.read()

# Scrolling long text on screen using scroll effect
def scroll_text_on_screen(text):
    image_height = 1000  
    scroll_speed = 5      # Scrolling speed - pixels per frame
    frame_delay = 0.005   # Pause between frames

    # Preparing full image with text
    full_image = Image.new("RGB", (WIDTH, image_height), "black")
    draw = ImageDraw.Draw(full_image)

    lines = wrap_text(text, fontS, WIDTH - 20, draw)
    y = 10
    for line in lines:
        draw.text((10, y), line, font=fontS, fill="white")
        y += fontS.getbbox(line)[3] - fontS.getbbox(line)[1] + 4

    # Scrolling the image upward
    for offset in range(0, max(1, y - HEIGHT + 50), scroll_speed):
        if config.STOP_FLAG:
            break

        frame = full_image.crop((0, offset, WIDTH, offset + HEIGHT))
        draw = ImageDraw.Draw(frame)
        draw_stop_button(draw)
        display.image(frame)
        time.sleep(frame_delay)

# Function for reading stories
def story_time():
    """
    Tries to retrieve story from API, if API is not available it uses local file instead.
    Smultaneously showing text with scroll effect and reading it using TTS.
    It can be interrupted by pressing Stop button and when story is finished either by
    getting to the end or being interrupted user is returned to menu.

    """
    if config.STATE == "story_time":
        return  # Prevent multiple starts
    
    config.STOP_FLAG = False
    config.STATE = "story_time"
    config.stop_button = None

    def story_thread():

        # Early exit if stopped
        if config.STOP_FLAG:
            return

        speak("Get comfy. I'll tell you a story.")

        # Early exit after speaking if stopped
        if config.STOP_FLAG:
            if config.speak_process and config.speak_process.poll() is None:
                config.speak_process.terminate()
            return

        # Fetch story from API or local fallback file
        story_text = None

        try:
            response = requests.get("https://shortstories-api.onrender.com/stories/", timeout=5)
            if response.status_code == 200:
                stories = response.json()
                if stories:
                    selected = random.choice(stories)
                    title = selected.get("title", "A Story")
                    body = selected.get("story", "")
                    moral = selected.get("moral", "")
                    story_text = f"{title}\n\n{body}"
                    if moral:
                        story_text += f"\n\nMoral: {moral}"
        except Exception as e:
            print(f"API error: {e}")
            story_text = None

        if not story_text:
            story_text = read_local_story()

        # Prepare display with Stop button
        image = Image.new("RGB", (WIDTH, HEIGHT), "black")
        draw = ImageDraw.Draw(image)
        draw_stop_button(draw)
        display.image(image)

        # Starting scroll and reading in paralel threads
        def scroll_task():
            scroll_text_on_screen(story_text)

        def speak_task():
            sentences = re.split(r'(?<=[.!?]) +', story_text.strip())
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

        # Show message based on STOP or finish
        if config.STOP_FLAG:
            show_message("Story stopped", delay=1)
        else:
            show_message("Story finished", delay=2)

        config.STOP_FLAG = False
        config.STATE = "menu"
        draw_menu()

    # Starting story thread
    threading.Thread(target=story_thread, daemon=True).start()

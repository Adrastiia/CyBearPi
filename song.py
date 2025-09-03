"""
song.py - module for reproduction of songs. 
This module enables reproduction of random song from local music folder.
On screen it displays name of the song and Stop button for stopping reproduction.
When reproduction is stopped or interrupted, state is back to menu.
"""

import os, time, threading # Standard Python library for working with files, time and running in separate thread
from PIL import Image, ImageDraw # Library for working with imges and drawing text and graphics
import adafruit_rgb_display.ili9341 as ili9341 # Library for controlling ILI9341 display via SPI
import random # Standard Python library, here used for randomly playing song
import subprocess # Standard Python library for starting and controling external processes
import config # Module with global settings and variables shared between all parts of the system
from tts import speak # Module for converting text to speech with espeak
from display import display, WIDTH, HEIGHT, draw_stop_button, wrap_text, fontM, show_message, draw_menu # Module for drawing on display

# Function for playing random song from local library
def play_song():
    """"
    Randomly selects .wav file from SONG_FOLDER. Using TTS it says which song
    is going to be played. It also shows name of the song and Stop button on display.
    Starts aplay process for reproduction and it allows for interrupting reproduction
    using voice command or Stop button. After song is finished or interrupted user is
    returned to menu. If there is no available song it speaks message to the user.
    """
    config.STATE = "play_song"
    config.STOP_FLAG = False
    config.stop_button = None

    try:
        # Retrieving playlist
        song_files = [f for f in os.listdir(config.SONG_FOLDER) if f.endswith(".wav")]
        if not song_files:
            speak("No songs found.")
            return

        # Randomly selecting song
        song_file = random.choice(song_files)
        speak(f"Playing {song_file.replace('-', ' ').replace('.wav', '')}")

        # Drawing STOP button and song name on screen
        image = Image.new("RGB", (WIDTH, HEIGHT), "black")
        draw = ImageDraw.Draw(image)

        draw_stop_button(draw)

        max_width = WIDTH - 20
        lines = wrap_text(f"Now playing: {song_file.replace('-', ' ').replace('.wav', '')}", fontM, max_width, draw)
        y = 10
        for line in lines:
            draw.text((10, y), line, fill="white", font=fontM)
            y += fontM.getbbox(line)[3] + 4

        display.image(image)

        # Play song subprocess, function for reproduction of song in separate thread
        def song_thread():
            process = subprocess.Popen(["aplay", os.path.join(config.SONG_FOLDER, song_file)])
            while process.poll() is None:
                if config.STOP_FLAG:
                    process.terminate()
                    break
                time.sleep(0.1)

            # Show message depending on whether it was stopped or finished
            if config.STOP_FLAG:
                show_message("Song stopped", delay=1)
            else:
                show_message("Song finished", delay=2)

            # Reseting state and return to menu
            config.STOP_FLAG = False
            config.STATE = "menu"
            draw_menu()

        # Starting song thread
        threading.Thread(target=song_thread, daemon=True).start()

    except Exception as e:
        speak("Something went wrong.")
        print("Error in play_song:", e)


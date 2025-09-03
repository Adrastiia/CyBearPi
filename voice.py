"""
voice.py - module for voice commands
This module handles voice interaction using Picovoice tools:
Porcupine for detecting wake word command, Rhino for user intent recognition,
PvRecorder for recording sound from the microphone.
After command is recognized, corresponding module is called.
"""

import pvporcupine # Picovoice library for wake word detection
import pvrhino # Picovoice library for intent recognition
from pvrecorder import PvRecorder # Picovoice library for recording sound from the microphone in real time
import adafruit_rgb_display.ili9341 as ili9341 # Library for controlling ILI9341 display via SPI 
import config # Module with global settings and variables shared between all parts of the system
from tts import speak # Module for converting text to speech with espeak
from display import display, draw_menu, draw_sleep_screen # Module for drawing menu and sleep screen on displaz
from camera import take_photo # Function for taking and saving photographs
from song import play_song # Function for reproduction of random song from local folder
from story import story_time # Function for telling story from API or local file
from funfact import fun_fact # Function for telling fun facts from API or local file

# Defininig voice listener for porcupine wake word and rhino intent
def voice_listener():
    """
    Function is using Porcupine for wake word detection and Rhino for intent recognition.
    When intent is recognized, corresponding module is launched.
    First it waits for wake word, then it starts Rhino for intent recognition. If intent is
    recognized command is executed if not it reports that intent wasn't recognized.
    """
    # Initialization and creation of Porcupine instance for wake word
    porcupine = pvporcupine.create(
        access_key=config.ACCESS_KEY,
        keyword_paths=["...Wake-up-teddy_en_raspberry-pi_v3_0_0.ppn"] # path for wake word
    )

    # Initialization of microphone for recording
    recorder = PvRecorder(device_index=2, frame_length=porcupine.frame_length)

    # Initialization and creation of Rhino instance for intent recognition
    rhino = pvrhino.create(
        access_key=config.ACCESS_KEY,
        context_path=config.RHINO_PATH
    )

    try:
        recorder.start()
        print("Voice listener started")

        while True:
            pcm = recorder.read()
            # Waiting for wake word
            if not config.WAKE_FLAG:
                result = porcupine.process(pcm)
                if result >= 0:
                    print("Wake word detected!")
                    speak("Hello, I'm awake! What do you want to do?")
                    config.WAKE_FLAG = True
                    draw_menu()
                    continue

            # Recognition of intents using Rhino
            if config.WAKE_FLAG:
                is_finalized = rhino.process(pcm)
                if is_finalized:
                    inference = rhino.get_inference()
                    if inference.is_understood:
                        intent = inference.intent
                        print(f"Recognized intent: {intent}")

                        # Stop command, interrupt active module
                        if intent == "stop_module":
                            if config.STATE in ["story_time", "play_song", "fun_fact"]:
                                config.STOP_FLAG = True
                                print("Voice STOP command received.")
                                # Reset STOP_FLAG so next commands work
                                config.STATE == "menu"
                        
                        # Executing functions from mnenu
                        elif config.STATE == "menu":
                            if intent == "story_time":
                                story_time()
                            elif intent == "photo_time":
                                take_photo()
                            elif intent == "play_song":
                                play_song()
                            elif intent == "fun_fact":
                                fun_fact()
                            elif intent == "go_to_sleep":
                                speak("Going to sleep...")
                                config.WAKE_FLAG = False
                                draw_sleep_screen()
                    else:
                        # If Rhino thinks speech was present but no intent matched 
                        if inference.slots or inference.intent:
                            # Rhino thinks something was said but no match
                            speak("Sorry, I didn't understand.")
                        else:
                            # Probably silence or noise, do nothing
                            print("No speech detected / silence.")
    except Exception as e:
        print("Voice thread error:", e)

    # Safe shutdown of resources
    finally:
        recorder.stop()
        porcupine.delete()
        rhino.delete()

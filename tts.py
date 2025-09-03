"""
tts.py - Module for Text-to-Speech
It alows for conversion of text to speech using espeak tool.
Function speak receives text and plays it with the possibility of interruption
via the global variable speak_process from config.py
Function starts espeak as a separate process and saves a reference to it in 
config.speak_process so that other components can interrupt it during execution.
"""

import subprocess # Standard Python library for starting and controling external processes
import config # Module with global settings and variables shared between all parts of the system

# Function for converting given text to speech
def speak(text):
    print("Speaking:", text)
    # Starting espeak process with select parameters, subprocess is used to run espeak as a separate process
    config.speak_process = subprocess.Popen([
        'espeak',
        '-v', 'en+f3', # used voice 
        '-p', '70', # pitch of the voice
        '-s', '180', # speed of speaking
        text
    ])
    config.speak_process.wait()  # Wait for completion (can be interrupted)

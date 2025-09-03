"""
main.py - Entry point for Cybear toy system.
It coordinates startup of core components including
touchscreen listener for UI interaction via touch input,
voice listener for wake word and voice commands and
display mangement for showing sleep screen at startup.
This system is multithreaded - voice and touch listeners run
in separated threads to allow simultaneous input handling. 
Keeps program running indefinitely until shutdown.

Usage:
Run this script to start the toy.
Use touchscreen and/or voice commands to interact with the toy.
Long press anywhere on touchscreen for 5 seconds will trigger shutdown.
"""

import time, threading # Standard Python library for working with time and running in separate thread
from voice import voice_listener # Continuous voice input detection
from touch import touch_listener # Handles touchscreen input events
from display import draw_sleep_screen # Draws sleep screen on display



def main():
    """
    Starts touchscreen and voice listener threads,
    shows sleep screen, and keeps main thread alive.
    """
    # Start touchscreen listener in separate daemon thread
    threading.Thread(target=touch_listener, daemon=True).start()
    # Start voice listener in separate daemon thread
    threading.Thread(target=voice_listener, daemon=True).start()

    # Show sleep screen on startup
    draw_sleep_screen()

    try:
        # Keep main thread alive indefinitely
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program.")

if __name__ == "__main__":
    main()

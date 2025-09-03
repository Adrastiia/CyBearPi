"""
camera.py - module for controlling camera and saving taken photos.
This module allows taking photographs with Raspberry Pi Camera Module 2.
Photographs are saved localy on device as well in MongoDB database in binary format.
After photo is taken IP address for accessing galery in web browser is shown.
"""

import os, time, threading, datetime # Standard Python library for working with files, time, running in separate thread and date/time
from bson.binary import Binary # Enables saving binary data in MongoDB
import socket # Getting local IP address
import config # Module with global settings and variables shared between all parts of the system
from tts import speak # Module for converting text to speech with espeak 
from display import show_message, draw_menu # Module for drawing on display

# Helper function for getting IP address
def get_ip():
    """
    Returns local IP address of device.
    Tries to connect to Google DNS to get correct IP address fro which device
    is reachable, it this is not possible it returns localhost.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable, used only for getting IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "localhost"
    finally:
        s.close()
    return ip

# Function for taking a photograph
def take_photo():
    """
    Taking photo with Pi Camera and saving it locally and in MongoDB.
    It starts camera and take some time for warming up.
    When photo is taken it is saved in local PHOTO_FOLDER directory.
    It also attempts to save it in MongoDB collection as binary.
    User is notified via screen and TTS and IP address for viewing photos
    is displayed.
    """
    config.STATE = "taking_photo"
    speak("Say cheesee.")
    show_message("3...2...1")

    def photo_thread():
        # Configuring and starting camera
        config.picam2.configure(config.picam2.create_still_configuration())
        config.picam2.start()
        time.sleep(1)  # For warming up

        # Generating name and photo path
        filename = datetime.datetime.now().strftime("photo_%Y%m%d_%H%M%S.jpg")
        filepath = os.path.join(config.PHOTO_FOLDER, filename)

        # Capturing photo and stopping camera
        config.picam2.capture_file(filepath)
        config.picam2.stop()

        # Attempt to save photo in MongoDB
        try:
            with open(filepath, "rb") as img_file: # rb - read binary
                img_data = img_file.read()

            config.photos_collection.insert_one({
                "filename": filename,
                "filepath": filepath,
                "timestamp": datetime.datetime.now(),
                "image_binary": Binary(img_data)
            })
            print(f"Saved {filename} and image data to MongoDB.")
        except Exception as e:
            print(f"Failed to store image binary in MongoDB: {e}")

        # Audio and visual notification to user
        speak("Picture saved.")
        ip_address = get_ip()
        show_message(f"Photo saved.\nVisit: http://{ip_address}\n:8080", delay=2)

        # Returning to menu
        draw_menu()

    # Starting photo thread
    threading.Thread(target=photo_thread, daemon=True).start()


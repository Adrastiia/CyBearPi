"""
config.py - CyBear smart toy configuration.
This module contains configuration variables and starting initializations
needed for system to work. It has all paths to files, database configuration,
initialization of camera and sound and state variables.
"""

from pymongo import MongoClient # alows connecting to and working with MongoDB database
from picamera2 import Picamera2 # official Python library for working with Raspberry Pi CSI camera
import pygame # for audio reproduction via pygame.mixer module


# Files and paths
STORY_FOLDER = "...Stories" # Backup file folder for stories when API is not available
FACT_FILE = "...Facts.txt" # Backup text file for fun facts when API is not available
SONG_FOLDER = "...Songs" # Folder for localy saved songs
PHOTO_FOLDER = "...Photos" # Taken pictures are saved here
RHINO_PATH = "...CyBear_en_raspberry-pi_v3_0_0.rhn" # Rhino Speech-to-Intent file for voice to intent, used in voice commands

# Picovoice Access Key for Porcupine and Rhino
ACCESS_KEY = "..."

# State variables
WAKE_FLAG = False # Indicates if there was wake word detection
STATE = "sleep"  # Starts in sleep mode
CURRENT_MENU_ITEM = None # Currently active menu item (story, song, fun fact, photo ...)
STOP_FLAG = False # Flag for stoping currently active module

stop_button = None # Reference to Stop button on touchscreen

# MongoDB Atlas setup
mongo_client = MongoClient('mongodb+srv://cybear:....mongodb.net/') # Connect to MongoDB Atlas
db = mongo_client['...'] # Main database
photos_collection = db['...'] # Collection for saving photos

# Camera initialization
picam2 = Picamera2()

# Pygame mixer initialization
pygame.mixer.init() # Audio mixer for sound reproduction

# Text to speech using espeak
speak_process = None  # Global reference to espeak process, it alows Stop button to stop speech 

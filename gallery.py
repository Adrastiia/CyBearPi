"""
gallery.py - Flask web application for displaying photos taken by CyBear smart toy
It sets up simple web gallery to view images stored in MongoDB database.
Gallery page uses simple template gallery.html to show thumbnails of all photos and
users can click on any photo to open it in full size.
"""

from flask import Flask, render_template, send_file, abort # Lightweight web framework for Python
from pymongo import MongoClient # Alows connecting to and working with MongoDB database
from bson import ObjectId # To query MongoDB documents by their ObjectId
from io import BytesIO # To handle image byte streams

# Flask initialization
app = Flask(__name__)

# MongoDB setup
MONGO_URI = "mongodb+srv://....mongodb.net/"
client = MongoClient(MONGO_URI) # Connect to MongoDB Atlas
db = client["..."] # Main database
photos_collection = db["..."] # Collection for saving photos

# Routes
@app.route('/')
# Gallery function
def gallery():
    """
    Main gallery page.
    Queries MongoDB photos collection and retrieves all photos with their id, timestamp
    and filename then passes list to the gallery.html for rendering.
    """
    # Fetch photos from database
    photos = list(photos_collection.find({}, {"_id": 1, "timestamp": 1, "filename": 1}))
    # Return HTML template with photos
    return render_template("gallery.html", photos=photos)

@app.route('/image/<photo_id>')
# Function for serving full size image for a given ID
def serve_image(photo_id):
    try:
        # Retrieve photo by ObjectId
        photo = photos_collection.find_one({"_id": ObjectId(photo_id)})
        if photo and "image_binary" in photo:
            # Check if photo exist and contains image data
            image_bytes = photo["image_binary"]
            # Send image as a file
            return send_file(BytesIO(image_bytes), mimetype='image/jpeg')
    except Exception as e:
        # Print error for debugging
        print("Error:", e)
    # If photo is not found 
    return abort(404)

# Application entry point
if __name__ == '__main__':
    # Run Flask web server, accessible from any device in local network
    app.run(host='0.0.0.0', port=8080)


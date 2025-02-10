import base64
import os
from typing import Any

from flask_cors import CORS

from flask import Flask, request

app = Flask(__name__)
CORS(app)

# Directory to save files
SAVE_DIRECTORY = "/home/user/Wallpapers/packs/"


def trymakedirectory(filename):
    filename = filename
    try:
        filename = filename.split(".")[0]
        filename = filename.split("_")[0]
        return filename
    finally:
        return filename


def trygetfilename(screen, location, extension):
    base_filename = str(screen) + "." + extension
    file_path = os.path.join(location, base_filename)
    # Check if the file exists and append _x if it does
    if os.path.exists(file_path):
        # Try appending _x where x is the next available number
        x = 1
        while os.path.exists(os.path.join(location, f"{str(screen)}_{x}.{extension}")):
            x += 1
        return str(screen) + f"_{x}." + extension
    else:
        # Return the original filename if it does not exist
        return base_filename


@app.route("/save", methods=["POST"])
def save_file():
    data: Any = request.json
    dirname = data.get("dirname", "Mix")
    packname = data.get("packname", "default")
    screenidx = data.get("screen", "1")
    filename = data.get("filename", "1.jpg")
    dir = trymakedirectory(filename)
    dir = os.path.join(SAVE_DIRECTORY, dirname, packname)
    extension = filename.split(".")[-1]
    filename = trygetfilename(screenidx, dir, extension)

    base64_content = data.get("content", "")
    file_content = base64.b64decode(base64_content)

    # Ensure the directory exists
    os.makedirs(dir, exist_ok=True)

    # Save the file
    filepath = os.path.join(dir, filename)
    with open(filepath, "wb") as file:
        file.write(file_content)

    return {"status": "success", "message": f"File saved to {filepath}"}, 200


if __name__ == "__main__":
    app.run(port=5000)

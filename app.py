from flask import Flask, request, jsonify
from flask_cors import CORS
from translate import translate
import time
import asyncio
import os
import subprocess


app = Flask(__name__)
CORS(app)
i = 0

@app.route('/translate', methods=['POST'])
def translate_file():
    global i
    start = time.time()
    print("Request received")
    file = request.files.get('file')
    if not file:
        print("No file found in the request")
        return jsonify({"error": "No file found"}), 400

    original_file_path = f"original{i}.webm"
    converted_file_path = f"converted{i}.wav"
    i += 1
    try:
        file.save(original_file_path)
        print(f"Original file saved at {original_file_path} with size {os.stat(original_file_path).st_size}")
    except Exception as e:
        print(f"Error saving file: {e}")
        return jsonify({"error": "Error saving file"}), 500

    # Convert the file using FFmpeg
    try:
        subprocess.run(["ffmpeg", "-y", "-f", "webm", "-i", original_file_path, converted_file_path], check=True)
        print(f"File converted to {converted_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during file conversion: {e}")
        return jsonify({"error": "Error during file conversion"}), 500

    # Ensure the converted file exists
    if not os.path.exists(converted_file_path):
        print(f"Converted file {converted_file_path} does not exist")
        return jsonify({"error": "File not found after conversion"}), 500

    print(f"Converted file size: {os.path.getsize(converted_file_path)} bytes")

    # Process the converted file for translation
    try:
        translated_text = asyncio.run(translate(converted_file_path))
        print(translated_text)
    except Exception as e:
        print(f"Error during translation: {e}")
        return jsonify({"error": "Error during translation"}), 500
    
    # Delete the files
    try:
        os.remove(original_file_path)
        os.remove(converted_file_path)
    except Exception as e:
        print(f"Error deleting files: {e}")

    print("Time taken for translation: ", time.time() - start)
    return jsonify({"translatedText": translated_text})

if __name__ == '__main__':
    app.run(port=8000, debug=True, threaded=True)

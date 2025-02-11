from flask import Flask, request, jsonify
import os
import hashlib
from PIL import Image
import numpy as np
import difflib

app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def calculate_text_similarity(text1, text2):
    """Calculate similarity between two text inputs using sequence matching."""
    return difflib.SequenceMatcher(None, text1, text2).ratio()


def calculate_image_hash(image_path):
    """Generate a perceptual hash for image comparison."""
    image = Image.open(image_path).convert("L").resize((8, 8), Image.ANTIALIAS)
    pixels = np.array(image)
    avg = pixels.mean()
    return ''.join('1' if pixel > avg else '0' for row in pixels for pixel in row)


@app.route('/detect', methods=['POST'])
def detect_plagiarism():
    result = {}

    # Handle text file
    text_file = request.files.get('text-file')
    if text_file:
        text_file_path = os.path.join(app.config['UPLOAD_FOLDER'], text_file.filename)
        text_file.save(text_file_path)
        with open(text_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text_data = f.read()
        # Mock detection: checking against static example
        example_text = "This is an example reference document for plagiarism detection."
        text_similarity = calculate_text_similarity(text_data, example_text)
        result['text_similarity_score'] = f"{text_similarity * 100:.2f}%"

    # Handle image file
    image_file = request.files.get('image-file')
    if image_file:
        image_file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(image_file_path)
        # Mock comparison using hash
        image_hash = calculate_image_hash(image_file_path)
        reference_hash = calculate_image_hash('./reference_image.jpg')  # Reference sample image
        image_similarity = 1 - sum(a != b for a, b in zip(image_hash, reference_hash)) / len(image_hash)
        result['image_similarity_score'] = f"{image_similarity * 100:.2f}%"

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)

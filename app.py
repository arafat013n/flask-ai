from flask import Flask, render_template, request, jsonify, send_file
import requests
from PIL import Image
from io import BytesIO
import os
import time

app = Flask(__name__)

# Hugging Face API Key
API_KEY = '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'  # Replace with your API Key

# FLUX.1-dev model API URL
URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"

# Headers for the API request
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Function to delete old images from the static folder
def delete_old_images():
    static_folder = "static"
    for filename in os.listdir(static_folder):
        if filename.startswith("generated_") and filename.endswith(".png"):
            os.remove(os.path.join(static_folder, filename))
            print(f"Deleted old image: {filename}")

# Home route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        input_text = request.form.get("input_text")

        # Delete old images before generating a new one
        delete_old_images()

        # Generate image with a unique filename
        image_path = generate_image(input_text)

        # Return JSON response with the image path
        if image_path:
            return jsonify({"image_path": image_path})
        else:
            return jsonify({"error": "Failed to generate image"}), 500

    return render_template("index.html")

# About page route
@app.route("/about")
def about():
    return render_template("about.html")

# Privacy policy page route
@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")

# Developer page route
@app.route("/developer")
def developer():
    return render_template("developer.html")

# Function to generate the image
def generate_image(input_text):
    response = requests.post(URL, headers=headers, json={"inputs": input_text})

    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))

        # Save image with a unique filename using timestamp
        timestamp = str(int(time.time()))
        image_path = f"static/generated_{timestamp}.png"  # Using the timestamp to make it unique
        image.save(image_path)
        return image_path
    else:
        return None

# Route to download the generated image
@app.route("/download/<filename>")
def download_file(filename):
    path = f"static/{filename}"  # Dynamically generating the download path
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
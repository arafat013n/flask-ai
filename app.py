from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_pymongo import PyMongo
from bson import ObjectId
from PIL import Image
from io import BytesIO
import os
import requests
import time

app = Flask(__name__)

# Secret key for session
app.secret_key = os.urandom(24)

# MongoDB connection string
app.config["MONGO_URI"] = "mongodb+srv://akash:<db_password>@cluster0.j48ryu4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# Hugging Face API Key
API_KEY = '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'

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

# Route for home page
@app.route("/", methods=["GET", "POST"])
def index():
    if 'user' not in session:
        flash("Please login to generate images", "danger")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        input_text = request.form.get("input_text")
        delete_old_images()
        image_path = generate_image(input_text)
        
        if image_path:
            return jsonify({"image_path": image_path})
        else:
            return jsonify({"error": "Failed to generate image"}), 500
    
    return render_template("index.html")

# Route for login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Fetch the user from MongoDB by username
        user = mongo.db.users.find_one({"username": username})
        
        # Check if the entered password matches the stored password
        if user and user["password"] == password:
            session['user'] = username
            flash("Login successful!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password", "danger")
    
    return render_template("login.html")

# Route for registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))
        
        # Check if the username already exists
        existing_user = mongo.db.users.find_one({"username": username})
        if existing_user:
            flash("Username already taken", "danger")
            return redirect(url_for("register"))
        
        # Insert the new user into MongoDB
        mongo.db.users.insert_one({"username": username, "password": password})
        flash("Registration successful! You can log in now.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

# Route for logout
@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("You have been logged out", "success")
    return redirect(url_for("login"))

# Function to generate the image
def generate_image(input_text):
    response = requests.post(URL, headers=headers, json={"inputs": input_text})

    if response.status_code == 200:
        image_data = response.content
        image = Image.open(BytesIO(image_data))
        
        # Save image with a unique filename using timestamp
        timestamp = str(int(time.time()))
        image_path = f"static/generated_{timestamp}.png"
        image.save(image_path)
        return image_path
    else:
        return None

# Route to download the generated image
@app.route("/download/<filename>")
def download_file(filename):
    path = f"static/{filename}"
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
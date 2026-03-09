import os
import random
import string
import time
import threading
import json
from flask import Flask, request, send_file, render_template

app = Flask(__name__)

# --- Config ---
UPLOAD_FOLDER = "uploads"
LINKS_FILE = "file_links.json"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024  # 25 MB
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Expiry time options (in seconds)
EXPIRY_OPTIONS = {
    "5": 5 * 60,
    "10": 10 * 60,
    "15": 15 * 60,
    "30": 30 * 60,
    "60": 60 * 60
}
DEFAULT_EXPIRY = "15"

# Load file links from persistent storage
def load_file_links():
    """Load file links from JSON file"""
    if os.path.exists(LINKS_FILE):
        try:
            with open(LINKS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_file_links(file_links):
    """Save file links to JSON file"""
    try:
        with open(LINKS_FILE, 'w') as f:
            json.dump(file_links, f)
    except:
        pass

# Store mapping: { random_id: {"path":..., "time":..., "expiry":...} }
file_links = load_file_links()

def generate_random_string(length=8):
    """Generate random ID for each file link"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.errorhandler(413)
def file_too_large(e):
    return "File is too large. Max limit is 25 MB.", 413

@app.route("/", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            return render_template("index.html", link=None, error="No file selected", expiry_options=EXPIRY_OPTIONS)

        file = request.files['file']
        if file.filename == "":
            return render_template("index.html", link=None, error="No file selected", expiry_options=EXPIRY_OPTIONS)

        # Get selected expiry time
        expiry_choice = request.form.get('expiry_time', DEFAULT_EXPIRY)
        if expiry_choice not in EXPIRY_OPTIONS:
            expiry_choice = DEFAULT_EXPIRY
        expiry_seconds = EXPIRY_OPTIONS[expiry_choice]

        # Save uploaded file
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Generate random link ID
        random_id = generate_random_string()
        file_links[random_id] = {
            "path": filepath,
            "time": time.time(),
            "expiry": expiry_seconds
        }
        save_file_links(file_links)  # Persist to disk

        share_link = request.host_url + random_id
        # Render the same page but with the link
        return render_template("index.html", link=share_link, error=None, selected_expiry=expiry_choice, expiry_options=EXPIRY_OPTIONS)

    # GET request: just show the page without a link
    return render_template("index.html", link=None, error=None, expiry_options=EXPIRY_OPTIONS)

@app.route("/<random_id>")
def download(random_id):
    """Serve the file if link is still valid"""
    file_info = file_links.get(random_id)
    if not file_info:
        return "Invalid or expired link", 404

    filepath = file_info["path"]
    # Check if file exists
    if not os.path.exists(filepath):
        return "File not found", 404

    try:
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error serving file {filepath}: {str(e)}")
        return "Error downloading file", 500

# --- Background cleaner thread ---
def cleanup_expired_files():
    """Periodically remove files older than their expiry time"""
    while True:
        now = time.time()
        expired_keys = []
        for key, info in list(file_links.items()):
            expiry_time = info.get("expiry", EXPIRY_OPTIONS[DEFAULT_EXPIRY])
            if now - info["time"] > expiry_time:
                # Delete the file
                try:
                    os.remove(info["path"])
                except FileNotFoundError:
                    pass
                expired_keys.append(key)

        # Remove expired entries
        for key in expired_keys:
            del file_links[key]
        
        if expired_keys:
            save_file_links(file_links)  # Persist changes

        time.sleep(60)  # Check every 60 seconds

# Start background thread for cleaning expired files
threading.Thread(target=cleanup_expired_files, daemon=True).start()

if __name__ == "__main__":
    # For local development
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('DEBUG', 'True').lower() == 'true'
    )

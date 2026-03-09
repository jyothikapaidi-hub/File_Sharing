# File Sharing App

A simple Flask application for uploading and sharing files with configurable expiry times.

## Features
- Upload files up to 25MB
- Generate shareable links with custom expiry times (5 min, 10 min, 15 min, 30 min, 1 hour)
- Automatic cleanup of expired files
- Clean, responsive web interface

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   python wsgi.py
   ```

3. Open http://localhost:5000 in your browser

## Deployment on PythonAnywhere

1. **Create a PythonAnywhere account** at https://www.pythonanywhere.com/

2. **Upload your files** to PythonAnywhere:
   - Create a new web app
   - Upload all files from this project to your PythonAnywhere home directory
   - Make sure the `templates/` and `uploads/` directories are included

3. **Set up the web app**:
   - Go to the Web tab in PythonAnywhere
   - Set the source code path to your project directory
   - Set the WSGI configuration file to: `wsgi.py`
   - In the WSGI file field, enter: `wsgi.py`

4. **Install dependencies**:
   - Go to the Consoles tab
   - Open a Bash console
   - Run: `pip install -r requirements.txt`

5. **Configure static files** (if needed):
   - The app uses relative paths, so static files should work automatically

6. **Reload your web app**:
   - Go back to the Web tab
   - Click the "Reload" button

Your app should now be live at your PythonAnywhere URL!

## Important Notes for PythonAnywhere Deployment

- **WSGI Multi-Process Limitation**: PythonAnywhere uses multiple WSGI processes. The current implementation uses in-memory storage for file links, which means:
  - Files uploaded in one process may not be accessible from another process
  - The cleanup thread runs in each process independently
  - For production use, consider implementing persistent storage (database) for file links

- **File Storage**: Uploaded files are stored in the `uploads/` directory. Make sure this directory has proper permissions.

- **Background Cleanup**: The cleanup thread will work, but it only cleans files known to its process.

## Environment Variables

For production deployment, you can set:
- `PORT`: Port number (default: 5000)
- `DEBUG`: Set to 'false' for production (default: true for local dev)

## File Structure
```
file-sharing/
├── wsgi.py             # Main Flask application (WSGI entry point)
├── app.py              # Legacy file (can be removed)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Main upload page
└── uploads/            # Directory for uploaded files (auto-created)
```
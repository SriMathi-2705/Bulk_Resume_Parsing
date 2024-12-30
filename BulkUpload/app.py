from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from resume_parser import ResumeParser


app = Flask(__name__)

# Set up allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = 'Bulk_Resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if the file has a valid extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Bulk upload endpoint for resumes
@app.route('/upload', methods=['POST'])
def upload_files():
    if 'resumes' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('resumes')
    if not files:
        return jsonify({"error": "No files selected"}), 400

    result = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Parse resume and extract information
            try:
                resume_data = ResumeParser.extract_resume_data(filepath, filename)
                result.append(resume_data)
            except Exception as e:
                result.append({
                    'filename': filename,
                    'error': str(e)
                })
        else:
            result.append({
                'filename': file.filename,
                'error': 'Invalid file format'
            })

    # Return parsed data or errors
    return render_template('index.html', result=result)

# Home route
@app.route('/bulk-upload')
def index():
    return render_template('index.html', result=None)

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    app.run(debug=True)

from flask import Flask, render_template, send_from_directory, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads' 
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
     uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
     return render_template("index.html", uploaded_files=uploaded_files)


@app.route('/upload', methods=['POST'])
def upload_video():
    # Check if a file was uploaded
    if 'video' not in request.files:
        return "No video file provided"

    video_file = request.files['video']

    # Check if the file has a valid extension
    if video_file and allowed_file(video_file.filename):
        # Save the uploaded video to the UPLOAD_FOLDER directory
        video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], video_file.filename))
        return f"Video '{video_file.filename}' uploaded successfully!"
    else:
        return "Invalid file format. Please upload a valid video file."

@app.route('/download/<filename>')
def download_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)


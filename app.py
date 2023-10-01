from flask import Flask, render_template, send_file, send_from_directory, request
import os
import speech_recognition as sr
import moviepy.editor as mp

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads' 
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def ensure_path_exists(path):
    if not os.path.exists(path):
        # If not, create the folder
        os.makedirs(path)
        print(f'The folder {path} has been created.')
    else:
        print(f'The folder {path} already exists.')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
     uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
     return render_template("index.html", uploaded_files=uploaded_files)

@app.route("/video", methods=["GET"])
def video():
    ensure_path_exists("uploads")
    ensure_path_exists("temp")
    # Path to your video file
    video_name = request.args.get(
        "name"
    )  # Fetch the 'name' query parameter from the URL
    video_path = f"uploads/{video_name}"  # Assuming videos are stored in a directory
    return send_file(video_path, mimetype="video/mp4")


@app.route("/transcribe", methods=["GET"])
def transcribe():
    ensure_path_exists("uploads")
    ensure_path_exists("temp")
    try:
        # Get the video file from the request
        video_file = request.args.get("name")
        # Initialize SpeechRecognition recognizer
        video = mp.VideoFileClip(f"uploads/{video_file}")
        if video.audio is None:
            return {'error': 'The video does not have an audio component.'}, 400
        audio_path = f"temp/{video_file}.wav"
        video.audio.write_audiofile(audio_path)
        recognizer = sr.Recognizer()
        # Read audio from the video file
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        # Perform speech recognition
        try:
            transcription = recognizer.recognize_google(audio_data)
            # Clean up temporary audio file
            video.close()
            os.remove(audio_path)
            return {"transcription": transcription}
        except Exception as e:
            return {"error": 'Unable to transcribe file'}, 500
    except Exception as e:
        print(e)
        return {"error": str(e)}, 500


@app.route("/upload", methods=["POST"])
def upload_video():
    # Check if a file was uploaded
    if "video" not in request.files:
        return "No video file provided"

    video_file = request.files["video"]

    # Check if the file has a valid extension
    if video_file and allowed_file(video_file.filename):
        # Save the uploaded video to the UPLOAD_FOLDER directory
        video_file.save(os.path.join(app.config["UPLOAD_FOLDER"], video_file.filename))
        return f"Video '{video_file.filename}' uploaded successfully!"
    else:
        return "Invalid file format. Please upload a valid video file."


@app.route("/download/<filename>")
def download_video(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename, as_attachment=True
    )

if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True, port=8000)

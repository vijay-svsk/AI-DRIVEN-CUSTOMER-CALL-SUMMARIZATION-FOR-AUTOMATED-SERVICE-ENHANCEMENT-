from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from utils.audio_processing import process_audio
from backend.db_handler import save_call_data

upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = "uploads/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'customer' not in request.form:
        return jsonify({"error": "Missing file or customer name"}), 400

    file = request.files['file']
    customer = request.form['customer']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    
    # Process the audio (transcription, diarization, etc.)
    transcript, speaker_data = process_audio(file_path)
    
    # Save details to the database
    call_entry = {
        "customer": customer,
        "file_path": file_path,
        "transcript": transcript,
        "speaker_data": speaker_data
    }
    save_call_data(call_entry)
    
    return jsonify({"message": "File uploaded and processed successfully", "data": call_entry}), 200

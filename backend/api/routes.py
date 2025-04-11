from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from utils.audio_processing import AudioProcessor
from utils.sentiment_analyser import SentimentAnalyzer
from utils.interaction_scoring import InteractionScorer
from utils.report_generation import ReportGenerator
import shutil
import os
import logging

# Initialize FastAPI app
app = FastAPI()

# Initialize processing components
audio_processor = AudioProcessor()
sentiment_analyzer = SentimentAnalyzer()
interaction_scorer = InteractionScorer()
report_generator = ReportGenerator()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@app.post("/process_call/")
async def process_call(audio_file: UploadFile = File(...)):
    """Processes a call recording and returns a summarized report."""
    try:
        # Validate file type
        if not audio_file.filename.endswith((".wav", ".mp3", ".flac")):
            raise HTTPException(status_code=400, detail="Invalid file format. Only WAV, MP3, and FLAC are supported.")
        
        file_path = os.path.join(UPLOAD_DIR, audio_file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        logger.info(f"File uploaded: {audio_file.filename}")
        
        # Process audio
        diarization_results = audio_processor.perform_diarization(file_path)
        cleaned_audio_path = audio_processor.denoise_audio(file_path, "cleaned_call.wav")
        transcript = audio_processor.transcribe_audio(cleaned_audio_path)
        
        # Perform sentiment analysis
        sentiment_scores = sentiment_analyzer.analyze_text(transcript)
        interaction_score = interaction_scorer.calculate_score(sentiment_scores)
        
        # Generate report
        report = report_generator.generate_report(cleaned_audio_path, transcript, sentiment_scores, interaction_score)
        
        return {"summary_report": report}
    
    except Exception as e:
        logger.error(f"Error processing call: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health_check/")
def health_check():
    """Simple health check endpoint."""
    return {"status": "API is running smoothly!"}

# Run FastAPI app with uvicorn (if running as a script)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

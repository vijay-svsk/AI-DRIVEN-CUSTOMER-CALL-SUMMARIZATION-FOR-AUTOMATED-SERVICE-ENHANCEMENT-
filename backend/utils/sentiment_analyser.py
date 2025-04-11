import librosa
import numpy as np
from db_handler import Database
from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self):
        """Initialize sentiment analysis models."""
        self.text_sentiment_model = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
        self.db = Database()
    
    def analyze_audio_sentiment(self, file_path: str):
        """Analyzes sentiment from audio using pitch and speech rate."""
        y, sr = librosa.load(file_path, sr=16000)
        pitch = librosa.yin(y, fmin=50, fmax=300)
        speech_rate = librosa.feature.rms(y=y).mean()
        
        pitch_median = np.nanmedian(pitch) if np.any(~np.isnan(pitch)) else 100  # Avoid NaN issues
        sentiment_score = np.clip((pitch_median - 100) / 50, 0, 1)  # Normalize 0-1
        
        return {"pitch_median": pitch_median, "speech_rate": speech_rate, "sentiment_score": sentiment_score}
    
    def analyze_text_sentiment(self, text: str):
        """Analyzes sentiment from transcribed text."""
        result = self.text_sentiment_model(text)[0]
        
        sentiment_data = {"label": result["label"], "score": result["score"]}
        
        # Store text sentiment in the database for future reference
        self.db.save_sentiment(text, sentiment_data)
        
        return sentiment_data

# Example usage
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    audio_sentiment = analyzer.analyze_audio_sentiment("cleaned_call.wav")
    print("Audio Sentiment:", audio_sentiment)
    
    text_sentiment = analyzer.analyze_text_sentiment("I am really happy with the service!")
    print("Text Sentiment:", text_sentiment)

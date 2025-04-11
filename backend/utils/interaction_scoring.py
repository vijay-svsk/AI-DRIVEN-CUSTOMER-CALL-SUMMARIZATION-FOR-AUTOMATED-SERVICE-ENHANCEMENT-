from utils.sentiment_analyser import SentimentAnalyzer
from db_handler import Database

class InteractionScorer:
    def __init__(self):
        """Initialize interaction scoring system."""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.db = Database()
    
    def score_interaction(self, audio_file: str, transcript: str):
        """Generates an overall interaction score based on sentiment analysis."""
        audio_sentiment = self.sentiment_analyzer.analyze_audio_sentiment(audio_file)
        text_sentiment = self.sentiment_analyzer.analyze_text_sentiment(transcript)
        
        # Normalize sentiment scores
        audio_score = (audio_sentiment['sentiment_score'] + 1) / 2  # Convert -1 to 1 range into 0 to 1
        text_score = text_sentiment['score']  # Hugging Face model score (already 0 to 1)
        
        # Weighted combination (adjust weights as needed)
        final_score = (0.6 * text_score) + (0.4 * audio_score)
        
        interaction_data = {
            "audio_sentiment": audio_sentiment,
            "text_sentiment": text_sentiment,
            "final_interaction_score": round(final_score, 2)
        }
        
        # Store interaction score in database
        self.db.save_interaction_score(audio_file, transcript, interaction_data)
        
        return interaction_data

# Example usage
if __name__ == "__main__":
    scorer = InteractionScorer()
    result = scorer.score_interaction("cleaned_call.wav", "I am really happy with the service!")
    print("Interaction Score Report:", result)

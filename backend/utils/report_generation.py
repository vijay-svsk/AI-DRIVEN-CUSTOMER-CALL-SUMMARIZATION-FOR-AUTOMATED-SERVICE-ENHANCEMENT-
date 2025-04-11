import json
from utils.interaction_scoring import InteractionScorer
from db_handler import Database

class ReportGenerator:
    def __init__(self):
        """Initialize the report generator."""
        self.scorer = InteractionScorer()
        self.db = Database()
    
    def generate_summary(self, transcript: str):
        """Generates a short summary from the conversation transcript."""
        summary = " ".join(transcript.split()[:50])  # Simple extractive summarization (first 50 words)
        return summary + "..." if len(transcript.split()) > 50 else summary
    
    def generate_report(self, audio_file: str, transcript: str):
        """Generates a structured report including interaction analysis and summary."""
        interaction_data = self.scorer.score_interaction(audio_file, transcript)
        summary = self.generate_summary(transcript)
        
        report = {
            "summary": summary,
            "interaction_score": interaction_data["final_interaction_score"],
            "audio_sentiment": interaction_data["audio_sentiment"],
            "text_sentiment": interaction_data["text_sentiment"]
        }
        
        # Save report to database
        self.db.save_report(audio_file, transcript, report)
        
        return json.dumps(report, indent=4)

# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()
    sample_transcript = "The customer was really satisfied with the service and appreciated the quick response time."
    report = generator.generate_report("cleaned_call.wav", sample_transcript)
    print("Final Report:", report)

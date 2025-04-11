import os
import json
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import json
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Configure Gemini
genai.configure(api_key="AIzaSyAvpaJ76-nL7ajWNesdmuRyBfD18lX65oE")
model = genai.GenerativeModel('models/gemini-1.5-pro-latest')

def analyze_audio(file_path):
    try:
        with open(file_path, 'rb') as f:
            audio_data = f.read()

        response = model.generate_content([
            """Analyze this audio file and provide:
            1. A detailed text analysis of the conversation.
            2. A JSON structure with technical analysis.

            - JSON must be valid without extra commas.
            - Do NOT include `//` comments.
            - Ensure all numerical values (except durations) are scaled to percentages (0-100%).
            - Sentiment, mood, persuasion, and engagement scores must sum to 100%.
            - Use only double quotes ("") for JSON keys and values.

            Format:
            [TEXT ANALYSIS]
            Full conversation analysis...

            [JSON]
            {
                "theme": "main theme",
                "number_of_speakers": integer,
                "key_topics": ["topic1", "topic2"],
                "mood_analysis": {
                    "agent": {"happy": integer, "sad": integer, "angry": integer, "neutral": integer},
                    "customer": {"happy": integer, "sad": integer, "angry": integer, "neutral": integer}
                },
                "background_noise": integer,
                "sentiment_score": integer,
                "transcription": "full transcription text",
                "speaker_diarization": [
                    {"time": "time", "speaker": "speaker", "text": "text"}
                ],
                "sentiment_analysis": {
                    "agent": {"positive": integer, "neutral": integer, "negative": integer},
                    "customer": {"positive": integer, "neutral": integer, "negative": integer}
                },
                "rate_of_interest": {
                    "agent": integer,
                    "customer": integer
                },
                "issue_escalation": boolean,
                "engagement_level": integer,
                "response_effectiveness": integer,
                "actionable_insights": ["insight1", "insight2"],
                "persuasion_analysis": {
                    "agent": integer,
                    "customer": integer
                },
                "sales_conversion_probability": integer,
                "competitive_mentions": ["competitor1", "competitor2"],
                "pain_points": ["pain point1", "pain point2"],
                "call_duration": integer,
                "resolution_time": integer,
                "follow_up_required": boolean,
                "follow_up_summary": "summary text",
                "churn_prediction": integer
            }""",
            {"mime_type": "audio/mp3", "data": audio_data}
        ])

        # Log raw response for debugging
        print("===== RAW API RESPONSE =====")
        print(response.text)
        print("============================")

        # Ensure response contains [JSON]
        if "[JSON]" not in response.text:
            return {"error": "Response format is incorrect. Missing [JSON] delimiter."}

        # Extract JSON block safely
        json_match = re.search(r"\[JSON\]\s*(\{.*\})", response.text, re.DOTALL)
        if not json_match:
            return {"error": "Failed to extract JSON from response"}

        json_part = json_match.group(1).strip()

        # Fix common JSON issues
        json_part = json_part.replace("“", "\"").replace("”", "\"")  # Normalize smart quotes
        json_part = json_part.replace("’", "'")  # Normalize apostrophes

        # Remove invalid JSON comments
        json_part = re.sub(r'//.*?\n', '', json_part)

        # Remove trailing commas before closing brackets
        json_part = re.sub(r',\s*([\]}])', r'\1', json_part)

        # Fix misplaced double quotes inside text fields
        json_part = re.sub(r'(\w)" (\w)', r'\1\' \2', json_part)  

        # Validate JSON format
        try:
            analysis_data = json.loads(json_part)
        except json.JSONDecodeError as e:
            print(f"===== INVALID JSON DETECTED =====")
            print(json_part)
            print(f"===== JSON ERROR: {e} =====")
            return {"error": f"Failed to parse JSON response: {e}"}

        return {
            "text_analysis": response.text.split("[JSON]")[0].replace("[TEXT ANALYSIS]", "").strip(),
            "data": analysis_data
        }

    except Exception as e:
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        result = analyze_audio(filename)
        os.remove(filename)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
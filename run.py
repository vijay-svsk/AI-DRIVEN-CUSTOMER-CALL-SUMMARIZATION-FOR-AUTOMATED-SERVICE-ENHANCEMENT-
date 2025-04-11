import librosa
import torch
import numpy as np
from pydub import AudioSegment
import whisper
from pyannote.audio import Pipeline
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from keybert import KeyBERT
import spacy
from transformers import BartForConditionalGeneration, BartTokenizer
from sklearn.metrics import accuracy_score, f1_score, precision_score

# Configuration
WHISPER_MODEL = "medium"
DIARIZATION_PIPELINE = "pyannote/speaker-diarization"
SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
SUMMARY_MODEL = "facebook/bart-large-cnn"

# Convert MP3 to WAV
def convert_mp3_to_wav(mp3_path, wav_path="output.wav"):
    audio = AudioSegment.from_mp3(mp3_path)
    audio.export(wav_path, format="wav")
    return wav_path

# Whisper Transcription
def transcribe_audio(wav_path):
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(wav_path)
    return result["text"]

# Speaker Diarization
def diarize_audio(wav_path):
    diarization_pipeline = Pipeline.from_pretrained(DIARIZATION_PIPELINE)
    diarization = diarization_pipeline(wav_path)
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "start": turn.start,
            "end": turn.end,
            "speaker": speaker
        })
    return segments

# Sentiment Analysis
def analyze_sentiment(text):
    tokenizer = AutoTokenizer.from_pretrained(SENTIMENT_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(SENTIMENT_MODEL)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    return torch.nn.functional.softmax(outputs.logits, dim=1).detach().numpy()[0]

# Background Sound Detection
def detect_background_noise(wav_path):
    y, sr = librosa.load(wav_path)
    noise_features = {
        "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(y)),
        "spectral_centroid": np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
        "rmse": np.mean(librosa.feature.rms(y=y))
    }
    return noise_features

# Key Topic Extraction
def extract_key_topics(text):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=10)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return keywords, entities

# Summary Generation
def generate_summary(text):
    tokenizer = BartTokenizer.from_pretrained(SUMMARY_MODEL)
    model = BartForConditionalGeneration.from_pretrained(SUMMARY_MODEL)
    inputs = tokenizer(text, max_length=1024, return_tensors="pt", truncation=True)
    summary_ids = model.generate(inputs.input_ids, num_beams=4, max_length=200, min_length=30, length_penalty=2.0)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Evaluation Metrics (requires labeled data)
def calculate_metrics(y_true, y_pred):
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred, average="weighted"),
        "precision": precision_score(y_true, y_pred, average="weighted")
    }

# Main Pipeline
def process_call(mp3_path):
    # Step 1: Convert MP3 to WAV
    wav_path = convert_mp3_to_wav(mp3_path)
    
    # Step 2: Transcribe Audio
    transcription = transcribe_audio(wav_path)
    
    # Step 3: Speaker Diarization
    diarization = diarize_audio(wav_path)
    
    # Step 4: Sentiment Analysis
    sentiment = analyze_sentiment(transcription)
    
    # Step 5: Background Noise Detection
    noise_features = detect_background_noise(wav_path)
    
    # Step 6: Key Topic Extraction
    keywords, entities = extract_key_topics(transcription)
    
    # Step 7: Summary Generation
    summary = generate_summary(transcription)
    
    # Optional: Evaluation (requires labeled data)
    # metrics = calculate_metrics(y_true, y_pred)
    
    return {
        "transcription": transcription,
        "diarization": diarization,
        "sentiment": sentiment,
        "noise_features": noise_features,
        "keywords": keywords,
        "entities": entities,
        "summary": summary
    }
if _name_ == "_main_":
    results = process_call("input.mp3")
    
    print("Transcription:\n", results["transcription"])
    print("\nDiarization:\n", results["diarization"])
    print("\nSentiment (Neg, Neu, Pos):\n", results["sentiment"])
    print("\nNoise Features:\n", results["noise_features"])
    print("\nKeywords:\n", results["keywords"])
    print("\nSummary:\n", results["summary"])
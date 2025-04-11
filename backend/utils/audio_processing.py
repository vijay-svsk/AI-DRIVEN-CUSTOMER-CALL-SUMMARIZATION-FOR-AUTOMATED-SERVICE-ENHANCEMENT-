import os
import librosa
import numpy as np
import torch
from pydub import AudioSegment
from speechbrain.pretrained import SepformerSeparation as separator
from pyannote.audio.pipelines import SpeakerDiarization
from pyannote.audio.core.io import Audio
from pyannote.core import Segment
import whisper
from pyannote.audio import Pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization",
    use_auth_token="YOUR_HUGGINGFACE_TOKEN"
)


class AudioProcessor:
    def __init__(self, model_path: str = "pyannote/speaker-diarization", sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.diarization_pipeline = SpeakerDiarization.from_pretrained(model_path)
        self.separation_model = separator.from_hparams(source="speechbrain/sepformer-wham", savedir="tmp_model")
        self.transcription_model = whisper.load_model("base")

    def load_audio(self, file_path: str):
        """Loads an audio file and converts it to the required format."""
        if not os.path.exists(file_path):
            raise FileNotFoundError("Audio file not found")
        
        audio, sr = librosa.load(file_path, sr=self.sample_rate)
        return audio, sr

    def perform_diarization(self, file_path: str):
        """Performs speaker diarization and returns speaker segments."""
        audio = Audio(file_path)
        diarization = self.diarization_pipeline({'uri': file_path, 'audio': audio})
        speaker_data = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            speaker_data.append({
                "speaker": speaker,
                "start": turn.start,
                "end": turn.end
            })
        return speaker_data

    def denoise_audio(self, file_path: str, output_path: str):
        """Applies speech separation to enhance voice clarity."""
        audio = AudioSegment.from_file(file_path)
        audio.export("temp.wav", format="wav")
        est_sources = self.separation_model.separate_file("temp.wav")
        enhanced_audio = np.mean(est_sources.squeeze().numpy(), axis=0)
        librosa.save(output_path, enhanced_audio, self.sample_rate)
        return output_path
    
    def transcribe_audio(self, file_path: str):
        """Transcribes speech to text using Whisper ASR model."""
        result = self.transcription_model.transcribe(file_path)
        return result["text"]
    
    def process_audio(self, file_path: str):
        """Runs full processing: diarization, denoising, transcription."""
        cleaned_audio_path = "cleaned_" + os.path.basename(file_path)
        self.denoise_audio(file_path, cleaned_audio_path)
        transcript = self.transcribe_audio(cleaned_audio_path)
        speaker_data = self.perform_diarization(file_path)
        return {"transcript": transcript, "speaker_data": speaker_data}

# Example usage
if __name__ == "__main__":
    processor = AudioProcessor()
    audio_file = "sample_call.wav"
    results = processor.process_audio(audio_file)
    print("Transcription:", results["transcript"])
    print("Speaker Data:", results["speaker_data"])

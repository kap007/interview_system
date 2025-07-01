# ================================
# 3. transcription_service.py
# Handles all transcription using Whisper
# ================================

import torch
from faster_whisper import WhisperModel

class TranscriptionService:
    def __init__(self, model_size="large-v3"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.compute_type = "float16" if self.device == "cuda" else "int8"
        self.model = self._load_model(model_size)
    
    def _load_model(self, model_size):
        """Load Whisper model"""
        try:
            model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)
            print(f"✅ Whisper {model_size} model loaded on {self.device}")
            return model
        except Exception as e:
            print(f"❌ Error loading Whisper model: {e}")
            return None
    
    def transcribe(self, audio_path):
        """Transcribe audio file"""
        if not self.model:
            return "", [], None
        
        try:
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5,
                language="en",
                condition_on_previous_text=False,
                word_timestamps=True,
                vad_filter=True
            )
            
            transcript = ""
            detailed_segments = []
            
            for segment in segments:
                text = segment.text.strip()
                transcript += text + " "
                detailed_segments.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': text
                })
            
            return transcript.strip(), detailed_segments, info
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return "", [], None

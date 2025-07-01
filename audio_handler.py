# ================================
# 1. audio_handler.py
# Handles all audio recording and processing
# ================================

import os
import wave
import threading
import pyaudio
import numpy as np
from pydub import AudioSegment

class AudioHandler:
    def __init__(self, chunk_size=1024, format=pyaudio.paInt16, channels=1, rate=44100, voice_threshold=500):
        self.chunk_size = chunk_size
        self.format = format
        self.channels = channels
        self.rate = rate
        self.voice_threshold = voice_threshold
        
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.is_monitoring = False
        self.audio_data = []
        
    def start_monitoring(self, callback=None):
        """Start monitoring for voice activity"""
        self.is_monitoring = True
        
        def monitor():
            stream = self.audio.open(
                format=self.format, channels=self.channels, rate=self.rate,
                input=True, frames_per_buffer=self.chunk_size
            )
            
            consecutive_speech = 0
            while self.is_monitoring:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    volume = np.abs(np.frombuffer(data, dtype=np.int16)).mean()
                    
                    if volume > self.voice_threshold:
                        consecutive_speech += 1
                        if consecutive_speech >= 5 and callback:
                            callback()  # Trigger callback when speech detected
                            break
                    else:
                        consecutive_speech = 0
                except:
                    break
                    
            stream.stop_stream()
            stream.close()
            
        threading.Thread(target=monitor, daemon=True).start()
    
    def start_recording(self):
        """Start recording audio"""
        self.is_recording = True
        self.audio_data = []
        threading.Thread(target=self._record_audio, daemon=True).start()
        
    def _record_audio(self):
        """Internal recording method"""
        stream = self.audio.open(
            format=self.format, channels=self.channels, rate=self.rate,
            input=True, frames_per_buffer=self.chunk_size
        )
        
        while self.is_recording:
            try:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.append(data)
            except:
                break
                
        stream.stop_stream()
        stream.close()
    
    def stop_recording(self):
        """Stop recording and return audio data"""
        self.is_recording = False
        self.is_monitoring = False
        return self.audio_data
    
    def save_audio(self, audio_data, output_path, format='mp3'):
        """Save audio data to file"""
        # Save as WAV first
        wav_path = output_path.replace('.mp3', '.wav')
        
        with wave.open(wav_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(audio_data))
        
        # Convert to MP3 if requested
        if format == 'mp3':
            audio = AudioSegment.from_wav(wav_path)
            audio.export(output_path, format="mp3", bitrate="192k")
            os.remove(wav_path)
        
        return output_path
    
    def cleanup(self):
        """Clean up audio resources"""
        if hasattr(self, 'audio'):
            self.audio.terminate()




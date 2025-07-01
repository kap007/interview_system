# ================================
# 2. speech_analyzer.py
# Handles all speech analysis (fillers, gaps, fluency)
# ================================

import re
from collections import defaultdict
import numpy as np

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import librosa
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    AUDIO_ANALYSIS_AVAILABLE = True
except ImportError:
    AUDIO_ANALYSIS_AVAILABLE = False

class FillerDetector:
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                pass
        
        self.filler_words = {
            'hesitation': ['uh', 'um', 'er', 'ah', 'eh', 'mm', 'hmm'],
            'discourse_markers': ['like', 'you know', 'i mean', 'you see', 'right', 'okay'],
            'qualification': ['sort of', 'kind of', 'pretty much', 'more or less', 'basically', 'essentially'],
            'intensifiers': ['literally', 'actually', 'really', 'totally', 'absolutely', 'definitely'],
            'stalling': ['well', 'so', 'now', 'then', 'anyway', 'anyhow'],
        }
        
        self.all_fillers = set()
        for category in self.filler_words.values():
            self.all_fillers.update(category)
        
        self.multi_word_patterns = [
            r'\byou know\b', r'\bi mean\b', r'\byou see\b',
            r'\bsort of\b', r'\bkind of\b', r'\bpretty much\b', r'\bmore or less\b'
        ]
    
    def detect_fillers(self, text):
        """Detect filler words in text"""
        if not text:
            return {'total_count': 0, 'details': {}, 'categories': {}}
        
        text_lower = text.lower()
        results = defaultdict(int)
        categories = defaultdict(int)
        
        # Regex-based detection
        for filler in self.all_fillers:
            if ' ' not in filler:
                pattern = r'\b' + re.escape(filler) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                if matches > 0:
                    results[filler] = matches
                    for cat, words in self.filler_words.items():
                        if filler in words:
                            categories[cat] += matches
                            break
        
        # Multi-word phrases
        for pattern in self.multi_word_patterns:
            matches = len(re.findall(pattern, text_lower))
            if matches > 0:
                phrase = pattern.replace(r'\b', '').replace(r'\\', '')
                results[phrase] = matches
                categories['discourse_markers'] += matches
        
        # spaCy enhancement
        if self.nlp:
            spacy_results = self._spacy_detection(text)
            for filler, count in spacy_results.items():
                if filler in results:
                    results[filler] = max(results[filler], count)
                else:
                    results[filler] = count
        
        # Repetition detection
        repetitions = self._detect_repetitions(text)
        if repetitions > 0:
            results['repetitions'] = repetitions
            categories['repetitions'] = repetitions
        
        return {
            'total_count': sum(results.values()),
            'details': dict(results),
            'categories': dict(categories)
        }
    
    def _spacy_detection(self, text):
        """Enhanced detection using spaCy"""
        doc = self.nlp(text)
        results = defaultdict(int)
        
        for token in doc:
            token_lower = token.text.lower()
            if token_lower in self.all_fillers:
                if (token.pos_ == 'INTJ' or token.dep_ in ['intj', 'discourse'] or 
                    token.i == 0 or (token.i > 0 and token.nbor(-1).is_punct)):
                    results[token_lower] += 1
        
        return dict(results)
    
    def _detect_repetitions(self, text):
        """Detect word repetitions"""
        words = text.lower().split()
        repetitions = 0
        
        for i in range(len(words) - 1):
            if words[i] == words[i + 1] and len(words[i]) > 2:
                repetitions += 1
        
        return repetitions

class GapAnalyzer:
    def __init__(self, silence_threshold=0.01, min_pause_duration=0.5, significant_pause_duration=2.0):
        self.silence_threshold = silence_threshold
        self.min_pause_duration = min_pause_duration
        self.significant_pause_duration = significant_pause_duration
    
    def analyze_gaps(self, audio_path):
        """Analyze pauses and gaps in audio"""
        if not AUDIO_ANALYSIS_AVAILABLE:
            return self._empty_analysis()
        
        try:
            y, sr = librosa.load(audio_path, sr=None)
            
            # Calculate RMS energy
            frame_length = int(0.025 * sr)
            hop_length = int(0.010 * sr)
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)
            
            # Detect speech/silence
            is_speech = rms > self.silence_threshold
            pauses = self._find_pauses(times, is_speech)
            
            total_duration = len(y) / sr
            frame_duration = times[1] - times[0] if len(times) > 1 else 0.01
            speech_duration = sum(frame_duration for speech in is_speech if speech)
            silence_duration = total_duration - speech_duration
            
            return {
                'total_duration': total_duration,
                'speech_duration': speech_duration,
                'silence_duration': silence_duration,
                'speech_ratio': speech_duration / total_duration if total_duration > 0 else 0,
                'pause_count': len(pauses),
                'pauses': pauses,
                'pause_analysis': self._analyze_pause_patterns(pauses)
            }
            
        except Exception as e:
            print(f"Gap analysis error: {e}")
            return self._empty_analysis()
    
    def _find_pauses(self, times, is_speech):
        """Find pause segments"""
        pauses = []
        in_pause = False
        pause_start = None
        
        for time, speech in zip(times, is_speech):
            if not speech and not in_pause:
                in_pause = True
                pause_start = time
            elif speech and in_pause:
                pause_duration = time - pause_start
                if pause_duration >= self.min_pause_duration:
                    pauses.append({
                        'start': pause_start,
                        'end': time,
                        'duration': pause_duration,
                        'type': 'significant' if pause_duration >= self.significant_pause_duration else 'normal'
                    })
                in_pause = False
        
        return pauses
    
    def _analyze_pause_patterns(self, pauses):
        """Analyze pause patterns"""
        if not pauses:
            return {
                'avg_pause_duration': 0,
                'max_pause_duration': 0,
                'significant_pauses': 0
            }
        
        durations = [p['duration'] for p in pauses]
        significant_pauses = sum(1 for p in pauses if p['type'] == 'significant')
        
        return {
            'avg_pause_duration': np.mean(durations),
            'max_pause_duration': max(durations),
            'significant_pauses': significant_pauses
        }
    
    def _empty_analysis(self):
        """Return empty analysis when processing fails"""
        return {
            'total_duration': 0,
            'speech_duration': 0,
            'silence_duration': 0,
            'speech_ratio': 0,
            'pause_count': 0,
            'pauses': [],
            'pause_analysis': {
                'avg_pause_duration': 0,
                'max_pause_duration': 0,
                'significant_pauses': 0
            }
        }

class SpeechAnalyzer:
    def __init__(self):
        self.filler_detector = FillerDetector()
        self.gap_analyzer = GapAnalyzer()
    
    def analyze_speech(self, transcript, audio_path=None):
        """Complete speech analysis combining all methods"""
        if not transcript:
            return self._empty_analysis()
        
        # Basic metrics
        words = transcript.split()
        word_count = len(words)
        
        # Filler analysis
        filler_analysis = self.filler_detector.detect_fillers(transcript)
        filler_count = filler_analysis['total_count']
        filler_ratio = (filler_count / word_count * 100) if word_count > 0 else 0
        
        # Gap analysis (if audio available)
        gap_analysis = None
        speech_rate = 0
        adjusted_fluency = 0
        
        if audio_path and AUDIO_ANALYSIS_AVAILABLE:
            gap_analysis = self.gap_analyzer.analyze_gaps(audio_path)
            speech_duration_minutes = gap_analysis['speech_duration'] / 60
            speech_rate = word_count / speech_duration_minutes if speech_duration_minutes > 0 else 0
        
        # Calculate fluency scores
        base_fluency = max(0, 100 - (filler_ratio * 1.5))
        
        if gap_analysis:
            silence_penalty = min((1 - gap_analysis['speech_ratio']) * 30, 20)
            pause_penalty = min(gap_analysis['pause_analysis']['significant_pauses'] * 5, 15)
            
            rate_penalty = 0
            if speech_rate > 0:
                if speech_rate < 100:
                    rate_penalty = (100 - speech_rate) / 10
                elif speech_rate > 200:
                    rate_penalty = (speech_rate - 200) / 20
            
            adjusted_fluency = max(0, base_fluency - silence_penalty - pause_penalty - rate_penalty)
        else:
            adjusted_fluency = base_fluency
        
        return {
            'word_count': word_count,
            'filler_count': filler_count,
            'filler_ratio': round(filler_ratio, 1),
            'filler_details': filler_analysis['details'],
            'filler_categories': filler_analysis['categories'],
            'fluency_score': round(base_fluency, 1),
            'adjusted_fluency_score': round(adjusted_fluency, 1),
            'speech_rate_wpm': round(speech_rate, 1) if speech_rate > 0 else None,
            'gap_analysis': gap_analysis,
            'pause_summary': self._create_pause_summary(gap_analysis) if gap_analysis else None
        }
    
    def _create_pause_summary(self, gap_analysis):
        """Create pause summary from gap analysis"""
        return {
            'total_pauses': gap_analysis['pause_count'],
            'significant_pauses': gap_analysis['pause_analysis']['significant_pauses'],
            'avg_pause_duration': round(gap_analysis['pause_analysis']['avg_pause_duration'], 2),
            'max_pause_duration': round(gap_analysis['pause_analysis']['max_pause_duration'], 2),
            'speech_ratio': round(gap_analysis['speech_ratio'] * 100, 1)
        }
    
    def _empty_analysis(self):
        """Return empty analysis"""
        return {
            'word_count': 0,
            'filler_count': 0,
            'filler_ratio': 0,
            'filler_details': {},
            'filler_categories': {},
            'fluency_score': 0,
            'adjusted_fluency_score': 0,
            'speech_rate_wpm': None,
            'gap_analysis': None,
            'pause_summary': None
        }

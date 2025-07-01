# ================================
# 6. main_interview_system.py
# Main orchestrator that ties everything together
# ================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import pyttsx3
import threading
import time
from datetime import datetime
import os

# Import our modular components
from audio_handler import AudioHandler
from speech_analyzer import SpeechAnalyzer
from transcription_service import TranscriptionService
from timing_analyzer import TimingAnalyzer
from report_generator import ReportGenerator

class InterviewSystem:
    def __init__(self):
        # Initialize all components
        self.audio_handler = AudioHandler()
        self.speech_analyzer = SpeechAnalyzer()
        self.transcription_service = TranscriptionService()
        self.timing_analyzer = TimingAnalyzer()
        self.report_generator = ReportGenerator()
        
        # Initialize TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
        
        # Interview state
        self.current_question = 0
        self.questions = self._load_default_questions()
        self.session_folder = ""
        self.session_data = {
            'candidate_name': '',
            'session_start': None,
            'questions_data': []
        }

        self.auto_recording = False
        self.silence_timeout_timer = None
        self.SILENCE_TIMEOUT = 30
        
        self.setup_gui()
    
    def _load_default_questions(self):
        return [
            "Tell me about yourself and your background.",
            "Why are you interested in this position?",
            "What are your greatest strengths?",
            "Describe a challenging situation you faced and how you handled it.",
            "What is your biggest weakness?",
            "Where do you see yourself in five years?",
            "Why should we hire you?",
            "Describe a time when you worked in a team.",
            "How do you handle stress and pressure?",
            "Do you have any questions for us?"
        ]
    
    def setup_gui(self):
        """Setup the main GUI with automated recording"""
        self.root = tk.Tk()
        self.root.title("Automated Interview System")
        self.root.geometry("800x600")
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Candidate info (unchanged)
        info_frame = ttk.LabelFrame(main_frame, text="Candidate Information", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(info_frame, text="Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.candidate_name = tk.StringVar()
        ttk.Entry(info_frame, textvariable=self.candidate_name, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(info_frame, text="Save to:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.folder_label = ttk.Label(info_frame, text="Select folder", foreground="gray")
        self.folder_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Button(info_frame, text="Browse", command=self.select_folder).grid(row=1, column=2, padx=5)
        
        # Question display (unchanged)
        question_frame = ttk.LabelFrame(main_frame, text="Current Question", padding="10")
        question_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.question_text = scrolledtext.ScrolledText(question_frame, height=5, width=70, wrap=tk.WORD)
        self.question_text.grid(row=0, column=0, pady=5)
        
        # === SIMPLIFIED CONTROLS (No Start/Stop Recording buttons) ===
        control_frame = ttk.Frame(question_frame)
        control_frame.grid(row=1, column=0, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="Start Interview", command=self.start_interview)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.speak_btn = ttk.Button(control_frame, text="Speak Question", command=self.speak_question, state='disabled')
        self.speak_btn.grid(row=0, column=1, padx=5)
        
        # REMOVED: Start Recording and Stop Recording buttons
        
        self.next_btn = ttk.Button(control_frame, text="Next Question", command=self.next_question, state='disabled')
        self.next_btn.grid(row=0, column=2, padx=5)
        
        self.finish_btn = ttk.Button(control_frame, text="Finish Interview", command=self.finish_interview, state='disabled')
        self.finish_btn.grid(row=0, column=3, padx=5)
        
        # === ENHANCED STATUS with Recording Indicator ===
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, pady=10)
        
        self.status_label = ttk.Label(status_frame, text="Ready to start", font=('Arial', 12))
        self.status_label.grid(row=0, column=0)
        
        # Enhanced recording indicator
        self.recording_indicator = ttk.Label(status_frame, text="⚫", foreground="gray", font=('Arial', 20))
        self.recording_indicator.grid(row=0, column=1, padx=20)
        
        self.recording_status = ttk.Label(status_frame, text="", font=('Arial', 10, 'italic'), foreground="gray")
        self.recording_status.grid(row=1, column=0, columnspan=2)
        
        # Progress (unchanged)
        self.progress_label = ttk.Label(main_frame, text="Question 0 of 0")
        self.progress_label.grid(row=3, column=0, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode='determinate')
        self.progress_bar.grid(row=4, column=0, pady=5)
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def select_folder(self):
        """Select folder for saving interview data"""
        folder = filedialog.askdirectory()
        if folder:
            self.session_folder = folder
            self.folder_label.config(text=f"✓ {os.path.basename(folder)}", foreground="green")
    
    def start_interview(self):
        """Start the interview process"""
        if not self.candidate_name.get().strip():
            messagebox.showerror("Error", "Please enter candidate name")
            return
        if not self.session_folder:
            messagebox.showerror("Error", "Please select save folder")
            return
        
        # Create session folder
        candidate_folder = f"{self.candidate_name.get().strip()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.candidate_session_folder = os.path.join(self.session_folder, candidate_folder)
        os.makedirs(self.candidate_session_folder, exist_ok=True)
        
        # Initialize session
        self.session_data['candidate_name'] = self.candidate_name.get().strip()
        self.session_data['session_start'] = datetime.now()
        self.current_question = 0
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.speak_btn.config(state='normal')
        self.finish_btn.config(state='normal')
        
        self.display_current_question()
        self.update_progress()
        self.status_label.config(text="Interview started")
    
    def display_current_question(self):
        """Display current question in the GUI"""
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(tk.END, f"Question {self.current_question + 1}: {question}")
    
    def speak_question(self):
        """Speak the current question and auto-start recording"""
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            self.status_label.config(text="🗣️ Speaking question...")
            self.recording_status.config(text="")
            
            def speak():
                self.tts_engine.say(question)
                self.tts_engine.runAndWait()
                # Mark timing when question finished
                self.timing_analyzer.mark_question_spoken()
                # Auto-start recording after question
                self.root.after(0, self.auto_start_recording)
            
            threading.Thread(target=speak, daemon=True).start()
    
    def auto_start_recording(self):
        """Automatically start recording after question is spoken"""
        self.speak_btn.config(state='disabled')
        self.next_btn.config(state='normal')
        # Visual feedback for auto-recording
        self.status_label.config(text="🎤 Recording your answer...")
        self.recording_indicator.config(text="🔴", foreground="red")
        self.recording_status.config(text="Recording started automatically - speak your answer", foreground="blue")
        # Start actual recording
        self.auto_recording = True
        self.audio_handler.start_recording()
        # Start monitoring for first speech
        self.audio_handler.start_monitoring(callback=self.timing_analyzer.mark_first_speech)
        # Start silence timeout timer
        self.start_silence_timeout()

    def start_silence_timeout(self):
        """Start 30-second timeout for no speech detection"""
        def timeout_handler():
            if self.auto_recording and not self.timing_analyzer.first_speech_time:
                # No speech detected in 30 seconds - auto skip
                self.root.after(0, self.handle_silence_timeout)
        
        self.silence_timeout_timer = threading.Timer(self.SILENCE_TIMEOUT, timeout_handler)
        self.silence_timeout_timer.start()
    
    def enable_recording(self):
        """Enable recording after question is spoken"""
        self.speak_btn.config(state='disabled')
        self.record_btn.config(state='normal')
        self.status_label.config(text="Ready to record answer")
        
        # Start monitoring for first speech
        self.audio_handler.start_monitoring(callback=self.timing_analyzer.mark_first_speech)
    
    def handle_silence_timeout(self):
        """Handle case where user doesn't speak for 30 seconds"""
        if self.auto_recording:
            # Stop recording
            self.auto_recording = False
            audio_data = self.audio_handler.stop_recording()
            
            # Cancel timeout timer
            if self.silence_timeout_timer:
                self.silence_timeout_timer.cancel()
            
            # Update UI
            self.recording_indicator.config(text="⚫", foreground="gray")
            self.status_label.config(text="⏭️ No response detected - moving to next question")
            self.recording_status.config(text="Skipped due to no response within 30 seconds", foreground="orange")
            
            # Create zero-confidence evaluation
            confidence_evaluation = {
                'response_time': None,
                'confidence_level': 'No Response',
                'explanation': 'No speech detected within 30 seconds - question skipped'
            }
            
            # Create minimal speech analysis
            speech_analysis = {
                'word_count': 0,
                'filler_count': 0,
                'filler_ratio': 0,
                'filler_details': {},
                'filler_categories': {},
                'fluency_score': 0,
                'adjusted_fluency_score': 0
            }
            
            # Save question data with zero scores
            question_num = self.current_question + 1
            question_data = {
                'question_number': question_num,
                'question_text': self.questions[self.current_question],
                'audio_file': None,
                'transcript': "",
                'confidence_evaluation': confidence_evaluation,
                'speech_analysis': speech_analysis,
                'audio_duration': 0,
                'transcript_segments': []
            }
            
            self.session_data['questions_data'].append(question_data)
            
            # Reset timing
            self.timing_analyzer.reset()
            
            # Auto-move to next question after 2 seconds
            self.root.after(2000, self.auto_next_question)

    def start_recording(self):
        """Start recording candidate's answer"""
        self.record_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.recording_indicator.config(text="🔴", foreground="red")
        self.status_label.config(text="Recording...")
        
        self.audio_handler.start_recording()
    
    def stop_recording(self):
        """Stop recording and process the answer"""
    # === NEW: Mark when answer ended ===
        self.timing_analyzer.mark_answer_end()
        self.stop_btn.config(state='disabled')
        self.recording_indicator.config(text="⚫", foreground="gray")
        self.status_label.config(text="Processing...")
        audio_data = self.audio_handler.stop_recording()
    
        if audio_data:
            threading.Thread(target=self.process_answer, args=(audio_data,), daemon=True).start()
        else:
            self.enable_next()
    
    def process_answer(self, audio_data):
        """Process the recorded answer with automated flow"""
        try:
            question_num = self.current_question + 1
            mp3_path = os.path.join(self.candidate_session_folder, f"Q{question_num:02d}_answer.mp3")
            
            # Save audio file
            self.audio_handler.save_audio(audio_data, mp3_path)
            
            # Transcribe audio
            transcript, segments, info = self.transcription_service.transcribe(mp3_path)
            
            # Analyze timing/confidence
            confidence_evaluation = self.timing_analyzer.evaluate_confidence()
            
            # Analyze speech (fillers, gaps, fluency)
            speech_analysis = self.speech_analyzer.analyze_speech(transcript, mp3_path)
            
            # Save question data
            question_data = {
                'question_number': question_num,
                'question_text': self.questions[self.current_question],
                'audio_file': os.path.basename(mp3_path),
                'transcript': transcript,
                'confidence_evaluation': confidence_evaluation,
                'speech_analysis': speech_analysis,
                'audio_duration': info.duration if info else 0,
                'transcript_segments': segments
            }
            
            self.session_data['questions_data'].append(question_data)
            
            # Reset timing for next question
            self.timing_analyzer.reset()
            
            # Continue to next question
            self.root.after(0, self.auto_next_question)
            
        except Exception as e:
            print(f"Processing error: {e}")
            self.root.after(0, self.auto_next_question)
    
    def enable_next(self):
        """Enable next question button"""
        self.next_btn.config(state='normal')
        self.status_label.config(text="Question complete")
    
    def next_question(self):
        """Process current answer and move to next question"""
        if self.auto_recording:
            # Stop recording and process
            self.auto_recording = False
            audio_data = self.audio_handler.stop_recording()
            
            # Cancel timeout timer
            if self.silence_timeout_timer:
                self.silence_timeout_timer.cancel()
            
            # Update UI
            self.next_btn.config(state='disabled')
            self.recording_indicator.config(text="⚫", foreground="gray")
            self.status_label.config(text="📝 Processing your answer...")
            self.recording_status.config(text="Processing...", foreground="gray")
            
            if audio_data:
                threading.Thread(target=self.process_answer, args=(audio_data,), daemon=True).start()
            else:
                self.auto_next_question()
        else:
            # Already processed or skipped
            self.auto_next_question()
    
    def auto_next_question(self):
        """Automatically move to next question"""
        self.current_question += 1
        
        if self.current_question < len(self.questions):
            # More questions available
            self.speak_btn.config(state='normal')
            self.next_btn.config(state='disabled')
            
            self.display_current_question()
            self.update_progress()
            self.status_label.config(text="✅ Ready for next question")
            self.recording_status.config(text="Click 'Speak Question' to continue", foreground="green")
        else:
            # No more questions - finish interview
            self.finish_interview()
    
    def update_progress(self):
        """Update progress indicators"""
        total = len(self.questions)
        current = min(self.current_question + 1, total)
        
        self.progress_label.config(text=f"Question {current} of {total}")
        self.progress_bar['value'] = (self.current_question / total) * 100
    
    def finish_interview(self):
        """Finish interview with automated flow"""
        # Ensure recording is stopped
        if self.auto_recording:
            self.auto_recording = False
            self.audio_handler.stop_recording()
        
        # Cancel any running timers
        if self.silence_timeout_timer:
            self.silence_timeout_timer.cancel()
        
        self.status_label.config(text="📊 Generating reports...")
        self.recording_status.config(text="Interview completed", foreground="green")
        
        # Generate comprehensive reports
        self.report_generator.generate_reports(self.session_data, self.candidate_session_folder)
        
        # Disable all controls
        for widget in [self.speak_btn, self.next_btn, self.finish_btn]:
            widget.config(state='disabled')
        
        self.status_label.config(text="✅ Interview completed!")
        self.recording_status.config(text="Reports generated successfully", foreground="green")
        messagebox.showinfo("Complete", f"Interview completed!\nReports saved to: {self.candidate_session_folder}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
    
    def cleanup(self):
        """Clean up resources including timers"""
        if self.silence_timeout_timer:
            self.silence_timeout_timer.cancel()
        self.audio_handler.cleanup()

def main():
    print("🎯 MODULAR INTERVIEW SYSTEM")
    print("=" * 40)
    print("Components loaded:")
    print("✅ Audio Handler - Recording & monitoring")
    print("✅ Speech Analyzer - Fillers, gaps, fluency")
    print("✅ Transcription Service - Whisper AI")
    print("✅ Timing Analyzer - Response confidence")
    print("✅ Report Generator - Comprehensive analysis")
    print()
    
    # Check dependencies
    missing_deps = []
    
    try:
        import spacy
        try:
            spacy.load("en_core_web_sm")
            print("✅ spaCy - Advanced filler detection available")
        except OSError:
            print("⚠️  spaCy model missing - Basic filler detection will be used")
            print("   Install: python -m spacy download en_core_web_sm")
    except ImportError:
        print("⚠️  spaCy not installed - Basic filler detection will be used")
        missing_deps.append("spacy")
    
    try:
        import librosa
        print("✅ librosa - Gap analysis available")
    except ImportError:
        print("⚠️  librosa not installed - No gap analysis")
        missing_deps.append("librosa")
    
    try:
        import matplotlib
        print("✅ matplotlib - Visualization available")
    except ImportError:
        print("⚠️  matplotlib not installed - No visualizations")
        missing_deps.append("matplotlib")
    
    if missing_deps:
        print(f"\n📦 Optional packages to install: pip install {' '.join(missing_deps)}")
    
    print("\n🚀 Starting interview system...")
    
    try:
        system = InterviewSystem()
        system.run()
        system.cleanup()
    except ImportError as e:
        print(f"❌ Missing required packages: {e}")
        print("Install: pip install faster-whisper pyaudio numpy pydub pyttsx3")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

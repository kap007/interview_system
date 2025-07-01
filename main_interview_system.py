# ================================
# UPDATED main_interview_system.py - SEPARATE INTERVIEWER/CANDIDATE VIEWS
# Analysis hidden from candidate, shown only to interviewer
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
from answer_evaluator import AdvancedKeywordEvaluator

class InterviewSystem:
    def __init__(self):
        # Initialize all components
        self.audio_handler = AudioHandler()
        self.speech_analyzer = SpeechAnalyzer()
        self.transcription_service = TranscriptionService()
        self.timing_analyzer = TimingAnalyzer()
        self.report_generator = ReportGenerator()
        self.answer_evaluator = AdvancedKeywordEvaluator()

        # Initialize TTS
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.9)
        
        # Add automated recording control
        self.auto_recording = False
        self.silence_timeout_timer = None
        self.SILENCE_TIMEOUT = 30  # 30 seconds timeout
        
        # Interview state
        self.current_question = 0
        self.questions = self._load_default_questions()
        self.session_folder = ""
        self.session_data = {
            'candidate_name': '',
            'session_start': None,
            'questions_data': []
        }
        
        # UI Mode: 'candidate' or 'interviewer'
        self.ui_mode = 'candidate'  # Default to candidate view
        self.interviewer_window = None
        
        self.setup_main_gui()
    
    def _load_default_questions(self):
        """Load Python/SQL specific interview questions"""
        return [
        "Tell me about your experience with Python programming and what projects you've worked on.",
        "Explain the difference between lists and tuples in Python. When would you use each?",
        "How do you handle exceptions in Python? Can you give me an example?",
        "What is the difference between SQL JOIN types? Explain INNER, LEFT, RIGHT, and OUTER joins.",
        "How would you optimize a slow SQL query? What steps would you take?",
        "Explain Python decorators. How do they work and when would you use them?",
        "What are Python generators and how do they differ from regular functions?",
        "How do you prevent SQL injection attacks? What best practices do you follow?",
        "Describe your experience with Python libraries like pandas, numpy, or requests.",
        "How would you design a database schema for an e-commerce application?"
        ]   
    
    def setup_main_gui(self):
        """Setup the main candidate-facing GUI (clean, minimal)"""
        self.root = tk.Tk()
        self.root.title("Interview System - Candidate View")
        self.root.geometry("800x600")
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Mode selection at the top (for setup only)
        mode_frame = ttk.LabelFrame(main_frame, text="Setup", padding="10")
        mode_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10)
        
        setup_frame = ttk.Frame(mode_frame)
        setup_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Candidate info
        ttk.Label(setup_frame, text="Candidate Name:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.candidate_name = tk.StringVar()
        ttk.Entry(setup_frame, textvariable=self.candidate_name, width=25).grid(row=0, column=1, padx=5)
        
        ttk.Label(setup_frame, text="Save to:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.folder_label = ttk.Label(setup_frame, text="Select folder", foreground="gray")
        self.folder_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Button(setup_frame, text="Browse", command=self.select_folder).grid(row=1, column=2, padx=5)
        
        # Interviewer controls
        interviewer_controls = ttk.Frame(setup_frame)
        interviewer_controls.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.start_btn = ttk.Button(interviewer_controls, text="Start Interview", command=self.start_interview)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        ttk.Button(interviewer_controls, text="Open Interviewer Dashboard", 
                  command=self.open_interviewer_dashboard).grid(row=0, column=1, padx=5)
        
        self.finish_btn = ttk.Button(interviewer_controls, text="Finish Interview", 
                                   command=self.finish_interview, state='disabled')
        self.finish_btn.grid(row=0, column=2, padx=5)
        
        # CANDIDATE VIEW - Clean and simple
        candidate_frame = ttk.LabelFrame(main_frame, text="Interview", padding="20")
        candidate_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        
        # Large, clear question display
        self.question_text = scrolledtext.ScrolledText(
            candidate_frame, height=8, width=80, wrap=tk.WORD, 
            font=('Arial', 14), padx=10, pady=10
        )
        self.question_text.grid(row=0, column=0, pady=20)
        
        # Simple controls for candidate
        candidate_controls = ttk.Frame(candidate_frame)
        candidate_controls.grid(row=1, column=0, pady=20)
        
        self.speak_btn = ttk.Button(
            candidate_controls, text="🔊 Speak Question", 
            command=self.speak_question, state='disabled',
            style='Large.TButton'
        )
        self.speak_btn.grid(row=0, column=0, padx=10)
        
        self.next_btn = ttk.Button(
            candidate_controls, text="Next Question ➡️", 
            command=self.next_question, state='disabled',
            style='Large.TButton'
        )
        self.next_btn.grid(row=0, column=1, padx=10)
        
        # Status display for candidate (minimal, friendly)
        status_frame = ttk.Frame(candidate_frame)
        status_frame.grid(row=2, column=0, pady=20)
        
        self.status_label = ttk.Label(
            status_frame, text="Welcome! Ready to start when you are.", 
            font=('Arial', 16), foreground="blue"
        )
        self.status_label.grid(row=0, column=0)
        
        self.recording_indicator = ttk.Label(
            status_frame, text="⚫", foreground="gray", font=('Arial', 24)
        )
        self.recording_indicator.grid(row=1, column=0, pady=10)
        
        self.recording_status = ttk.Label(
            status_frame, text="", font=('Arial', 12), foreground="gray"
        )
        self.recording_status.grid(row=2, column=0)
        
        # Progress bar for candidate
        progress_frame = ttk.Frame(candidate_frame)
        progress_frame.grid(row=3, column=0, pady=20)
        
        self.progress_label = ttk.Label(progress_frame, text="Question 0 of 0", font=('Arial', 12))
        self.progress_label.grid(row=0, column=0, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=500, mode='determinate', style='Large.Horizontal.TProgressbar')
        self.progress_bar.grid(row=1, column=0, pady=5)
        
        # Configure button styles for better visibility
        style = ttk.Style()
        style.configure('Large.TButton', font=('Arial', 12), padding=10)
        style.configure('Large.Horizontal.TProgressbar', thickness=20)
        
        # Configure grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        candidate_frame.columnconfigure(0, weight=1)
        candidate_frame.rowconfigure(0, weight=1)
    
    def open_interviewer_dashboard(self):
        """Open separate interviewer dashboard window"""
        if self.interviewer_window is not None:
            self.interviewer_window.lift()  # Bring to front if already open
            return
        
        self.interviewer_window = tk.Toplevel(self.root)
        self.interviewer_window.title("Interview System - Interviewer Dashboard")
        self.interviewer_window.geometry("1000x800")
        
        # Handle window closing
        self.interviewer_window.protocol("WM_DELETE_WINDOW", self.close_interviewer_dashboard)
        
        main_frame = ttk.Frame(self.interviewer_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Current question info
        current_frame = ttk.LabelFrame(main_frame, text="Current Question", padding="10")
        current_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.interviewer_question = ttk.Label(current_frame, text="No question active", font=('Arial', 12, 'bold'))
        self.interviewer_question.grid(row=0, column=0, sticky=tk.W)
        
        self.interviewer_status = ttk.Label(current_frame, text="Ready", font=('Arial', 10))
        self.interviewer_status.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Real-time evaluation (LEFT PANEL)
        eval_frame = ttk.LabelFrame(main_frame, text="Real-time Analysis", padding="10")
        eval_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Score display
        score_frame = ttk.Frame(eval_frame)
        score_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(score_frame, text="Content Score:", font=('Arial', 11, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.interviewer_score = ttk.Label(score_frame, text="--/10", font=('Arial', 14, 'bold'), foreground="blue")
        self.interviewer_score.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # Keywords found
        ttk.Label(eval_frame, text="Keywords Detected:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(10,5))
        self.interviewer_keywords = scrolledtext.ScrolledText(eval_frame, height=8, width=45, wrap=tk.WORD, font=('Arial', 9))
        self.interviewer_keywords.grid(row=2, column=0, pady=5)
        
        # Coverage meters
        coverage_frame = ttk.LabelFrame(eval_frame, text="Coverage Analysis", padding="5")
        coverage_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(coverage_frame, text="Essential Keywords:").grid(row=0, column=0, sticky=tk.W)
        self.interviewer_essential = ttk.Progressbar(coverage_frame, length=250, mode='determinate')
        self.interviewer_essential.grid(row=0, column=1, padx=5)
        self.interviewer_essential_label = ttk.Label(coverage_frame, text="0%")
        self.interviewer_essential_label.grid(row=0, column=2)
        
        ttk.Label(coverage_frame, text="Bonus Keywords:").grid(row=1, column=0, sticky=tk.W)
        self.interviewer_bonus = ttk.Progressbar(coverage_frame, length=250, mode='determinate')
        self.interviewer_bonus.grid(row=1, column=1, padx=5)
        self.interviewer_bonus_label = ttk.Label(coverage_frame, text="0%")
        self.interviewer_bonus_label.grid(row=1, column=2)
        
        # Suggestions
        suggestions_frame = ttk.LabelFrame(eval_frame, text="Improvement Notes", padding="5")
        suggestions_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.interviewer_suggestions = scrolledtext.ScrolledText(suggestions_frame, height=5, width=45, wrap=tk.WORD, font=('Arial', 9))
        self.interviewer_suggestions.grid(row=0, column=0)
        
        # Interview summary (RIGHT PANEL)
        summary_frame = ttk.LabelFrame(main_frame, text="Interview Progress", padding="10")
        summary_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Overall stats
        stats_frame = ttk.Frame(summary_frame)
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(stats_frame, text="Overall Performance:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.overall_score = ttk.Label(stats_frame, text="--/10", font=('Arial', 12, 'bold'))
        self.overall_score.grid(row=0, column=1, padx=10)
        
        # Question-by-question summary
        ttk.Label(summary_frame, text="Question Summary:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(10,5))
        self.interviewer_summary = scrolledtext.ScrolledText(summary_frame, height=20, width=45, wrap=tk.WORD, font=('Arial', 9))
        self.interviewer_summary.grid(row=2, column=0, pady=5)
        
        # Quick actions
        actions_frame = ttk.Frame(summary_frame)
        actions_frame.grid(row=3, column=0, pady=10)
        
        ttk.Button(actions_frame, text="Clear Analysis", command=self.clear_interviewer_displays).grid(row=0, column=0, padx=5)
        ttk.Button(actions_frame, text="Export Notes", command=self.export_interviewer_notes).grid(row=0, column=1, padx=5)
        
        # Configure grid weights
        self.interviewer_window.columnconfigure(0, weight=1)
        self.interviewer_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        eval_frame.rowconfigure(2, weight=1)
        summary_frame.rowconfigure(2, weight=1)
    
    def close_interviewer_dashboard(self):
        """Handle interviewer dashboard closing"""
        self.interviewer_window.destroy()
        self.interviewer_window = None
    
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
        
        # Clear displays
        self.clear_interviewer_displays()
        
        # Update UI
        self.start_btn.config(state='disabled')
        self.speak_btn.config(state='normal')
        self.finish_btn.config(state='normal')
        
        self.display_current_question()
        self.update_progress()
        
        # Candidate-friendly status
        self.status_label.config(text="Let's begin! Click 'Speak Question' when ready.", foreground="green")
        
        # Update interviewer dashboard
        if self.interviewer_window:
            self.interviewer_status.config(text="Interview started - Ready for first question")
            self.update_interviewer_summary("Interview started successfully")
    
    def clear_interviewer_displays(self):
        """Clear interviewer dashboard displays"""
        if not self.interviewer_window:
            return
        
        self.interviewer_score.config(text="--/10")
        self.interviewer_keywords.delete(1.0, tk.END)
        self.interviewer_essential['value'] = 0
        self.interviewer_bonus['value'] = 0
        self.interviewer_essential_label.config(text="0%")
        self.interviewer_bonus_label.config(text="0%")
        self.interviewer_suggestions.delete(1.0, tk.END)
        self.overall_score.config(text="--/10")
    
    def display_current_question(self):
        """Display current question in both candidate and interviewer views"""
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            # Candidate view - clean and large
            self.question_text.delete(1.0, tk.END)
            self.question_text.insert(tk.END, f"Question {self.current_question + 1}:\n\n{question}")
            
            # Interviewer view
            if self.interviewer_window:
                self.interviewer_question.config(text=f"Q{self.current_question + 1}: {question}")
                self.interviewer_status.config(text="Question displayed - Ready to speak")
                self.clear_current_evaluation()
    
    def clear_current_evaluation(self):
        """Clear current question evaluation in interviewer view"""
        if not self.interviewer_window:
            return
        
        self.interviewer_score.config(text="--/10")
        self.interviewer_keywords.delete(1.0, tk.END)
        self.interviewer_essential['value'] = 0
        self.interviewer_bonus['value'] = 0
        self.interviewer_essential_label.config(text="0%")
        self.interviewer_bonus_label.config(text="0%")
        self.interviewer_suggestions.delete(1.0, tk.END)
    
    def speak_question(self):
        """Speak the current question and auto-start recording"""
        if self.current_question < len(self.questions):
            question = self.questions[self.current_question]
            
            # Candidate view - simple status
            self.status_label.config(text="🗣️ Listen carefully...", foreground="blue")
            self.recording_status.config(text="")
            
            # Interviewer view
            if self.interviewer_window:
                self.interviewer_status.config(text="Speaking question aloud...")
            
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
        
        # Candidate view - encouraging and clear
        self.status_label.config(text="🎤 Please share your answer", foreground="green")
        self.recording_indicator.config(text="🔴", foreground="red")
        self.recording_status.config(text="Recording... Take your time to give a thoughtful answer", foreground="blue")
        
        # Interviewer view
        if self.interviewer_window:
            self.interviewer_status.config(text="🔴 RECORDING - Candidate is answering")
        
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
    
    def handle_silence_timeout(self):
        """Handle case where user doesn't speak for 30 seconds"""
        if self.auto_recording:
            # Stop recording
            self.auto_recording = False
            audio_data = self.audio_handler.stop_recording()
            
            # Cancel timeout timer
            if self.silence_timeout_timer:
                self.silence_timeout_timer.cancel()
            
            # Candidate view - gentle message
            self.recording_indicator.config(text="⚫", foreground="gray")
            self.status_label.config(text="No response detected. Moving to next question.", foreground="orange")
            self.recording_status.config(text="Don't worry - let's try the next question", foreground="gray")
            
            # Interviewer view
            if self.interviewer_window:
                self.interviewer_status.config(text="❌ No response detected - question skipped")
                self.update_interviewer_evaluation_zero()
            
            # Create evaluation data
            confidence_evaluation = {
                'response_time': None,
                'confidence_level': 'No Response',
                'explanation': 'No speech detected within 30 seconds - question skipped'
            }
            
            speech_analysis = {
                'word_count': 0, 'filler_count': 0, 'filler_ratio': 0,
                'filler_details': {}, 'filler_categories': {},
                'fluency_score': 0, 'adjusted_fluency_score': 0
            }
            
            answer_evaluation = {
                'question_index': self.current_question, 'question_type': 'behavioral', 'combined_score': 0,
                'keyword_evaluation': {
                    'keyword_score': 0,
                    'matches_found': {'exact': {'essential': {}, 'bonus': {}}, 'semantic': {'essential': {}, 'bonus': {}}},
                    'coverage_analysis': {'essential_coverage': 0, 'bonus_coverage': 0},
                    'improvement_suggestions': ['No response provided - encourage candidate to answer']
                },
                'score_breakdown': {'keyword_score': 0, 'scoring_method': 'No Response'}
            }
            
            # Save question data
            question_num = self.current_question + 1
            question_data = {
                'question_number': question_num, 'question_text': self.questions[self.current_question],
                'audio_file': None, 'transcript': "", 'confidence_evaluation': confidence_evaluation,
                'speech_analysis': speech_analysis, 'answer_evaluation': answer_evaluation,
                'audio_duration': 0, 'transcript_segments': []
            }
            
            self.session_data['questions_data'].append(question_data)
            
            # Update interviewer summary
            self.update_interviewer_summary(f"Q{question_num}: No response (0/10)")
            
            # Reset timing
            self.timing_analyzer.reset()
            
            # Auto-move to next question after 3 seconds
            self.root.after(3000, self.auto_next_question)
    
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
            
            # Candidate view - encouraging
            self.status_label.config(text="📝 Thank you! Processing your answer...", foreground="blue")
            self.recording_status.config(text="Great job! Let's move on...", foreground="gray")
            
            # Interviewer view
            if self.interviewer_window:
                self.interviewer_status.config(text="⏳ Processing answer and analyzing content...")
            
            if audio_data:
                threading.Thread(target=self.process_answer, args=(audio_data,), daemon=True).start()
            else:
                self.auto_next_question()
        else:
            # Already processed or skipped
            self.auto_next_question()
    
    def process_answer(self, audio_data):
        """Process the recorded answer (analysis only visible to interviewer)"""
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
            
            # Evaluate answer content (ONLY for interviewer)
            question_index = self.current_question
            answer_evaluation = self.answer_evaluator.evaluate_single_answer(
                question_index, self.questions[question_index], transcript
            )
            
            # Update interviewer dashboard ONLY (not candidate view)
            if self.interviewer_window:
                self.root.after(0, lambda: self.update_interviewer_evaluation(answer_evaluation))
            
            # Save question data
            question_data = {
                'question_number': question_num, 'question_text': self.questions[self.current_question],
                'audio_file': os.path.basename(mp3_path), 'transcript': transcript,
                'confidence_evaluation': confidence_evaluation, 'speech_analysis': speech_analysis,
                'answer_evaluation': answer_evaluation, 'audio_duration': info.duration if info else 0,
                'transcript_segments': segments
            }
            
            self.session_data['questions_data'].append(question_data)
            
            # Update interviewer summary only
            score = answer_evaluation['combined_score']
            self.root.after(0, lambda: self.update_interviewer_summary(
                f"Q{question_num}: {score}/10 ({answer_evaluation['question_type']})"
            ))
            
            # Reset timing for next question
            self.timing_analyzer.reset()
            
            # Continue to next question
            self.root.after(0, self.auto_next_question)
            
        except Exception as e:
            print(f"Processing error: {e}")
            self.root.after(0, self.auto_next_question)
    
    def update_interviewer_evaluation(self, answer_evaluation):
        """Update interviewer dashboard with evaluation (hidden from candidate)"""
        if not self.interviewer_window:
            return
        
        # Update score with color coding
        score = answer_evaluation['combined_score']
        self.interviewer_score.config(text=f"{score}/10")
        
        if score >= 8:
            self.interviewer_score.config(foreground="green")
        elif score >= 6:
            self.interviewer_score.config(foreground="orange")
        else:
            self.interviewer_score.config(foreground="red")
        
        # Update keywords found
        self.interviewer_keywords.delete(1.0, tk.END)
        keyword_eval = answer_evaluation['keyword_evaluation']
        
        keywords_text = "ESSENTIAL KEYWORDS FOUND:\n"
        exact_essential = keyword_eval['matches_found']['exact']['essential']
        for group, keywords in exact_essential.items():
            if keywords:
                keywords_text += f"✓ {group.replace('_', ' ').title()}: {', '.join(keywords)}\n"
        
        keywords_text += "\nBONUS KEYWORDS FOUND:\n"
        exact_bonus = keyword_eval['matches_found']['exact']['bonus']
        for group, keywords in exact_bonus.items():
            if keywords:
                keywords_text += f"+ {group.replace('_', ' ').title()}: {', '.join(keywords)}\n"
        
        # Add semantic matches
        semantic_essential = keyword_eval['matches_found']['semantic']['essential']
        semantic_bonus = keyword_eval['matches_found']['semantic']['bonus']
        
        if any(semantic_essential.values()) or any(semantic_bonus.values()):
            keywords_text += "\nSEMANTIC MATCHES (Related Terms):\n"
            for group, keywords in semantic_essential.items():
                if keywords:
                    keywords_text += f"~ {group.replace('_', ' ').title()}: {', '.join(keywords)}\n"
            for group, keywords in semantic_bonus.items():
                if keywords:
                    keywords_text += f"~ {group.replace('_', ' ').title()}: {', '.join(keywords)}\n"
        
        self.interviewer_keywords.insert(tk.END, keywords_text)
        
        # Update coverage meters
        coverage = keyword_eval['coverage_analysis']
        essential_pct = coverage['essential_coverage']
        bonus_pct = coverage['bonus_coverage']
        
        self.interviewer_essential['value'] = essential_pct
        self.interviewer_bonus['value'] = bonus_pct
        self.interviewer_essential_label.config(text=f"{essential_pct}%")
        self.interviewer_bonus_label.config(text=f"{bonus_pct}%")
        
        # Update suggestions
        self.interviewer_suggestions.delete(1.0, tk.END)
        suggestions = keyword_eval.get('improvement_suggestions', [])
        if suggestions:
            suggestions_text = "AREAS FOR IMPROVEMENT:\n"
            for i, suggestion in enumerate(suggestions, 1):
                suggestions_text += f"{i}. {suggestion}\n"
        else:
            suggestions_text = "✅ EXCELLENT ANSWER!\nNo specific improvements needed."
        
        self.interviewer_suggestions.insert(tk.END, suggestions_text)
        
        # Update overall average score
        self.update_overall_score()
    
    def update_interviewer_evaluation_zero(self):
        """Update interviewer dashboard for no response"""
        if not self.interviewer_window:
            return
        
        self.interviewer_score.config(text="0/10", foreground="red")
        self.interviewer_keywords.delete(1.0, tk.END)
        self.interviewer_keywords.insert(tk.END, "❌ NO RESPONSE DETECTED\n\nCandidate did not provide an answer within the time limit.")
        
        self.interviewer_essential['value'] = 0
        self.interviewer_bonus['value'] = 0
        self.interviewer_essential_label.config(text="0%")
        self.interviewer_bonus_label.config(text="0%")
        
        self.interviewer_suggestions.delete(1.0, tk.END)
        self.interviewer_suggestions.insert(tk.END, "FOLLOW-UP ACTIONS:\n1. Check if candidate understood the question\n2. Consider rephrasing or simplifying\n3. Encourage candidate to take their time")
        
        self.update_overall_score()
    
    def update_interviewer_summary(self, message):
        """Update the interviewer summary panel"""
        if not self.interviewer_window:
            return
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.interviewer_summary.insert(tk.END, f"[{timestamp}] {message}\n")
        self.interviewer_summary.see(tk.END)
    
    def update_overall_score(self):
        """Calculate and display overall interview score for interviewer"""
        if not self.interviewer_window:
            return
        
        if not self.session_data['questions_data']:
            self.overall_score.config(text="--/10")
            return
        
        scores = []
        for q_data in self.session_data['questions_data']:
            if 'answer_evaluation' in q_data:
                scores.append(q_data['answer_evaluation']['combined_score'])
        
        if scores:
            avg_score = sum(scores) / len(scores)
            self.overall_score.config(text=f"{avg_score:.1f}/10")
            
            # Color code overall score
            if avg_score >= 8:
                self.overall_score.config(foreground="green")
            elif avg_score >= 6:
                self.overall_score.config(foreground="orange")
            else:
                self.overall_score.config(foreground="red")
    
    def auto_next_question(self):
        """Automatically move to next question"""
        self.current_question += 1
        
        if self.current_question < len(self.questions):
            # More questions available
            self.speak_btn.config(state='normal')
            self.next_btn.config(state='disabled')
            
            self.display_current_question()
            self.update_progress()
            
            # Candidate view - encouraging
            self.status_label.config(text="✅ Ready for the next question!", foreground="green")
            self.recording_status.config(text="Click 'Speak Question' when you're ready to continue", foreground="blue")
            
            # Interviewer view
            if self.interviewer_window:
                self.interviewer_status.config(text="✅ Ready for next question - Click 'Speak Question'")
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
        """Finish interview with comprehensive analysis for interviewer"""
        # Ensure recording is stopped
        if self.auto_recording:
            self.auto_recording = False
            self.audio_handler.stop_recording()
        
        # Cancel any running timers
        if self.silence_timeout_timer:
            self.silence_timeout_timer.cancel()
        
        # Candidate view - positive and encouraging
        self.status_label.config(text="🎉 Interview completed! Thank you!", foreground="green")
        self.recording_status.config(text="Great job! You've finished all questions.", foreground="green")
        
        # Interviewer view
        if self.interviewer_window:
            self.interviewer_status.config(text="📊 Generating comprehensive evaluation reports...")
        
        # Run enhanced evaluation on full interview (for interviewer analysis only)
        enhanced_session = self.answer_evaluator.evaluate_full_interview(self.session_data)
        
        # Generate comprehensive reports (for interviewer review)
        self.report_generator.generate_reports(enhanced_session, self.candidate_session_folder)
        
        # Update interviewer with final summary
        if self.interviewer_window and 'content_analysis_summary' in enhanced_session:
            summary = enhanced_session['content_analysis_summary']
            final_summary = f"""
===== INTERVIEW COMPLETED =====

FINAL PERFORMANCE ANALYSIS:
• Overall Average: {summary['average_content_score']}/10
• Highest Score: {summary['highest_score']}/10  
• Lowest Score: {summary['lowest_score']}/10
• Questions Answered: {summary['total_questions_evaluated']}/{len(self.questions)}

SCORE BREAKDOWN:
• Excellent (8-10): {summary['score_distribution']['excellent (8-10)']} answers
• Good (6-7.9): {summary['score_distribution']['good (6-7.9)']} answers  
• Fair (4-5.9): {summary['score_distribution']['fair (4-5.9)']} answers
• Poor (0-3.9): {summary['score_distribution']['poor (0-3.9)']} answers

EVALUATION METHOD: {summary['evaluation_method']}

📁 Detailed reports saved to:
{self.candidate_session_folder}
"""
            self.update_interviewer_summary(final_summary)
        
        # Disable all controls
        for widget in [self.speak_btn, self.next_btn, self.finish_btn]:
            widget.config(state='disabled')
        
        # Final status updates
        self.status_label.config(text="✅ Interview completed successfully!", foreground="green")
        
        if self.interviewer_window:
            self.interviewer_status.config(text="✅ Analysis complete - Reports generated")
        
        # Show completion message
        messagebox.showinfo(
            "Interview Complete", 
            f"Interview completed successfully!\n\n"
            f"Candidate: {self.session_data['candidate_name']}\n"
            f"Questions: {len(self.session_data['questions_data'])}/{len(self.questions)}\n\n"
            f"Reports saved to:\n{self.candidate_session_folder}\n\n"
            f"The candidate cannot see the evaluation results.\n"
            f"Check the interviewer dashboard for detailed analysis."
        )
    
    def clear_interviewer_displays(self):
        """Clear all interviewer displays"""
        if not self.interviewer_window:
            return
        
        self.interviewer_score.config(text="--/10")
        self.interviewer_keywords.delete(1.0, tk.END)
        self.interviewer_essential['value'] = 0
        self.interviewer_bonus['value'] = 0
        self.interviewer_essential_label.config(text="0%")
        self.interviewer_bonus_label.config(text="0%")
        self.interviewer_suggestions.delete(1.0, tk.END)
        self.interviewer_summary.delete(1.0, tk.END)
        self.overall_score.config(text="--/10")
    
    def export_interviewer_notes(self):
        """Export interviewer notes and analysis"""
        if not self.interviewer_window:
            return
        
        try:
            notes_file = os.path.join(self.candidate_session_folder, "interviewer_notes.txt")
            
            with open(notes_file, 'w', encoding='utf-8') as f:
                f.write("INTERVIEWER NOTES AND ANALYSIS\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Candidate: {self.session_data['candidate_name']}\n")
                f.write(f"Date: {self.session_data['session_start']}\n\n")
                
                f.write("LIVE NOTES FROM INTERVIEW:\n")
                f.write("-" * 30 + "\n")
                f.write(self.interviewer_summary.get(1.0, tk.END))
                
                f.write("\n\nCURRENT EVALUATION STATE:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Overall Score: {self.overall_score.cget('text')}\n")
                f.write(f"Keywords Analysis:\n{self.interviewer_keywords.get(1.0, tk.END)}\n")
                f.write(f"Suggestions:\n{self.interviewer_suggestions.get(1.0, tk.END)}\n")
            
            messagebox.showinfo("Notes Exported", f"Interviewer notes saved to:\n{notes_file}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export notes: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()
    
    def cleanup(self):
        """Clean up resources including timers"""
        if self.silence_timeout_timer:
            self.silence_timeout_timer.cancel()
        if self.interviewer_window:
            self.interviewer_window.destroy()
        self.audio_handler.cleanup()


def main():
    print("🎯 INTERVIEW SYSTEM - SEPARATE CANDIDATE/INTERVIEWER VIEWS")
    print("=" * 65)
    print("Key Features:")
    print("✅ Clean candidate interface - No analysis visible")
    print("✅ Separate interviewer dashboard - Real-time evaluation")
    print("✅ Advanced keyword-based content analysis")
    print("✅ Live feedback for interviewers only")
    print("✅ Professional candidate experience")
    print("✅ Comprehensive interviewer insights")
    print()
    
    print("🔒 PRIVACY & PROFESSIONALISM:")
    print("=" * 35)
    print("✅ Candidate sees only questions and progress")
    print("✅ No scores or analysis visible to candidate") 
    print("✅ Interviewer gets real-time insights")
    print("✅ Professional interview experience maintained")
    print("✅ Detailed reports for post-interview review")
    print()
    
    print("📊 INTERVIEWER DASHBOARD FEATURES:")
    print("=" * 40)
    print("✅ Real-time content scoring (0-10)")
    print("✅ Keyword detection and coverage analysis")
    print("✅ Improvement suggestions for follow-up")
    print("✅ Live interview progress tracking")
    print("✅ Overall performance calculation")
    print("✅ Export capabilities for notes")
    print()
    
    print("🎮 USAGE INSTRUCTIONS:")
    print("=" * 25)
    print("1. Fill in candidate name and select save folder")
    print("2. Click 'Open Interviewer Dashboard' for analysis view")
    print("3. Click 'Start Interview' to begin")
    print("4. Use 'Speak Question' to read questions aloud")
    print("5. Monitor real-time analysis in interviewer dashboard")
    print("6. Click 'Next Question' after each answer")
    print("7. Review comprehensive reports after completion")
    print()
    
    print("🚀 Starting interview system...")
    
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
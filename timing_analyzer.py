# ================================
# 4. timing_analyzer.py
# Handles response time analysis
# ================================

import time
class TimingAnalyzer:
    def __init__(self):
        self.response_time_excellent = 10.0
        self.response_time_good = 20.0
        self.response_time_poor = 30.0
        
        self.question_spoken_time = None
        self.first_speech_time = None
        
        # === NEW: Add answer duration tracking ===
        self.answer_start_time = None
        self.answer_end_time = None
    
    def mark_question_spoken(self):
        """Mark when question was finished speaking"""
        self.question_spoken_time = time.time()
        self.first_speech_time = None
        # === NEW: Reset answer timing ===
        self.answer_start_time = None
        self.answer_end_time = None
    
    def mark_first_speech(self):
        """Mark when candidate first started speaking"""
        if not self.first_speech_time:
            self.first_speech_time = time.time()
            self.answer_start_time = time.time()
    
    def mark_answer_end(self):
        """Mark when candidate finished answering (recording stopped)"""
        self.answer_end_time = time.time()
    
    def evaluate_confidence(self):
        """Evaluate confidence based on response timing"""
        timing_data = {}
        
        if not self.question_spoken_time or not self.first_speech_time:
            timing_data.update({
                'response_time': None,
                'confidence_level': 'Unable to measure',
                'explanation': 'Could not detect speech timing'
            })
        else:
            response_time = self.first_speech_time - self.question_spoken_time
            
            if response_time <= self.response_time_excellent:
                confidence_level = 'High'
                explanation = 'Started answering within 10 seconds - knows the answer'
            elif response_time <= self.response_time_good:
                confidence_level = 'Moderate'
                explanation = 'Started answering within 10-20 seconds - not very sure'
            elif response_time <= self.response_time_poor:
                confidence_level = 'Low'
                explanation = 'Started answering within 20-30 seconds - took time to think'
            else:
                confidence_level = 'Very Low'
                explanation = 'Took more than 30 seconds to start - does not know the answer'
            
            timing_data.update({
                'response_time': round(response_time, 1),
                'confidence_level': confidence_level,
                'explanation': explanation
            })
        
        if self.answer_start_time and self.answer_end_time:
            answer_duration = self.answer_end_time - self.answer_start_time
            timing_data['answer_duration'] = round(answer_duration, 1)
            
            if answer_duration < 15:
                duration_assessment = 'Very Brief'
            elif answer_duration < 30:
                duration_assessment = 'Brief'
            elif answer_duration < 60:
                duration_assessment = 'Appropriate'
            elif answer_duration < 120:
                duration_assessment = 'Detailed'
            else:
                duration_assessment = 'Very Detailed'
            
            timing_data['duration_assessment'] = duration_assessment
        else:
            timing_data['answer_duration'] = None
            timing_data['duration_assessment'] = 'Unable to measure'
        
        return timing_data
    
    def reset(self):
        """Reset timing for next question"""
        self.question_spoken_time = None
        self.first_speech_time = None
        self.answer_start_time = None
        self.answer_end_time = None


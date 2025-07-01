# ================================
# 5. report_generator.py
# Handles all report generation
# ================================

import json
import os
from datetime import datetime
from collections import defaultdict
import numpy as np

class ReportGenerator:
    def __init__(self):
        pass
    
    def generate_reports(self, session_data, output_folder):
        """Generate both JSON and text reports"""
        self._save_json_report(session_data, output_folder)
        self._generate_text_report(session_data, output_folder)
    
    def _save_json_report(self, session_data, output_folder):
        """Save detailed JSON report"""
        json_path = os.path.join(output_folder, "interview_analysis.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, default=str)

    def _generate_text_report(self, session_data, output_folder):
        """Generate human-readable text report with pause timing"""
        questions_data = session_data['questions_data']
        
        # Calculate overall metrics
        total_words = sum(q['speech_analysis']['word_count'] for q in questions_data)
        total_fillers = sum(q['speech_analysis']['filler_count'] for q in questions_data)
        overall_filler_ratio = (total_fillers / total_words * 100) if total_words > 0 else 0
        
        # Calculate average scores
        fluency_scores = [q['speech_analysis']['fluency_score'] for q in questions_data]
        avg_fluency = sum(fluency_scores) / len(fluency_scores) if fluency_scores else 0
        
        adjusted_scores = [q['speech_analysis'].get('adjusted_fluency_score', 0) for q in questions_data]
        avg_adjusted_fluency = sum(adjusted_scores) / len(adjusted_scores) if adjusted_scores else 0
        
        # === NEW: Calculate pause timing metrics ===
        all_pause_data = []
        total_silence_time = 0
        total_speech_time = 0
        total_significant_pauses = 0
        
        for q in questions_data:
            gap_analysis = q['speech_analysis'].get('gap_analysis')
            if gap_analysis:
                all_pause_data.extend(gap_analysis.get('pauses', []))
                total_silence_time += gap_analysis.get('silence_duration', 0)
                total_speech_time += gap_analysis.get('speech_duration', 0)
                total_significant_pauses += gap_analysis.get('pause_analysis', {}).get('significant_pauses', 0)
        
        # Calculate pause statistics
        if all_pause_data:
            all_pause_durations = [p['duration'] for p in all_pause_data]
            avg_pause_duration = sum(all_pause_durations) / len(all_pause_durations)
            max_pause_duration = max(all_pause_durations)
            total_pause_time = sum(all_pause_durations)
            total_pauses = len(all_pause_data)
        else:
            avg_pause_duration = 0
            max_pause_duration = 0
            total_pause_time = 0
            total_pauses = 0
        
        # Analyze filler categories
        all_categories = defaultdict(int)
        for q in questions_data:
            for category, count in q['speech_analysis'].get('filler_categories', {}).items():
                all_categories[category] += count
        
        # Count confidence levels
        confidence_counts = defaultdict(int)
        for q in questions_data:
            level = q['confidence_evaluation']['confidence_level']
            confidence_counts[level] += 1
        
        # Calculate speech rate
        speech_rates = [q['speech_analysis'].get('speech_rate_wpm') for q in questions_data 
                    if q['speech_analysis'].get('speech_rate_wpm')]
        avg_speech_rate = np.mean(speech_rates) if speech_rates else 0
        
        # Generate report
        report_path = os.path.join(output_folder, "interview_evaluation_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("🎯 COMPREHENSIVE INTERVIEW EVALUATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            
            # Header info
            f.write(f"Candidate: {session_data['candidate_name']}\n")
            f.write(f"Date: {session_data['session_start'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Questions Completed: {len(questions_data)}\n\n")
            
            # Overall analysis
            f.write("📊 OVERALL ANALYSIS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Words: {total_words}\n")
            f.write(f"Total Fillers: {total_fillers} ({overall_filler_ratio:.1f}%)\n")
            f.write(f"Base Fluency Score: {avg_fluency:.1f}/100\n")
            f.write(f"Adjusted Fluency Score: {avg_adjusted_fluency:.1f}/100\n")
            
            if avg_speech_rate > 0:
                f.write(f"Average Speech Rate: {avg_speech_rate:.1f} words/minute\n")
            
            # === NEW: Add comprehensive pause timing ===
            if total_pause_time > 0:
                f.write(f"Total Speech Time: {total_speech_time:.1f} seconds\n")
                f.write(f"Total Silence Time: {total_silence_time:.1f} seconds\n")
                f.write(f"Total Pause Time: {total_pause_time:.1f} seconds\n")
                f.write(f"Speech-to-Silence Ratio: {(total_speech_time/(total_speech_time+total_silence_time)*100):.1f}% speech\n")
            f.write("\n")
            
            # === NEW: Detailed pause analysis section ===
            if total_pauses > 0:
                f.write("⏸️ PAUSE TIMING ANALYSIS\n")
                f.write("-" * 23 + "\n")
                f.write(f"Total Pauses: {total_pauses}\n")
                f.write(f"Significant Pauses (>2s): {total_significant_pauses}\n")
                f.write(f"Average Pause Duration: {avg_pause_duration:.2f} seconds\n")
                f.write(f"Longest Pause: {max_pause_duration:.2f} seconds\n")
                f.write(f"Total Time in Pauses: {total_pause_time:.1f} seconds ({total_pause_time/60:.1f} minutes)\n")
                
                # Pause assessment
                if avg_pause_duration < 1.0:
                    f.write("🟢 PAUSE PATTERN: Quick, natural pauses\n")
                elif avg_pause_duration < 2.0:
                    f.write("🟡 PAUSE PATTERN: Moderate thinking pauses\n")
                elif avg_pause_duration < 3.0:
                    f.write("🟠 PAUSE PATTERN: Longer hesitation pauses\n")
                else:
                    f.write("🔴 PAUSE PATTERN: Extensive thinking required\n")
                
                # Pause frequency assessment
                pause_frequency = total_pauses / len(questions_data)
                if pause_frequency < 2:
                    f.write("🟢 PAUSE FREQUENCY: Smooth delivery\n")
                elif pause_frequency < 4:
                    f.write("🟡 PAUSE FREQUENCY: Occasional hesitation\n")
                elif pause_frequency < 6:
                    f.write("🟠 PAUSE FREQUENCY: Frequent pauses\n")
                else:
                    f.write("🔴 PAUSE FREQUENCY: Very hesitant delivery\n")
                f.write("\n")
            
            # Filler breakdown (existing)
            if all_categories:
                f.write("🔍 FILLER BREAKDOWN BY CATEGORY\n")
                f.write("-" * 32 + "\n")
                for category, count in sorted(all_categories.items()):
                    percentage = (count / total_fillers * 100) if total_fillers > 0 else 0
                    f.write(f"{category.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n")
                f.write("\n")
            
            # Confidence evaluation (existing)
            f.write("🎯 CONFIDENCE EVALUATION\n")
            f.write("-" * 25 + "\n")
            f.write("Based on response timing analysis:\n\n")
            for level, count in confidence_counts.items():
                f.write(f"{level}: {count} questions\n")
            f.write("\n")
            
            # Fluency assessment (existing)
            f.write("📈 FLUENCY ASSESSMENT\n")
            f.write("-" * 20 + "\n")
            if avg_adjusted_fluency >= 80:
                f.write("🟢 EXCELLENT: Very fluent speech with minimal issues\n")
            elif avg_adjusted_fluency >= 60:
                f.write("🟡 GOOD: Generally fluent with some hesitation\n")
            elif avg_adjusted_fluency >= 40:
                f.write("🟠 FAIR: Noticeable issues affecting fluency\n")
            else:
                f.write("🔴 NEEDS IMPROVEMENT: Significant communication challenges\n")
            f.write("\n")
            
            # Speech rate assessment (existing)
            if avg_speech_rate > 0:
                f.write("⏱️ SPEECH PACE ANALYSIS\n")
                f.write("-" * 22 + "\n")
                if 120 <= avg_speech_rate <= 180:
                    f.write("🟢 OPTIMAL: Speech rate within ideal range\n")
                elif avg_speech_rate < 120:
                    f.write("🟡 SLOW: Speech rate below optimal (may indicate hesitation)\n")
                elif avg_speech_rate > 180:
                    f.write("🟠 FAST: Speech rate above optimal (may indicate nervousness)\n")
                f.write("\n")
            
            # === ENHANCED: Detailed question analysis with pause details ===
            f.write("📝 DETAILED QUESTION ANALYSIS\n")
            f.write("-" * 30 + "\n")
            for q in questions_data:
                f.write(f"\nQuestion {q['question_number']}: {q['question_text']}\n")
                
                # Confidence
                conf = q['confidence_evaluation']
                f.write(f"Confidence: {conf['confidence_level']}")
                if conf.get('response_time'):
                    f.write(f" ({conf['response_time']}s)")
                f.write("\n")
                
                # Speech metrics
                speech = q['speech_analysis']
                f.write(f"Words: {speech['word_count']} | Fillers: {speech['filler_count']} ({speech['filler_ratio']}%)\n")
                f.write(f"Fluency: {speech.get('fluency_score', 'N/A')}/100")
                if speech.get('adjusted_fluency_score') != speech.get('fluency_score'):
                    f.write(f" → {speech.get('adjusted_fluency_score', 'N/A')}/100 (adjusted)")
                f.write("\n")
                
                # === NEW: Enhanced timing with pause details ===
                if speech.get('speech_rate_wpm'):
                    f.write(f"Speech Rate: {speech['speech_rate_wpm']} wpm")
                    
                    # Enhanced pause information
                    if speech.get('pause_summary'):
                        ps = speech['pause_summary']
                        f.write(f" | Pauses: {ps['total_pauses']}")
                        if ps.get('significant_pauses', 0) > 0:
                            f.write(f" ({ps['significant_pauses']} significant)")
                        f.write(f" | Speech: {ps['speech_ratio']}%")
                        
                        # Show pause timing details
                        if ps.get('avg_pause_duration', 0) > 0:
                            f.write(f"\nPause Details: Avg {ps['avg_pause_duration']:.2f}s, Max {ps['max_pause_duration']:.2f}s")
                    
                    f.write("\n")
                
                # === NEW: Individual pause breakdown for detailed questions ===
                gap_analysis = speech.get('gap_analysis')
                if gap_analysis and gap_analysis.get('pauses'):
                    pauses = gap_analysis['pauses']
                    if len(pauses) > 0:
                        # Show individual pause times for questions with many pauses
                        if len(pauses) > 3:
                            significant_pauses = [p for p in pauses if p['type'] == 'significant']
                            if significant_pauses:
                                pause_times = [f"{p['duration']:.1f}s" for p in significant_pauses[:3]]
                                f.write(f"Notable Pauses: {', '.join(pause_times)}")
                                if len(significant_pauses) > 3:
                                    f.write(f" (+{len(significant_pauses)-3} more)")
                                f.write("\n")
                
                # Top fillers (existing)
                if speech.get('filler_details'):
                    top_fillers = sorted(speech['filler_details'].items(), key=lambda x: x[1], reverse=True)[:3]
                    if top_fillers:
                        filler_summary = ', '.join([f"{word}({count})" for word, count in top_fillers])
                        f.write(f"Top Fillers: {filler_summary}\n")
                
                # Transcript preview (existing)
                transcript = q['transcript']
                f.write(f"Transcript: {transcript}\n")
                f.write("-" * 40 + "\n")
        
        print(f"Reports saved to: {output_folder}")
        return report_path


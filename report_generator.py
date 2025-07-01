# ================================
# 3. UPDATED report_generator.py
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
        """Generate comprehensive human-readable text report with answer evaluation"""
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
        
        # NEW: Calculate content evaluation metrics
        content_scores = []
        keyword_coverages = []
        llm_scores = []
        
        for q in questions_data:
            if 'answer_evaluation' in q:
                content_scores.append(q['answer_evaluation']['combined_score'])
                keyword_coverages.append(q['answer_evaluation']['keyword_evaluation']['coverage_percentage'])
                llm_scores.append(q['answer_evaluation']['score_breakdown']['llm_average'])
        
        avg_content_score = np.mean(content_scores) if content_scores else 0
        avg_keyword_coverage = np.mean(keyword_coverages) if keyword_coverages else 0
        avg_llm_score = np.mean(llm_scores) if llm_scores else 0
        
        # Calculate pause timing metrics
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
            f.write(f"Questions Completed: {len(questions_data)}\n")
            
            # Show analysis capabilities
            analysis_features = []
            if any(q['speech_analysis'].get('gap_analysis') for q in questions_data):
                analysis_features.append("Gap Analysis")
            if any(q['speech_analysis'].get('filler_categories') for q in questions_data):
                analysis_features.append("Advanced Filler Detection")
            if content_scores:
                analysis_features.append("Content Evaluation")  # NEW
            
            if analysis_features:
                f.write(f"Analysis Features: {', '.join(analysis_features)}\n")
            f.write("\n")
            
            # Overall analysis
            f.write("📊 OVERALL ANALYSIS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Words: {total_words}\n")
            f.write(f"Total Fillers: {total_fillers} ({overall_filler_ratio:.1f}%)\n")
            f.write(f"Base Fluency Score: {avg_fluency:.1f}/100\n")
            f.write(f"Adjusted Fluency Score: {avg_adjusted_fluency:.1f}/100\n")
            
            # NEW: Content evaluation summary
            if content_scores:
                f.write(f"Average Content Score: {avg_content_score:.1f}/10\n")
                f.write(f"Average Keyword Coverage: {avg_keyword_coverage:.1f}%\n")
                f.write(f"Average LLM Assessment: {avg_llm_score:.1f}/10\n")
            
            if avg_speech_rate > 0:
                f.write(f"Average Speech Rate: {avg_speech_rate:.1f} words/minute\n")
            
            # Speech vs silence breakdown
            if total_speech_time > 0:
                total_audio_time = total_speech_time + total_silence_time
                speech_percentage = (total_speech_time / total_audio_time * 100) if total_audio_time > 0 else 0
                f.write(f"Total Speech Time: {total_speech_time:.1f} seconds\n")
                f.write(f"Total Silence Time: {total_silence_time:.1f} seconds\n")
                if total_pause_time > 0:
                    f.write(f"Total Pause Time: {total_pause_time:.1f} seconds\n")
                f.write(f"Speech-to-Silence Ratio: {speech_percentage:.1f}% speech\n")
            f.write("\n")
            
            # NEW: Content quality analysis section
            if content_scores:
                f.write("🧠 CONTENT QUALITY ANALYSIS\n")
                f.write("-" * 27 + "\n")
                
                if avg_content_score >= 8.0:
                    f.write("🟢 EXCELLENT: Strong, relevant answers with good coverage\n")
                elif avg_content_score >= 6.5:
                    f.write("🟡 GOOD: Generally solid answers with room for improvement\n")
                elif avg_content_score >= 5.0:
                    f.write("🟠 FAIR: Adequate answers but lacking depth or relevance\n")
                else:
                    f.write("🔴 NEEDS IMPROVEMENT: Weak answers with poor content quality\n")
                
                # Keyword coverage assessment
                if avg_keyword_coverage >= 70:
                    f.write("✅ KEYWORD COVERAGE: Good coverage of expected topics\n")
                elif avg_keyword_coverage >= 50:
                    f.write("⚠️ KEYWORD COVERAGE: Moderate coverage, some key points missing\n")
                else:
                    f.write("❌ KEYWORD COVERAGE: Poor coverage of expected topics\n")
                
                # Content distribution
                excellent_answers = sum(1 for score in content_scores if score >= 8.0)
                poor_answers = sum(1 for score in content_scores if score < 5.0)
                f.write(f"📈 ANSWER DISTRIBUTION: {excellent_answers} excellent, {poor_answers} need improvement\n")
                f.write("\n")
            
            # Detailed pause analysis section
            if total_pauses > 0:
                f.write("⏸️ PAUSE TIMING ANALYSIS\n")
                f.write("-" * 25 + "\n")
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
            
            # Filler breakdown
            if all_categories:
                f.write("🔍 FILLER BREAKDOWN BY CATEGORY\n")
                f.write("-" * 32 + "\n")
                for category, count in sorted(all_categories.items()):
                    percentage = (count / total_fillers * 100) if total_fillers > 0 else 0
                    f.write(f"{category.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n")
                f.write("\n")
            
            # Confidence evaluation
            f.write("🎯 CONFIDENCE EVALUATION\n")
            f.write("-" * 25 + "\n")
            f.write("Based on response timing analysis:\n\n")
            for level, count in confidence_counts.items():
                f.write(f"{level}: {count} questions\n")
            f.write("\n")
            
            # Fluency assessment
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
            
            # Speech rate assessment
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
            
            # ENHANCED: Detailed question analysis with content evaluation
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
                
                # NEW: Content evaluation details
                if 'answer_evaluation' in q:
                    eval_data = q['answer_evaluation']
                    f.write(f"Content Score: {eval_data['combined_score']}/10 ")
                    
                    # Quality assessment
                    score = eval_data['combined_score']
                    if score >= 8.0:
                        f.write("(Excellent)\n")
                    elif score >= 6.5:
                        f.write("(Good)\n")
                    elif score >= 5.0:
                        f.write("(Fair)\n")
                    else:
                        f.write("(Needs Improvement)\n")
                    
                    # Keyword details
                    kw_eval = eval_data['keyword_evaluation']
                    if kw_eval['found_required']:
                        f.write(f"Keywords Found: {', '.join(kw_eval['found_required'])}\n")
                    if kw_eval['missing_required']:
                        f.write(f"Missing Keywords: {', '.join(kw_eval['missing_required'])}\n")
                    f.write(f"Keyword Coverage: {kw_eval['coverage_percentage']:.1f}%\n")
                    
                    # LLM assessment highlights
                    llm_eval = eval_data['llm_evaluation']
                    if llm_eval.get('strengths') and llm_eval['strengths'][0] != "Answer provided":
                        f.write(f"Strengths: {', '.join(llm_eval['strengths'][:2])}\n")
                    if llm_eval.get('weaknesses') and llm_eval['weaknesses'][0] != "LLM evaluation not available":
                        f.write(f"Areas for Improvement: {', '.join(llm_eval['weaknesses'][:2])}\n")
                
                # Enhanced timing with pause details
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
                
                # Individual pause breakdown for detailed questions
                gap_analysis = speech.get('gap_analysis')
                if gap_analysis and gap_analysis.get('pauses'):
                    pauses = gap_analysis['pauses']
                    if len(pauses) > 3:
                        significant_pauses = [p for p in pauses if p['type'] == 'significant']
                        if significant_pauses:
                            pause_times = [f"{p['duration']:.1f}s" for p in significant_pauses[:3]]
                            f.write(f"Notable Pauses: {', '.join(pause_times)}")
                            if len(significant_pauses) > 3:
                                f.write(f" (+{len(significant_pauses)-3} more)")
                            f.write("\n")
                
                # Top fillers
                if speech.get('filler_details'):
                    top_fillers = sorted(speech['filler_details'].items(), key=lambda x: x[1], reverse=True)[:3]
                    if top_fillers:
                        filler_summary = ', '.join([f"{word}({count})" for word, count in top_fillers])
                        f.write(f"Top Fillers: {filler_summary}\n")
                
                transcript = q['transcript']
                f.write(f"Transcript: {transcript}\n")
                f.write("-" * 40 + "\n")
        
        print(f"Enhanced reports saved to: {output_folder}")
        return report_path
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
    
    # FIXED: Handle new data structure for content evaluation
    content_scores = []
    keyword_coverages = []
    
    for q in questions_data:
        if 'answer_evaluation' in q:
            content_scores.append(q['answer_evaluation']['combined_score'])
            # FIXED: Use the correct field name from enhanced evaluator
            coverage_analysis = q['answer_evaluation']['keyword_evaluation'].get('coverage_analysis', {})
            essential_coverage = coverage_analysis.get('essential_coverage', 0)
            keyword_coverages.append(essential_coverage)
    
    avg_content_score = sum(content_scores) / len(content_scores) if content_scores else 0
    avg_keyword_coverage = sum(keyword_coverages) / len(keyword_coverages) if keyword_coverages else 0
    
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
    from collections import defaultdict
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
    avg_speech_rate = sum(speech_rates) / len(speech_rates) if speech_rates else 0
    
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
            analysis_features.append("Enhanced Keyword Evaluation")  # UPDATED
        
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
        
        # UPDATED: Content evaluation summary
        if content_scores:
            f.write(f"Average Content Score: {avg_content_score:.1f}/10\n")
            f.write(f"Average Keyword Coverage: {avg_keyword_coverage:.1f}%\n")
            f.write(f"Evaluation Method: Advanced Keyword Matching\n")
        
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
        
        # UPDATED: Content quality analysis section
        if content_scores:
            f.write("🧠 CONTENT QUALITY ANALYSIS\n")
            f.write("-" * 27 + "\n")
            
            if avg_content_score >= 8.0:
                f.write("🟢 EXCELLENT: Strong, relevant answers with good technical depth\n")
            elif avg_content_score >= 6.5:
                f.write("🟡 GOOD: Generally solid technical answers with room for improvement\n")
            elif avg_content_score >= 5.0:
                f.write("🟠 FAIR: Adequate technical knowledge but lacking depth\n")
            else:
                f.write("🔴 NEEDS IMPROVEMENT: Weak technical answers with poor content quality\n")
            
            # Keyword coverage assessment
            if avg_keyword_coverage >= 70:
                f.write("✅ KEYWORD COVERAGE: Good coverage of technical concepts\n")
            elif avg_keyword_coverage >= 50:
                f.write("⚠️ KEYWORD COVERAGE: Moderate coverage, some technical gaps\n")
            else:
                f.write("❌ KEYWORD COVERAGE: Poor coverage of expected technical topics\n")
            
            # Content distribution
            excellent_answers = sum(1 for score in content_scores if score >= 8.0)
            poor_answers = sum(1 for score in content_scores if score < 5.0)
            f.write(f"📈 ANSWER DISTRIBUTION: {excellent_answers} excellent, {poor_answers} need improvement\n")
            f.write("\n")
        
        # Rest of the report generation continues as before...
        # [Include all the existing pause analysis, filler breakdown, etc.]
        
        # ENHANCED: Detailed question analysis with new data structure
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
            
            # UPDATED: Content evaluation details with new structure
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
                
                # FIXED: Use new data structure
                kw_eval = eval_data['keyword_evaluation']
                coverage_analysis = kw_eval.get('coverage_analysis', {})
                
                # Show found keywords
                matches_found = kw_eval.get('matches_found', {})
                exact_matches = matches_found.get('exact', {})
                essential_keywords = []
                
                for group_name, keywords in exact_matches.get('essential', {}).items():
                    essential_keywords.extend(keywords)
                
                if essential_keywords:
                    f.write(f"Keywords Found: {', '.join(essential_keywords[:5])}\n")
                
                # Coverage percentage
                essential_coverage = coverage_analysis.get('essential_coverage', 0)
                f.write(f"Keyword Coverage: {essential_coverage:.1f}%\n")
                
                # Improvement suggestions
                suggestions = kw_eval.get('improvement_suggestions', [])
                if suggestions and suggestions[0] != "No specific improvements needed.":
                    f.write(f"Suggestions: {suggestions[0]}\n")
            
            # Rest of question analysis...
            transcript = q['transcript']
            f.write(f"Transcript: {transcript}\n")
            f.write("-" * 40 + "\n")
    
    print(f"Enhanced reports saved to: {output_folder}")
    return report_path
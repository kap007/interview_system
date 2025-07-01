# ================================
# test_existing_data.py - Test with Old Interview Data
# ================================

import json
import os
from answer_evaluator import AnswerEvaluator
from report_generator import ReportGenerator

def test_with_existing_json():
    """
    Method 1: Test with existing JSON interview data
    Use this if you have interview_analysis.json files from previous interviews
    """
    print("🧪 TESTING WITH EXISTING JSON DATA")
    print("=" * 50)
    
    # Path to your existing interview JSON file
    json_file_path = input("Enter path to your interview_analysis.json file: ").strip()
    
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        return
    
    try:
        # Load existing interview data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        print(f"✅ Loaded interview data for: {session_data.get('candidate_name', 'Unknown')}")
        print(f"📊 Questions: {len(session_data.get('questions_data', []))}")
        
        # Initialize evaluator
        evaluator = AnswerEvaluator()
        
        # Add content evaluation to existing data
        enhanced_session = evaluator.evaluate_full_interview(session_data)
        
        # Generate new enhanced reports
        output_folder = os.path.dirname(json_file_path)
        report_generator = ReportGenerator()
        report_generator.generate_reports(enhanced_session, output_folder)
        
        print(f"✅ Enhanced reports generated in: {output_folder}")
        print("📁 Files created:")
        print("   - interview_analysis.json (updated with content evaluation)")
        print("   - interview_evaluation_report.txt (enhanced report)")
        
        # Show summary
        if 'content_analysis_summary' in enhanced_session:
            summary = enhanced_session['content_analysis_summary']
            print(f"\n📊 CONTENT ANALYSIS SUMMARY:")
            print(f"   Average Content Score: {summary['average_content_score']}/10")
            print(f"   Highest Score: {summary['highest_score']}/10")
            print(f"   Lowest Score: {summary['lowest_score']}/10")
            print(f"   Questions Above 7: {summary['questions_above_7']}")
            print(f"   Questions Below 5: {summary['questions_below_5']}")
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")

def test_with_transcripts():
    """
    Method 2: Test with just transcript text
    Use this if you have transcripts but no full JSON data
    """
    print("🧪 TESTING WITH TRANSCRIPT DATA")
    print("=" * 50)
    
    # Sample transcripts for testing
    test_transcripts = [
        {
            "question": "Tell me about yourself and your background.",
            "transcript": "My name is John and I have a background in computer science with 5 years of experience in software development. I've worked on various projects using Python and JavaScript. I have strong skills in problem-solving and I'm passionate about creating efficient solutions."
        },
        {
            "question": "What are your greatest strengths?",
            "transcript": "My greatest strength is my ability to solve complex problems. For example, in my last project, I identified a performance bottleneck that was causing system slowdowns. I analyzed the issue, implemented a caching solution, and improved system performance by 40%. I'm also very detail-oriented and work well in teams."
        },
        {
            "question": "Why are you interested in this position?",
            "transcript": "I'm very interested in this position because I've researched your company and I'm impressed by your mission to create innovative software solutions. This role aligns perfectly with my career goals in software development. I see great opportunity for growth here and I believe I can contribute valuable skills to your team."
        }
    ]
    
    # Allow user to add their own transcripts
    print("📝 You can test with sample data or enter your own transcripts")
    choice = input("Use sample data? (y/n): ").lower().strip()
    
    if choice != 'y':
        # User wants to enter their own data
        test_transcripts = []
        questions = [
            "Tell me about yourself and your background.",
            "Why are you interested in this position?",
            "What are your greatest strengths?",
            "Describe a challenging situation you faced and how you handled it.",
            "What is your biggest weakness?"
        ]
        
        print("\n📝 Enter transcripts for evaluation (press Enter to skip a question):")
        for i, question in enumerate(questions):
            print(f"\nQuestion {i+1}: {question}")
            transcript = input("Transcript: ").strip()
            if transcript:
                test_transcripts.append({
                    "question": question,
                    "transcript": transcript
                })
    
    # Evaluate transcripts
    evaluator = AnswerEvaluator()
    results = []
    
    print(f"\n🔍 Evaluating {len(test_transcripts)} answers...")
    
    for i, data in enumerate(test_transcripts):
        question = data["question"]
        transcript = data["transcript"]
        
        # Find question index (map to your 10 standard questions)
        question_index = map_question_to_index(question)
        
        result = evaluator.evaluate_single_answer(question_index, question, transcript)
        results.append({
            "question": question,
            "transcript": transcript,
            "evaluation": result
        })
        
        print(f"✅ Q{i+1}: {result['combined_score']}/10 - {question[:50]}...")
    
    # Display detailed results
    print(f"\n📊 DETAILED EVALUATION RESULTS")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        eval_data = result["evaluation"]
        kw_eval = eval_data["keyword_evaluation"]
        llm_eval = eval_data["llm_evaluation"]
        
        print(f"\n📝 Question {i}: {result['question']}")
        print(f"🎯 Combined Score: {eval_data['combined_score']}/10")
        print(f"📊 Breakdown: Keywords {kw_eval['keyword_score']}/10 | LLM {eval_data['score_breakdown']['llm_average']}/10")
        print(f"🔍 Keywords Found: {', '.join(kw_eval['found_required']) if kw_eval['found_required'] else 'None'}")
        print(f"❌ Missing Keywords: {', '.join(kw_eval['missing_required']) if kw_eval['missing_required'] else 'None'}")
        print(f"📈 Coverage: {kw_eval['coverage_percentage']}%")
        
        if llm_eval.get('strengths') and llm_eval['strengths'][0] != "Answer provided":
            print(f"✅ Strengths: {', '.join(llm_eval['strengths'][:2])}")
        if llm_eval.get('weaknesses') and llm_eval['weaknesses'][0] != "LLM evaluation not available":
            print(f"⚠️  Areas for Improvement: {', '.join(llm_eval['weaknesses'][:2])}")
        
        print(f"💭 Assessment: {llm_eval.get('overall_assessment', 'N/A')}")
        print("-" * 60)
    
    # Calculate overall performance
    all_scores = [r["evaluation"]["combined_score"] for r in results]
    avg_score = sum(all_scores) / len(all_scores)
    
    print(f"\n🎯 OVERALL PERFORMANCE:")
    print(f"   Average Score: {avg_score:.1f}/10")
    print(f"   Score Range: {min(all_scores):.1f} - {max(all_scores):.1f}")
    print(f"   Strong Answers (≥7): {sum(1 for s in all_scores if s >= 7)}")
    print(f"   Weak Answers (<5): {sum(1 for s in all_scores if s < 5)}")

def map_question_to_index(question):
    """
    Map question text to the appropriate index (0-9) for evaluation
    """
    question_lower = question.lower()
    
    question_mappings = {
        0: ["tell me about yourself", "about yourself", "background"],
        1: ["why are you interested", "interested in this position", "why this position"],
        2: ["greatest strengths", "strengths", "what are your strengths"],
        3: ["challenging situation", "challenging", "difficult situation", "handled"],
        4: ["biggest weakness", "weakness", "weaknesses"],
        5: ["five years", "see yourself", "future", "where do you see"],
        6: ["why should we hire", "hire you", "why hire"],
        7: ["worked in a team", "team", "teamwork", "collaboration"],
        8: ["handle stress", "stress", "pressure", "handle pressure"],
        9: ["questions for us", "any questions", "questions"]
    }
    
    for index, keywords in question_mappings.items():
        if any(keyword in question_lower for keyword in keywords):
            return index
    
    # Default to first question if no match
    return 0

def test_single_answer():
    """
    Method 3: Test evaluation of a single answer
    Quick test for specific question-answer pairs
    """
    print("🧪 TESTING SINGLE ANSWER EVALUATION")
    print("=" * 50)
    
    questions = [
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
    
    print("Available questions:")
    for i, q in enumerate(questions):
        print(f"{i+1}. {q}")
    
    try:
        question_num = int(input("\nSelect question number (1-10): ")) - 1
        if question_num < 0 or question_num >= len(questions):
            print("❌ Invalid question number")
            return
        
        question = questions[question_num]
        print(f"\nSelected: {question}")
        
        transcript = input("\nEnter candidate's answer: ").strip()
        if not transcript:
            print("❌ No transcript provided")
            return
        
        # Evaluate
        evaluator = AnswerEvaluator()
        result = evaluator.evaluate_single_answer(question_num, question, transcript)
        
        # Display results
        print(f"\n🎯 EVALUATION RESULTS")
        print("=" * 30)
        print(f"Combined Score: {result['combined_score']}/10")
        print(f"Keyword Score: {result['score_breakdown']['keyword_score']}/10")
        print(f"LLM Score: {result['score_breakdown']['llm_average']}/10")
        print(f"Coverage: {result['keyword_evaluation']['coverage_percentage']}%")
        
        kw_eval = result['keyword_evaluation']
        if kw_eval['found_required']:
            print(f"✅ Found Keywords: {', '.join(kw_eval['found_required'])}")
        if kw_eval['missing_required']:
            print(f"❌ Missing Keywords: {', '.join(kw_eval['missing_required'])}")
        
        llm_eval = result['llm_evaluation']
        print(f"💭 LLM Assessment: {llm_eval.get('overall_assessment', 'N/A')}")
        
    except ValueError:
        print("❌ Please enter a valid number")

def main():
    """
    Main testing interface
    """
    print("🧪 INTERVIEW SYSTEM TESTING")
    print("=" * 40)
    print("Choose testing method:")
    print("1. Test with existing interview JSON file")
    print("2. Test with transcript data")
    print("3. Test single answer evaluation")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == "1":
                test_with_existing_json()
                break
            elif choice == "2":
                test_with_transcripts()
                break
            elif choice == "3":
                test_single_answer()
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Please enter 1, 2, 3, or 4")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()

# ================================
# USAGE INSTRUCTIONS
# ================================

"""
TESTING OPTIONS:

🎯 METHOD 1: Existing JSON Files
- If you have previous interview_analysis.json files
- Will add content evaluation to existing data
- Generates enhanced reports with new features

🎯 METHOD 2: Transcript Testing  
- Test with transcript text only
- Good for validating evaluation logic
- Can use sample data or enter your own

🎯 METHOD 3: Single Answer Testing
- Quick test of individual question-answer pairs
- Good for fine-tuning keyword criteria
- Immediate feedback on evaluation

EXAMPLE USAGE:
python test_existing_data.py

This will give you a menu to choose your testing method!
"""
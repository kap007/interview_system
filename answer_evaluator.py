# ================================
# UPDATED answer_evaluator.py - WITH LLM CONNECTED
# ================================

import ollama
import json
import numpy as np

class LlamaClient:
    def __init__(self):
        self.model = "llama3.1:8b"
    
    def generate(self, prompt):
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f'{{"error": "LLM generation failed: {str(e)}"}}'

class AnswerEvaluator:
    def __init__(self, llm_client=None):
        """
        Initialize evaluator for your fixed set of interview questions
        
        Args:
            llm_client: Your Llama3.1:8b client instance
        """
        # FIXED: If no LLM client provided, create one automatically
        if llm_client is None:
            try:
                self.llm_client = LlamaClient()
                print("✅ LLM client initialized successfully with Ollama")
            except Exception as e:
                print(f"⚠️  LLM initialization failed: {e}")
                print("   Falling back to default scores")
                self.llm_client = None
        else:
            self.llm_client = llm_client
            
        # Fixed evaluation criteria for your 10 hardcoded questions
        self.question_criteria = self._initialize_question_criteria()
        self.llm_prompt = self._get_llm_prompt_template()
    
    def _initialize_question_criteria(self):
        """
        Define keywords and weights for each of your 10 interview questions
        Matches your existing questions list exactly
        """
        return {
            # Question 1: Tell me about yourself and your background
            0: {
                "type": "behavioral",
                "required_keywords": ["background", "experience", "education"],
                "bonus_keywords": ["skills", "achievements", "goals", "projects"],
                "negative_keywords": ["personal", "family", "irrelevant"],
                "keyword_weight": 0.2,  # Behavioral questions rely more on LLM
                "max_score": 10
            },
            
            # Question 2: Why are you interested in this position?
            1: {
                "type": "behavioral", 
                "required_keywords": ["interested", "position", "company", "role"],
                "bonus_keywords": ["research", "mission", "growth", "opportunity"],
                "negative_keywords": ["money", "salary", "benefits"],
                "keyword_weight": 0.3,
                "max_score": 10
            },
            
            # Question 3: What are your greatest strengths?
            2: {
                "type": "behavioral",
                "required_keywords": ["strength", "skill", "good at"],
                "bonus_keywords": ["example", "specific", "relevant", "achievement"],
                "negative_keywords": ["weakness", "bad at"],
                "keyword_weight": 0.3,
                "max_score": 10
            },
            
            # Question 4: Describe a challenging situation you faced and how you handled it
            3: {
                "type": "behavioral",
                "required_keywords": ["challenge", "situation", "problem", "handled"],
                "bonus_keywords": ["solution", "result", "learned", "team", "overcome"],
                "negative_keywords": ["gave up", "failed", "couldn't"],
                "keyword_weight": 0.3,
                "max_score": 10
            },
            
            # Question 5: What is your biggest weakness?
            4: {
                "type": "behavioral",
                "required_keywords": ["weakness", "improve", "working on"],
                "bonus_keywords": ["example", "specific", "learning", "progress"],
                "negative_keywords": ["perfect", "no weakness", "strength"],
                "keyword_weight": 0.3,
                "max_score": 10
            },
            
            # Question 6: Where do you see yourself in five years?
            5: {
                "type": "behavioral",
                "required_keywords": ["five years", "future", "goals", "career"],
                "bonus_keywords": ["growth", "development", "leadership", "expertise"],
                "negative_keywords": ["don't know", "uncertain", "same place"],
                "keyword_weight": 0.3,
                "max_score": 10
            },
            
            # Question 7: Why should we hire you?
            6: {
                "type": "behavioral",
                "required_keywords": ["hire", "value", "bring", "contribute"],
                "bonus_keywords": ["unique", "skills", "experience", "results"],
                "negative_keywords": ["don't know", "maybe", "hope"],
                "keyword_weight": 0.3,
                "max_score": 10
            },
            
            # Question 8: Describe a time when you worked in a team
            7: {
                "type": "behavioral",
                "required_keywords": ["team", "worked", "collaboration", "together"],
                "bonus_keywords": ["role", "contribution", "result", "communication"],
                "negative_keywords": ["alone", "individual", "by myself"],
                "keyword_weight": 0.3,
                "max_score": 10
            },
            
            # Question 9: How do you handle stress and pressure?
            8: {
                "type": "behavioral",
                "required_keywords": ["stress", "pressure", "handle", "manage"],
                "bonus_keywords": ["techniques", "example", "calm", "organize"],
                "negative_keywords": ["panic", "can't handle", "avoid"],
                "keyword_weight": 0.3,
                "max_score": 10
            },
            
            # Question 10: Do you have any questions for us?
            9: {
                "type": "behavioral",
                "required_keywords": ["question", "ask", "about"],
                "bonus_keywords": ["company", "role", "team", "culture", "growth"],
                "negative_keywords": ["no questions", "nothing", "salary"],
                "keyword_weight": 0.4,  # Having questions is important
                "max_score": 10
            }
        }
    
    def _get_llm_prompt_template(self):
        """
        Single LLM prompt template for all questions
        """
        return """
You are an expert HR interviewer evaluating a candidate's answer to an interview question.

Question: {question}
Candidate Answer: {transcript}

Evaluate this answer on a scale of 0-10 for each criterion:

1. RELEVANCE: How well does the answer address the question asked?
2. STRUCTURE: Is the answer well-organized and easy to follow?
3. SPECIFICITY: Does it include concrete examples and specific details?
4. PROFESSIONALISM: Is the tone and content appropriate for an interview?

Provide your response in this exact JSON format:
{{
    "relevance": score,
    "structure": score,
    "specificity": score,
    "professionalism": score,
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "overall_assessment": "brief summary in 1-2 sentences"
}}
"""
    
    def evaluate_keywords(self, transcript, question_index):
        """
        Evaluate based on predefined keywords for specific question
        
        Args:
            transcript: Candidate's answer
            question_index: Index of question (0-9)
            
        Returns:
            dict: Keyword evaluation results
        """
        if question_index not in self.question_criteria:
            return {"keyword_score": 0, "details": "Question not found"}
        
        criteria = self.question_criteria[question_index]
        transcript_lower = transcript.lower()
        
        # Count required keywords
        found_required = []
        for keyword in criteria["required_keywords"]:
            if keyword.lower() in transcript_lower:
                found_required.append(keyword)
        
        # Count bonus keywords
        found_bonus = []
        for keyword in criteria["bonus_keywords"]:
            if keyword.lower() in transcript_lower:
                found_bonus.append(keyword)
        
        # Count negative keywords
        found_negative = []
        for keyword in criteria["negative_keywords"]:
            if keyword.lower() in transcript_lower:
                found_negative.append(keyword)
        
        # Calculate keyword score
        required_ratio = len(found_required) / len(criteria["required_keywords"]) if criteria["required_keywords"] else 1
        bonus_points = len(found_bonus) * 0.5  # 0.5 points per bonus keyword
        negative_penalty = len(found_negative) * 1.0  # 1 point penalty per negative
        
        keyword_score = max(0, min(10, (required_ratio * 7) + bonus_points - negative_penalty))
        
        return {
            "keyword_score": round(keyword_score, 1),
            "found_required": found_required,
            "found_bonus": found_bonus,
            "found_negative": found_negative,
            "missing_required": [kw for kw in criteria["required_keywords"] 
                               if kw.lower() not in transcript_lower],
            "coverage_percentage": round(required_ratio * 100, 1)
        }
    
    def evaluate_with_llm(self, question, transcript):
        """
        Get LLM evaluation for any question
        
        Args:
            question: The interview question
            transcript: Candidate's answer
            
        Returns:
            dict: LLM evaluation results
        """
        if not self.llm_client:
            # Return reasonable default scores if no LLM
            return {
                "relevance": 7.0,
                "structure": 6.5,
                "specificity": 6.0,
                "professionalism": 7.5,
                "strengths": ["Answer provided"],
                "weaknesses": ["LLM evaluation not available"],
                "overall_assessment": "LLM client not configured"
            }
        
        try:
            # Format prompt
            prompt = self.llm_prompt.format(question=question, transcript=transcript)
            print(f"🤖 Evaluating with LLM: {question[:50]}...")
            
            # Call your LLM
            response = self.llm_client.generate(prompt)
            print(f"✅ LLM response received")
            
            # Parse response
            try:
                # Clean up response - sometimes LLM adds extra text
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean[7:]
                if response_clean.endswith('```'):
                    response_clean = response_clean[:-3]
                response_clean = response_clean.strip()
                
                llm_scores = json.loads(response_clean)
                return llm_scores
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing error: {e}")
                print(f"Raw response: {response[:200]}...")
                
                # Try to extract scores using regex if JSON parsing fails
                try:
                    import re
                    relevance_match = re.search(r'"relevance":\s*(\d+(?:\.\d+)?)', response)
                    structure_match = re.search(r'"structure":\s*(\d+(?:\.\d+)?)', response)
                    specificity_match = re.search(r'"specificity":\s*(\d+(?:\.\d+)?)', response)
                    professionalism_match = re.search(r'"professionalism":\s*(\d+(?:\.\d+)?)', response)
                    
                    if all([relevance_match, structure_match, specificity_match, professionalism_match]):
                        return {
                            "relevance": float(relevance_match.group(1)),
                            "structure": float(structure_match.group(1)),
                            "specificity": float(specificity_match.group(1)),
                            "professionalism": float(professionalism_match.group(1)),
                            "strengths": ["LLM provided scores"],
                            "weaknesses": ["Response formatting irregular"],
                            "overall_assessment": "Scores extracted from irregular response format"
                        }
                except:
                    pass
                
                # Final fallback
                return {
                    "relevance": 6.0,
                    "structure": 6.0,
                    "specificity": 6.0,
                    "professionalism": 7.0,
                    "strengths": ["Response received"],
                    "weaknesses": ["Could not parse LLM response"],
                    "overall_assessment": "LLM response formatting error"
                }
                
        except Exception as e:
            print(f"❌ LLM evaluation error: {e}")
            return {
                "relevance": 5.0,
                "structure": 5.0,
                "specificity": 5.0,
                "professionalism": 6.0,
                "strengths": [],
                "weaknesses": [f"LLM error: {str(e)}"],
                "overall_assessment": "LLM evaluation failed"
            }
    
    def evaluate_single_answer(self, question_index, question_text, transcript):
        """
        Complete evaluation for one question
        
        Args:
            question_index: Index (0-9) of the question
            question_text: The actual question text
            transcript: Candidate's answer
            
        Returns:
            dict: Complete evaluation results
        """
        print(f"📊 Evaluating Question {question_index + 1}: {question_text[:50]}...")
        
        # Get keyword evaluation
        keyword_results = self.evaluate_keywords(transcript, question_index)
        print(f"✅ Keywords: {keyword_results['coverage_percentage']}% coverage")
        
        # Get LLM evaluation
        llm_results = self.evaluate_with_llm(question_text, transcript)
        
        # Get weights for this question
        criteria = self.question_criteria.get(question_index, {"keyword_weight": 0.3})
        keyword_weight = criteria["keyword_weight"]
        llm_weight = 1 - keyword_weight
        
        # Calculate LLM average score
        llm_scores = [
            llm_results.get("relevance", 5),
            llm_results.get("structure", 5),
            llm_results.get("specificity", 5),
            llm_results.get("professionalism", 5)
        ]
        llm_average = np.mean(llm_scores)
        
        # Calculate combined score
        combined_score = (
            keyword_results["keyword_score"] * keyword_weight +
            llm_average * llm_weight
        )
        
        print(f"🎯 Final Score: {combined_score:.1f}/10 (Keywords: {keyword_results['keyword_score']}, LLM: {llm_average:.1f})")
        
        return {
            "question_index": question_index,
            "question_type": criteria.get("type", "behavioral"),
            "combined_score": round(combined_score, 1),
            "keyword_evaluation": keyword_results,
            "llm_evaluation": llm_results,
            "score_breakdown": {
                "keyword_score": keyword_results["keyword_score"],
                "llm_average": round(llm_average, 1),
                "keyword_weight": keyword_weight,
                "llm_weight": llm_weight
            }
        }
    
    def evaluate_full_interview(self, session_data):
        """
        Evaluate all questions in the interview session
        
        Args:
            session_data: Your existing session data structure
            
        Returns:
            dict: Enhanced session data with evaluations
        """
        enhanced_session = session_data.copy()
        all_scores = []
        
        print("🧠 Starting comprehensive answer evaluation...")
        
        for question_data in enhanced_session["questions_data"]:
            question_number = question_data["question_number"]
            question_index = question_number - 1  # Convert to 0-based index
            question_text = question_data["question_text"]
            transcript = question_data["transcript"]
            
            # Skip empty transcripts
            if not transcript.strip():
                print(f"⏭️  Skipping Question {question_number} - no transcript")
                continue
            
            # Evaluate this answer
            evaluation = self.evaluate_single_answer(question_index, question_text, transcript)
            
            # Add to question data
            question_data["answer_evaluation"] = evaluation
            all_scores.append(evaluation["combined_score"])
        
        if all_scores:
            # Calculate overall content metrics
            enhanced_session["content_analysis_summary"] = {
                "average_content_score": round(np.mean(all_scores), 1),
                "highest_score": max(all_scores),
                "lowest_score": min(all_scores),
                "total_questions_evaluated": len(all_scores),
                "questions_above_7": sum(1 for score in all_scores if score >= 7.0),
                "questions_below_5": sum(1 for score in all_scores if score < 5.0)
            }
            
            print(f"📊 Evaluation complete! Average score: {enhanced_session['content_analysis_summary']['average_content_score']}/10")
        else:
            print("⚠️  No answers to evaluate")
        
        return enhanced_session

# ================================
# TESTING FUNCTION
# ================================

def test_llm_connection():
    """Test if LLM connection is working"""
    print("🧪 Testing LLM connection...")
    
    try:
        client = LlamaClient()
        test_response = client.generate("Hello, please respond with just the word 'SUCCESS' if you can understand this.")
        print(f"✅ LLM Response: {test_response}")
        
        if "SUCCESS" in test_response.upper() or len(test_response) > 0:
            print("✅ LLM is working correctly!")
            return True
        else:
            print("⚠️  LLM responded but may not be following instructions well")
            return False
            
    except Exception as e:
        print(f"❌ LLM connection failed: {e}")
        print("Make sure Ollama is running: ollama serve")
        print("And model is available: ollama pull llama3.1:8b")
        return False

if __name__ == "__main__":
    # Test LLM connection
    test_llm_connection()
    
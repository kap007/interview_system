
# ================================
# 5. LLM Client Integration Examples
# ================================

"""
OPTION A: OLLAMA INTEGRATION (Recommended)

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b
pip install ollama

# In answer_evaluator.py initialization:
import ollama

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

# In main_interview_system.py:
llm_client = LlamaClient()
self.answer_evaluator = AnswerEvaluator(llm_client=llm_client)

---

OPTION B: TRANSFORMERS (Local)

# Install transformers
pip install transformers torch accelerate

# In answer_evaluator.py:
from transformers import pipeline

class LlamaClient:
    def __init__(self):
        self.generator = pipeline(
            "text-generation",
            model="meta-llama/Llama-3.1-8B-Instruct",
            device_map="auto",
            torch_dtype="auto"
        )
    
    def generate(self, prompt):
        try:
            result = self.generator(
                prompt,
                max_new_tokens=500,
                temperature=0.7,
                do_sample=True,
                return_full_text=False
            )
            return result[0]['generated_text']
        except Exception as e:
            return f'{{"error": "LLM generation failed: {str(e)}"}}'
"""

# ================================
# 6. Testing Script
# ================================

"""
# test_integration.py

from answer_evaluator import AnswerEvaluator

def test_answer_evaluation():
    print("🧪 TESTING ANSWER EVALUATION SYSTEM")
    print("=" * 50)
    
    # Initialize without LLM for testing
    evaluator = AnswerEvaluator(llm_client=None)
    
    # Test cases
    test_cases = [
        {
            "question_index": 0,
            "question": "Tell me about yourself and your background.",
            "transcript": "I have a background in computer science with 3 years of experience in software development. I have strong skills in Python and have worked on various projects."
        },
        {
            "question_index": 2, 
            "question": "What are your greatest strengths?",
            "transcript": "My greatest strength is my problem-solving skill. For example, in my last project, I identified a performance bottleneck and improved the system speed by 40%."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🔍 TEST {i}:")
        print(f"Question: {test['question']}")
        print(f"Answer: {test['transcript'][:100]}...")
        
        result = evaluator.evaluate_single_answer(
            test['question_index'],
            test['question'], 
            test['transcript']
        )
        
        print(f"✅ Combined Score: {result['combined_score']}/10")
        print(f"📊 Keyword Score: {result['score_breakdown']['keyword_score']}/10")
        print(f"🤖 LLM Score: {result['score_breakdown']['llm_average']}/10")
        print(f"🔍 Keywords Found: {result['keyword_evaluation']['found_required']}")
        print(f"❌ Missing: {result['keyword_evaluation']['missing_required']}")
        print(f"📈 Coverage: {result['keyword_evaluation']['coverage_percentage']}%")
    
    print("\n✅ TESTING COMPLETE!")

if __name__ == "__main__":
    test_answer_evaluation()
"""

print("🎯 COMPLETE INTERVIEW SYSTEM WITH ANSWER EVALUATION")
print("=" * 60)
print("📁 FILES PROVIDED:")
print("1. ✅ answer_evaluator.py - NEW evaluation system")
print("2. ✅ main_interview_system.py - UPDATED with evaluation")  
print("3. ✅ report_generator.py - UPDATED with content analysis")
print("4. ✅ requirements.txt - UPDATED with LLM dependencies")
print("5. ✅ LLM integration examples")
print("6. ✅ Testing script")
print("\n🚀 Ready for deployment with comprehensive interview analysis!")
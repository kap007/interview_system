# ================================
# ENHANCED answer_evaluator.py - KEYWORD-ONLY VERSION
# No LLM dependencies - Pure keyword matching with advanced techniques
# ================================

import re
import json
import numpy as np
from collections import defaultdict, Counter
from difflib import SequenceMatcher

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

class AdvancedKeywordEvaluator:
    def __init__(self):
        """
        Enhanced keyword-based evaluator with no LLM dependencies
        Uses sophisticated matching techniques and scoring algorithms
        """
        
        # Initialize spaCy for better text processing (optional)
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("✅ spaCy loaded for enhanced text processing")
            except OSError:
                print("⚠️  spaCy model not found - using basic text processing")
        
        # Enhanced question criteria with multiple matching strategies
        self.question_criteria = self._initialize_enhanced_criteria()
        
        # Semantic word groups for better matching
        self.semantic_groups = self._initialize_semantic_groups()
        
        # Common synonyms for key concepts
        self.synonyms = self._initialize_synonyms()
    
    def _initialize_enhanced_criteria(self):
        """
        Python/SQL specific keyword criteria
        """
        return {
            # Question 1: Python experience and projects
            0: {
                "type": "python_experience",
                "essential_keywords": {
                    "experience": ["python", "programming", "experience", "years", "worked"],
                    "projects": ["project", "application", "system", "built", "developed"],
                    "technologies": ["framework", "library", "tool", "technology", "stack"]
                },
                "bonus_keywords": {
                    "specific_frameworks": ["django", "flask", "fastapi", "pyramid", "tornado"],
                    "libraries": ["pandas", "numpy", "requests", "matplotlib", "scikit-learn"],
                    "deployment": ["aws", "docker", "kubernetes", "heroku", "azure"],
                    "version_control": ["git", "github", "version control", "repository"]
                },
                "negative_keywords": ["never used", "don't know", "basic only", "just started"],
                "context_patterns": [
                    r"(\d+)\s+years?\s+(of\s+)?python",
                    r"built\s+(a|an)\s+\w+\s+(application|system)",
                    r"used\s+\w+\s+(framework|library)",
                    r"deployed\s+(to|on)\s+\w+"
                ],
                "length_expectations": {"min_words": 30, "optimal_words": 80, "max_words": 180},
                "scoring_weights": {"essential": 0.6, "bonus": 0.3, "structure": 0.1}
            },
            
            # Question 2: Lists vs Tuples
            1: {
                "type": "python_fundamentals",
                "essential_keywords": {
                    "data_types": ["list", "tuple", "difference", "mutable", "immutable"],
                    "characteristics": ["ordered", "indexed", "changeable", "modify", "elements"],
                    "use_cases": ["use", "when", "choose", "scenario", "situation"]
                },
                "bonus_keywords": {
                    "technical_details": ["memory", "performance", "iteration", "slicing", "indexing"],
                    "examples": ["example", "instance", "case", "situation", "scenario"],
                    "methods": ["append", "extend", "remove", "pop", "sort"]
                },
                "negative_keywords": ["same thing", "no difference", "don't know"],
                "context_patterns": [
                    r"list.*mutable.*tuple.*immutable",
                    r"tuple.*immutable.*list.*mutable", 
                    r"use\s+list\s+when",
                    r"use\s+tuple\s+when"
                ],
                "length_expectations": {"min_words": 25, "optimal_words": 60, "max_words": 120},
                "scoring_weights": {"essential": 0.7, "bonus": 0.2, "structure": 0.1}
            },
            
            # Question 3: Exception handling
            2: {
                "type": "python_error_handling",
                "essential_keywords": {
                    "exception_basics": ["exception", "error", "try", "except", "handle"],
                    "structure": ["try block", "except block", "finally", "else", "raise"],
                    "examples": ["example", "code", "demonstrate", "show", "implement"]
                },
                "bonus_keywords": {
                    "specific_exceptions": ["valueerror", "typeerror", "indexerror", "keyerror", "filenotfounderror"],
                    "best_practices": ["specific", "generic", "logging", "graceful", "user friendly"],
                    "advanced": ["custom exception", "exception chaining", "traceback", "debugging"]
                },
                "negative_keywords": ["avoid errors", "don't handle", "ignore exceptions"],
                "context_patterns": [
                    r"try:\s*.*\s*except",
                    r"except\s+\w+Error",
                    r"finally\s+block",
                    r"raise\s+\w+"
                ],
                "length_expectations": {"min_words": 30, "optimal_words": 70, "max_words": 150},
                "scoring_weights": {"essential": 0.6, "bonus": 0.3, "structure": 0.1}
            },
            
            # Question 4: SQL JOINs
            3: {
                "type": "sql_joins",
                "essential_keywords": {
                    "join_types": ["inner join", "left join", "right join", "outer join", "full outer"],
                    "concepts": ["table", "relationship", "match", "record", "row"],
                    "explanation": ["difference", "when", "use", "returns", "result"]
                },
                "bonus_keywords": {
                    "technical_details": ["foreign key", "primary key", "null", "cartesian product"],
                    "examples": ["example", "scenario", "case", "customers", "orders"],
                    "performance": ["performance", "index", "optimization", "efficiency"]
                },
                "negative_keywords": ["all the same", "don't know difference", "confusing"],
                "context_patterns": [
                    r"inner\s+join.*returns.*matching",
                    r"left\s+join.*returns.*all.*left",
                    r"right\s+join.*returns.*all.*right",
                    r"outer\s+join.*returns.*all"
                ],
                "length_expectations": {"min_words": 35, "optimal_words": 80, "max_words": 160},
                "scoring_weights": {"essential": 0.7, "bonus": 0.2, "structure": 0.1}
            },
            
            # Question 5: SQL Query optimization
            4: {
                "type": "sql_performance",
                "essential_keywords": {
                    "optimization_techniques": ["index", "query plan", "optimize", "performance", "slow"],
                    "analysis": ["explain", "analyze", "execution", "bottleneck", "identify"],
                    "solutions": ["improve", "faster", "efficient", "reduce", "time"]
                },
                "bonus_keywords": {
                    "specific_techniques": ["covering index", "composite index", "statistics", "partitioning"],
                    "tools": ["profiler", "execution plan", "query analyzer", "monitoring"],
                    "advanced": ["materialized view", "denormalization", "caching", "sharding"]
                },
                "negative_keywords": ["can't optimize", "always fast", "don't check performance"],
                "context_patterns": [
                    r"add.*index.*on",
                    r"explain.*plan",
                    r"rewrite.*query",
                    r"avoid.*select.*\*"
                ],
                "length_expectations": {"min_words": 30, "optimal_words": 70, "max_words": 140},
                "scoring_weights": {"essential": 0.6, "bonus": 0.3, "structure": 0.1}
            },
            
            # Question 6: Python decorators
            5: {
                "type": "python_advanced",
                "essential_keywords": {
                    "decorator_basics": ["decorator", "function", "wrapper", "modify", "behavior"],
                    "syntax": ["@", "symbol", "syntax", "above", "before"],
                    "purpose": ["use", "when", "why", "purpose", "benefit"]
                },
                "bonus_keywords": {
                    "examples": ["@property", "@staticmethod", "@classmethod", "@wraps"],
                    "concepts": ["closure", "first class", "higher order", "functional"],
                    "use_cases": ["logging", "timing", "authentication", "validation", "caching"]
                },
                "negative_keywords": ["too complex", "never use", "don't understand"],
                "context_patterns": [
                    r"@\w+",
                    r"def\s+\w+\(func\)",
                    r"wrapper.*function",
                    r"return.*wrapper"
                ],
                "length_expectations": {"min_words": 25, "optimal_words": 65, "max_words": 130},
                "scoring_weights": {"essential": 0.6, "bonus": 0.3, "structure": 0.1}
            },
            
            # Question 7: Python generators
            6: {
                "type": "python_advanced",
                "essential_keywords": {
                    "generator_basics": ["generator", "yield", "function", "iterator", "difference"],
                    "memory": ["memory", "efficient", "lazy", "evaluation", "space"],
                    "behavior": ["one at a time", "iterate", "next", "value", "state"]
                },
                "bonus_keywords": {
                    "syntax": ["yield from", "generator expression", "comprehension"],
                    "use_cases": ["large data", "streaming", "pipeline", "processing"],
                    "concepts": ["coroutine", "send", "throw", "close", "protocol"]
                },
                "negative_keywords": ["same as function", "don't see benefit", "complicated"],
                "context_patterns": [
                    r"yield\s+\w+",
                    r"def\s+\w+.*yield",
                    r"memory.*efficient",
                    r"lazy.*evaluation"
                ],
                "length_expectations": {"min_words": 25, "optimal_words": 60, "max_words": 120},
                "scoring_weights": {"essential": 0.7, "bonus": 0.2, "structure": 0.1}
            },
            
            # Question 8: SQL injection prevention
            7: {
                "type": "sql_security",
                "essential_keywords": {
                    "security_basics": ["sql injection", "prevent", "attack", "security", "vulnerability"],
                    "techniques": ["parameterized", "prepared statement", "bind", "escape", "sanitize"],
                    "best_practices": ["validate", "input", "user data", "never", "concatenate"]
                },
                "bonus_keywords": {
                    "specific_methods": ["placeholder", "question mark", "named parameter"],
                    "frameworks": ["orm", "sqlalchemy", "django orm", "active record"],
                    "validation": ["whitelist", "type checking", "length limit", "regex"]
                },
                "negative_keywords": ["not important", "never happens", "don't worry about"],
                "context_patterns": [
                    r"parameterized.*query",
                    r"prepared.*statement",
                    r"never.*concatenate.*user.*input",
                    r"validate.*input"
                ],
                "length_expectations": {"min_words": 30, "optimal_words": 70, "max_words": 140},
                "scoring_weights": {"essential": 0.7, "bonus": 0.2, "structure": 0.1}
            },
            
            # Question 9: Python libraries experience
            8: {
                "type": "python_libraries",
                "essential_keywords": {
                    "libraries": ["pandas", "numpy", "requests", "library", "experience"],
                    "usage": ["use", "used", "work", "project", "implement"],
                    "purpose": ["data", "analysis", "processing", "http", "api"]
                },
                "bonus_keywords": {
                    "specific_functions": ["dataframe", "array", "get", "post", "json"],
                    "advanced": ["matplotlib", "seaborn", "scipy", "sklearn", "tensorflow"],
                    "real_world": ["production", "scale", "performance", "optimization"]
                },
                "negative_keywords": ["never used", "only heard of", "too complex"],
                "context_patterns": [
                    r"pandas.*dataframe",
                    r"numpy.*array", 
                    r"requests.*get|post",
                    r"import\s+\w+"
                ],
                "length_expectations": {"min_words": 25, "optimal_words": 65, "max_words": 130},
                "scoring_weights": {"essential": 0.6, "bonus": 0.3, "structure": 0.1}
            },
            
            # Question 10: Database schema design
            9: {
                "type": "database_design",
                "essential_keywords": {
                    "design_basics": ["schema", "design", "database", "table", "relationship"],
                    "ecommerce": ["user", "product", "order", "customer", "inventory"],
                    "structure": ["primary key", "foreign key", "normalize", "entity"]
                },
                "bonus_keywords": {
                    "advanced_design": ["normalization", "denormalization", "index", "constraint"],
                    "ecommerce_specific": ["cart", "payment", "shipping", "category", "review"],
                    "performance": ["partitioning", "sharding", "replication", "scaling"]
                },
                "negative_keywords": ["one big table", "don't need relationships", "simple is better"],
                "context_patterns": [
                    r"users?.*table",
                    r"products?.*table",
                    r"orders?.*table",
                    r"one.*to.*many|many.*to.*one"
                ],
                "length_expectations": {"min_words": 35, "optimal_words": 80, "max_words": 160},
                "scoring_weights": {"essential": 0.6, "bonus": 0.3, "structure": 0.1}
            }
        }
    def _initialize_semantic_groups(self):
        """
        Semantic word groups for Python/SQL interviews
        """
        return {
            "python_concepts": [
                "object oriented", "functional", "procedural", "interpreted", 
                "dynamic typing", "duck typing", "pythonic", "pep8"
            ],
            "python_data_structures": [
                "dictionary", "set", "frozenset", "deque", "counter", 
                "defaultdict", "namedtuple", "dataclass"
            ],
            "sql_operations": [
                "select", "insert", "update", "delete", "create", "drop", 
                "alter", "grant", "revoke", "commit", "rollback"
            ],
            "database_concepts": [
                "acid", "transaction", "isolation", "consistency", "durability",
                "atomicity", "concurrency", "locking", "deadlock"
            ],
            "python_libraries": [
                "django", "flask", "requests", "pandas", "numpy", "matplotlib",
                "seaborn", "sqlalchemy", "pytest", "unittest"
            ],
            "sql_functions": [
                "count", "sum", "avg", "max", "min", "group by", "order by",
                "having", "distinct", "union", "intersect", "except"
            ],
            "performance_terms": [
                "optimization", "indexing", "caching", "profiling", "benchmarking",
                "bottleneck", "scalability", "efficiency", "throughput"
            ],
            "achievement_words": [
                "achieved", "accomplished", "completed", "delivered", "exceeded", 
                "improved", "increased", "reduced", "optimized", "enhanced"
            ],
            "leadership_words": [
                "led", "managed", "coordinated", "organized", "supervised", 
                "guided", "mentored", "facilitated", "directed", "oversaw"
            ],
            "collaboration_words": [
                "collaborated", "cooperated", "partnered", "worked together", 
                "team effort", "coordinated", "supported", "contributed"
            ],
            "problem_solving_words": [
                "solved", "resolved", "addressed", "tackled", "overcame", 
                "analyzed", "identified", "implemented", "developed"
            ],
            "communication_words": [
                "communicated", "presented", "explained", "discussed", 
                "negotiated", "persuaded", "clarified", "documented"
            ]
        }
    
    def _initialize_synonyms(self):
        """
        Synonyms for Python/SQL terms
        """
        return {
            # General terms
            "experience": ["background", "history", "track record", "expertise"],
            "skills": ["abilities", "capabilities", "competencies", "expertise"],
            "improve": ["enhance", "develop", "better", "upgrade", "advance"],
            "implement": ["code", "develop", "build", "create", "program"],
            
            # Python-specific
            "function": ["method", "procedure", "subroutine", "callable", "def"],
            "variable": ["identifier", "name", "reference", "symbol"],
            "framework": ["library", "toolkit", "package", "module"],
            "list": ["array", "sequence", "collection"],
            "dictionary": ["dict", "hash", "map", "associative array"],
            
            # SQL-specific  
            "database": ["db", "data store", "repository", "warehouse"],
            "query": ["statement", "command", "sql", "request"],
            "table": ["relation", "entity", "dataset", "collection"],
            "record": ["row", "tuple", "entry", "item"],
            "field": ["column", "attribute", "property", "element"],
            "join": ["link", "connect", "merge", "combine"],
            
            # Performance terms
            "optimize": ["improve", "enhance", "tune", "refactor", "speed up"],
            "slow": ["sluggish", "poor performance", "bottleneck", "inefficient"],
            "fast": ["quick", "efficient", "optimized", "performant"],
            
            # General technical
            "bug": ["error", "issue", "defect", "problem"],
            "fix": ["resolve", "solve", "correct", "repair"],
            "test": ["validate", "verify", "check", "examine"]
        }
    
    def evaluate_keywords_advanced(self, transcript, question_index):
        """
        Advanced keyword evaluation with multiple matching strategies
        """
        if question_index not in self.question_criteria:
            return {"keyword_score": 0, "details": "Question not found"}
        
        criteria = self.question_criteria[question_index]
        
        # Clean and prepare text
        transcript_clean = self._clean_text(transcript)
        
        # Multiple matching strategies
        exact_matches = self._find_exact_matches(transcript_clean, criteria)
        semantic_matches = self._find_semantic_matches(transcript_clean, criteria)
        pattern_matches = self._find_pattern_matches(transcript, criteria)
        synonym_matches = self._find_synonym_matches(transcript_clean, criteria)
        
        # Calculate scores for each category
        essential_score = self._calculate_category_score(
            exact_matches["essential"], semantic_matches["essential"], 
            criteria["essential_keywords"]
        )
        
        bonus_score = self._calculate_category_score(
            exact_matches["bonus"], semantic_matches["bonus"], 
            criteria["bonus_keywords"]
        )
        
        # Structure and length analysis
        structure_score = self._analyze_structure(transcript, criteria)
        
        # Apply weights
        weights = criteria["scoring_weights"]
        final_score = (
            essential_score * weights["essential"] + 
            bonus_score * weights["bonus"] + 
            structure_score * weights["structure"]
        ) * 10  # Scale to 0-10
        
        # Apply penalties
        negative_penalty = self._calculate_negative_penalty(transcript_clean, criteria)
        final_score = max(0, final_score - negative_penalty)
        
        return {
            "keyword_score": round(min(10, final_score), 1),
            "detailed_breakdown": {
                "essential_score": round(essential_score, 2),
                "bonus_score": round(bonus_score, 2),
                "structure_score": round(structure_score, 2),
                "negative_penalty": negative_penalty
            },
            "matches_found": {
                "exact": exact_matches,
                "semantic": semantic_matches,
                "patterns": pattern_matches,
                "synonyms": synonym_matches
            },
            "coverage_analysis": self._analyze_coverage(exact_matches, semantic_matches, criteria),
            "improvement_suggestions": self._generate_suggestions(exact_matches, criteria)
        }
    
    def _clean_text(self, text):
        """Clean and normalize text for better matching"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Handle contractions
        text = re.sub(r"won't", "will not", text)
        text = re.sub(r"can't", "cannot", text)
        text = re.sub(r"n't", " not", text)
        text = re.sub(r"'re", " are", text)
        text = re.sub(r"'ve", " have", text)
        text = re.sub(r"'ll", " will", text)
        text = re.sub(r"'d", " would", text)
        
        return text
    
    def _find_exact_matches(self, text, criteria):
        """Find exact keyword matches"""
        matches = {"essential": defaultdict(list), "bonus": defaultdict(list)}
        
        for category in ["essential", "bonus"]:
            keyword_groups = criteria[f"{category}_keywords"]
            for group_name, keywords in keyword_groups.items():
                for keyword in keywords:
                    if self._is_keyword_present(text, keyword):
                        matches[category][group_name].append(keyword)
        
        return matches
    
    def _find_semantic_matches(self, text, criteria):
        """Find semantic matches using word groups"""
        matches = {"essential": defaultdict(list), "bonus": defaultdict(list)}
        
        # Use semantic groups to find related words
        for category in ["essential", "bonus"]:
            keyword_groups = criteria[f"{category}_keywords"]
            for group_name, keywords in keyword_groups.items():
                for semantic_group_name, semantic_words in self.semantic_groups.items():
                    if any(kw in semantic_group_name or semantic_group_name in kw for kw in keywords):
                        for semantic_word in semantic_words:
                            if self._is_keyword_present(text, semantic_word):
                                matches[category][group_name].append(f"{semantic_word} (semantic)")
        
        return matches
    
    def _find_pattern_matches(self, text, criteria):
        """Find pattern matches using regex"""
        matches = []
        if "context_patterns" in criteria:
            for pattern in criteria["context_patterns"]:
                found = re.findall(pattern, text, re.IGNORECASE)
                if found:
                    matches.extend(found)
        return matches
    
    def _find_synonym_matches(self, text, criteria):
        """Find matches using synonyms"""
        matches = {"essential": defaultdict(list), "bonus": defaultdict(list)}
        
        for category in ["essential", "bonus"]:
            keyword_groups = criteria[f"{category}_keywords"]
            for group_name, keywords in keyword_groups.items():
                for keyword in keywords:
                    if keyword in self.synonyms:
                        for synonym in self.synonyms[keyword]:
                            if self._is_keyword_present(text, synonym):
                                matches[category][group_name].append(f"{synonym} (synonym for {keyword})")
        
        return matches
    
    def _is_keyword_present(self, text, keyword):
        """Check if keyword is present with flexible matching"""
        # Exact phrase match
        if keyword in text:
            return True
        
        # Word boundary match for multi-word phrases
        if ' ' in keyword:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            return bool(re.search(pattern, text))
        
        # Single word with boundaries
        pattern = r'\b' + re.escape(keyword) + r'\b'
        return bool(re.search(pattern, text))
    
    def _calculate_category_score(self, exact_matches, semantic_matches, keyword_groups):
        """Calculate score for a category (essential/bonus)"""
        total_groups = len(keyword_groups)
        if total_groups == 0:
            return 1.0
        
        groups_covered = 0
        for group_name in keyword_groups.keys():
            exact_count = len(exact_matches.get(group_name, []))
            semantic_count = len(semantic_matches.get(group_name, []))
            
            if exact_count > 0:
                groups_covered += 1.0
            elif semantic_count > 0:
                groups_covered += 0.7  # Semantic matches get partial credit
        
        return groups_covered / total_groups
    
    def _analyze_structure(self, text, criteria):
        """Analyze answer structure and length"""
        words = text.split()
        word_count = len(words)
        
        length_expectations = criteria["length_expectations"]
        min_words = length_expectations["min_words"]
        optimal_words = length_expectations["optimal_words"]
        max_words = length_expectations["max_words"]
        
        # Length scoring
        if word_count < min_words:
            length_score = word_count / min_words * 0.5  # Penalty for too short
        elif word_count <= optimal_words:
            length_score = 0.5 + (word_count - min_words) / (optimal_words - min_words) * 0.5
        elif word_count <= max_words:
            length_score = 1.0 - (word_count - optimal_words) / (max_words - optimal_words) * 0.2
        else:
            length_score = 0.8 - min((word_count - max_words) / 50, 0.3)  # Penalty for too long
        
        # Structure indicators (examples, transitions, etc.)
        structure_indicators = [
            "for example", "for instance", "such as", "specifically",
            "first", "second", "then", "next", "finally", "in conclusion",
            "as a result", "therefore", "consequently", "however"
        ]
        
        structure_bonus = 0
        text_lower = text.lower()
        for indicator in structure_indicators:
            if indicator in text_lower:
                structure_bonus += 0.1
        
        structure_bonus = min(structure_bonus, 0.3)  # Cap bonus at 0.3
        
        return min(1.0, length_score + structure_bonus)
    
    def _calculate_negative_penalty(self, text, criteria):
        """Calculate penalty for negative keywords"""
        penalty = 0
        negative_keywords = criteria.get("negative_keywords", [])
        
        for neg_keyword in negative_keywords:
            if self._is_keyword_present(text, neg_keyword):
                penalty += 1.0
        
        return penalty
    
    def _analyze_coverage(self, exact_matches, semantic_matches, criteria):
        """Analyze keyword coverage"""
        total_essential_groups = len(criteria["essential_keywords"])
        total_bonus_groups = len(criteria["bonus_keywords"])
        
        essential_covered = len([g for g in criteria["essential_keywords"].keys() 
                               if exact_matches["essential"].get(g) or semantic_matches["essential"].get(g)])
        
        bonus_covered = len([g for g in criteria["bonus_keywords"].keys() 
                           if exact_matches["bonus"].get(g) or semantic_matches["bonus"].get(g)])
        
        return {
            "essential_coverage": round(essential_covered / total_essential_groups * 100, 1) if total_essential_groups > 0 else 100,
            "bonus_coverage": round(bonus_covered / total_bonus_groups * 100, 1) if total_bonus_groups > 0 else 100,
            "essential_groups_covered": f"{essential_covered}/{total_essential_groups}",
            "bonus_groups_covered": f"{bonus_covered}/{total_bonus_groups}"
        }
    
    def _generate_suggestions(self, exact_matches, criteria):
        """Generate improvement suggestions based on missing keywords"""
        suggestions = []
        
        # Check essential keywords
        for group_name, keywords in criteria["essential_keywords"].items():
            if not exact_matches["essential"].get(group_name):
                suggestions.append(f"Consider mentioning {group_name.replace('_', ' ')}: {', '.join(keywords[:3])}")
        
        # Structure suggestions
        if criteria["type"] == "behavioral_STAR":
            suggestions.append("Use the STAR method: Situation, Task, Action, Result")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def evaluate_single_answer(self, question_index, question_text, transcript):
        """
        Complete evaluation for one question using only keyword matching
        """
        print(f"📊 Evaluating Question {question_index + 1}: {question_text[:50]}...")
        
        # Get enhanced keyword evaluation
        keyword_results = self.evaluate_keywords_advanced(transcript, question_index)
        print(f"✅ Keywords: {keyword_results['coverage_analysis']['essential_coverage']}% essential coverage")
        
        # Get question type and expectations
        criteria = self.question_criteria.get(question_index, {"type": "general"})
        
        return {
            "question_index": question_index,
            "question_type": criteria.get("type", "general"),
            "combined_score": keyword_results["keyword_score"],
            "keyword_evaluation": keyword_results,
            "score_breakdown": {
                "keyword_score": keyword_results["keyword_score"],
                "scoring_method": "Advanced Keyword Matching",
                "components": keyword_results["detailed_breakdown"]
            },
            "coverage_analysis": keyword_results["coverage_analysis"],
            "improvement_suggestions": keyword_results["improvement_suggestions"]
        }
    
    def evaluate_full_interview(self, session_data):
        """
        Evaluate all questions in the interview session
        """
        enhanced_session = session_data.copy()
        all_scores = []
        
        print("🧠 Starting comprehensive keyword-based evaluation...")
        
        for question_data in enhanced_session["questions_data"]:
            question_number = question_data["question_number"]
            question_index = question_number - 1
            question_text = question_data["question_text"]
            transcript = question_data["transcript"]
            
            if not transcript.strip():
                print(f"⏭️  Skipping Question {question_number} - no transcript")
                continue
            
            # Evaluate this answer
            evaluation = self.evaluate_single_answer(question_index, question_text, transcript)
            
            # Add to question data
            question_data["answer_evaluation"] = evaluation
            all_scores.append(evaluation["combined_score"])
        
        if all_scores:
            # Calculate comprehensive metrics
            enhanced_session["content_analysis_summary"] = {
                "average_content_score": round(np.mean(all_scores), 1),
                "highest_score": max(all_scores),
                "lowest_score": min(all_scores),
                "total_questions_evaluated": len(all_scores),
                "questions_above_7": sum(1 for score in all_scores if score >= 7.0),
                "questions_below_5": sum(1 for score in all_scores if score < 5.0),
                "score_distribution": {
                    "excellent (8-10)": sum(1 for score in all_scores if score >= 8.0),
                    "good (6-7.9)": sum(1 for score in all_scores if 6.0 <= score < 8.0),
                    "fair (4-5.9)": sum(1 for score in all_scores if 4.0 <= score < 6.0),
                    "poor (0-3.9)": sum(1 for score in all_scores if score < 4.0)
                },
                "evaluation_method": "Advanced Keyword Matching with Semantic Analysis"
            }
            
            print(f"📊 Evaluation complete! Average score: {enhanced_session['content_analysis_summary']['average_content_score']}/10")
        else:
            print("⚠️  No answers to evaluate")
        
        return enhanced_session

if __name__ == "__main__":
    print("🚀 ENHANCED KEYWORD-BASED ANSWER EVALUATOR")
    print("=" * 55)
    print("Features:")
    print("✅ No LLM dependencies")
    print("✅ Advanced keyword matching with semantic analysis")
    print("✅ Synonym recognition")
    print("✅ Pattern matching with regex")
    print("✅ Structure and length analysis")
    print("✅ Detailed scoring breakdown")
    print("✅ Improvement suggestions")
    print()
    
    
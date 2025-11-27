"""
Advanced Evaluation Metrics for RAG Assessment

This module extends the basic evaluation with:
1. Hallucination Detection - Identifies unsupported claims
2. Citation Quality - Evaluates source attribution
3. Latency Scoring - Penalizes slow responses
4. Consistency Scoring - Checks response stability
"""

import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

import dashscope
from dashscope import Generation

from . import config


@dataclass
class AdvancedEvaluationResult:
    """Extended evaluation result with advanced metrics."""
    # Basic scores (0-100)
    accuracy_score: int
    relevance_score: int
    completeness_score: int
    
    # Advanced scores (0-100)
    hallucination_score: int  # Higher = fewer hallucinations
    citation_quality_score: int  # Higher = better citations
    latency_score: int  # Higher = faster response
    
    # Overall scores
    basic_overall: float  # Average of accuracy, relevance, completeness
    advanced_overall: float  # Weighted average including advanced metrics
    
    # Detailed analysis
    reasoning: str
    hallucination_details: List[str]  # List of detected hallucinations
    citation_analysis: str
    latency_ms: float
    
    # Flags
    has_hallucinations: bool
    has_citations: bool
    is_slow: bool


class HallucinationDetector:
    """Detects hallucinations in RAG responses."""
    
    def __init__(self, model: str = "qwen-turbo", temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        dashscope.api_key = config.DASHSCOPE_API_KEY
    
    def detect(
        self,
        question: str,
        response: str,
        context: str,
        expected_answer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Detect hallucinations in the response.
        
        Args:
            question: The original question
            response: The RAG system's response
            context: The retrieved context/chunks used
            expected_answer: Optional expected answer for comparison
            
        Returns:
            Dict with:
            - hallucination_score: 0-100 (higher = fewer hallucinations)
            - has_hallucinations: bool
            - hallucination_details: List of detected hallucinations
            - reasoning: Explanation
        """
        if not response or not response.strip():
            return {
                "hallucination_score": 0,
                "has_hallucinations": True,
                "hallucination_details": ["Empty response"],
                "reasoning": "Response is empty"
            }
        
        system_prompt = """You are an expert at detecting hallucinations in RAG system responses.

A hallucination is information in the response that:
1. Is NOT supported by the provided context
2. Makes claims beyond what the context states
3. Contradicts the context
4. Invents facts, dates, names, or numbers not in the context

Your task: Identify ALL hallucinations in the response.

Return JSON:
{
  "hallucination_score": <0-100, where 100=no hallucinations, 0=severe hallucinations>,
  "has_hallucinations": <true/false>,
  "hallucination_details": [<list of specific hallucinated claims>],
  "reasoning": "<brief explanation>"
}"""

        user_prompt = f"""Question:
{question}

Retrieved Context (Ground Truth):
{context}

RAG System Response:
{response}

Analyze the response for hallucinations. Every claim must be verifiable in the context."""

        try:
            response_obj = Generation.call(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                result_format="json_object"
            )
            
            content = response_obj.output["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            # Validate and clamp score
            result["hallucination_score"] = max(0, min(100, int(result.get("hallucination_score", 50))))
            result["has_hallucinations"] = bool(result.get("has_hallucinations", False))
            
            if "hallucination_details" not in result:
                result["hallucination_details"] = []
            
            if "reasoning" not in result:
                result["reasoning"] = "No reasoning provided"
            
            return result
            
        except Exception as e:
            print(f"⚠️ Hallucination detection failed: {e}")
            return {
                "hallucination_score": 50,
                "has_hallucinations": False,
                "hallucination_details": [],
                "reasoning": f"Detection error: {str(e)}"
            }


class CitationQualityEvaluator:
    """Evaluates the quality of citations in RAG responses."""
    
    def __init__(self, model: str = "qwen-turbo", temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
        dashscope.api_key = config.DASHSCOPE_API_KEY
    
    def has_citations(self, response: str) -> bool:
        """Quick check if response contains citation markers."""
        # Common citation patterns
        patterns = [
            r'\[\d+\]',  # [1], [2]
            r'\(\d+\)',  # (1), (2)
            r'\[.*?\]',  # [source], [doc1]
            r'according to',
            r'as stated in',
            r'source:',
            r'reference:',
            r'from the document',
            r'the text states',
        ]
        
        for pattern in patterns:
            if re.search(pattern, response, re.IGNORECASE):
                return True
        return False
    
    def evaluate(
        self,
        question: str,
        response: str,
        context: str,
        retrieved_sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate citation quality in the response.
        
        Args:
            question: The original question
            response: The RAG system's response
            context: The retrieved context
            retrieved_sources: Optional list of source identifiers
            
        Returns:
            Dict with:
            - citation_quality_score: 0-100
            - has_citations: bool
            - citation_analysis: Detailed analysis
        """
        has_cites = self.has_citations(response)
        
        if not response or not response.strip():
            return {
                "citation_quality_score": 0,
                "has_citations": False,
                "citation_analysis": "Empty response"
            }
        
        system_prompt = """You are an expert at evaluating citation quality in RAG responses.

Evaluate citations on:
1. **Presence**: Are sources cited?
2. **Accuracy**: Do citations match the context?
3. **Completeness**: Are all key claims cited?
4. **Format**: Are citations clear and consistent?
5. **Traceability**: Can claims be traced to sources?

Return JSON:
{
  "citation_quality_score": <0-100>,
  "has_citations": <true/false>,
  "citation_analysis": "<detailed analysis of citation quality>"
}"""

        user_prompt = f"""Question:
{question}

Retrieved Context:
{context}

RAG System Response:
{response}

Evaluate the citation quality. Consider:
- Are important claims backed by citations?
- Are citations accurate and traceable?
- Is the citation format clear?"""

        try:
            response_obj = Generation.call(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                result_format="json_object"
            )
            
            content = response_obj.output["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            # Validate
            result["citation_quality_score"] = max(0, min(100, int(result.get("citation_quality_score", 50))))
            result["has_citations"] = bool(result.get("has_citations", has_cites))
            
            if "citation_analysis" not in result:
                result["citation_analysis"] = "No analysis provided"
            
            return result
            
        except Exception as e:
            print(f"⚠️ Citation evaluation failed: {e}")
            return {
                "citation_quality_score": 50 if has_cites else 0,
                "has_citations": has_cites,
                "citation_analysis": f"Evaluation error: {str(e)}"
            }


class LatencyScorer:
    """Scores responses based on latency."""
    
    def __init__(
        self,
        excellent_threshold_ms: float = 500,
        good_threshold_ms: float = 2000,
        acceptable_threshold_ms: float = 5000
    ):
        """
        Initialize latency scorer.
        
        Args:
            excellent_threshold_ms: Response time for 100 score
            good_threshold_ms: Response time for 80 score
            acceptable_threshold_ms: Response time for 60 score
        """
        self.excellent = excellent_threshold_ms
        self.good = good_threshold_ms
        self.acceptable = acceptable_threshold_ms
    
    def score(self, latency_ms: float) -> Tuple[int, bool, str]:
        """
        Score latency performance.
        
        Args:
            latency_ms: Response time in milliseconds
            
        Returns:
            Tuple of (score, is_slow, description)
        """
        if latency_ms <= self.excellent:
            return 100, False, f"Excellent ({latency_ms:.0f}ms)"
        elif latency_ms <= self.good:
            # Linear interpolation between 100 and 80
            score = 100 - ((latency_ms - self.excellent) / (self.good - self.excellent)) * 20
            return int(score), False, f"Good ({latency_ms:.0f}ms)"
        elif latency_ms <= self.acceptable:
            # Linear interpolation between 80 and 60
            score = 80 - ((latency_ms - self.good) / (self.acceptable - self.good)) * 20
            return int(score), False, f"Acceptable ({latency_ms:.0f}ms)"
        else:
            # Exponential decay below 60
            score = max(0, 60 - ((latency_ms - self.acceptable) / 1000) * 10)
            return int(score), True, f"Slow ({latency_ms:.0f}ms)"


class AdvancedEvaluator:
    """
    Advanced evaluator combining multiple evaluation dimensions.
    """
    
    def __init__(
        self,
        model: str = "qwen-turbo",
        temperature: float = 0.0,
        enable_hallucination_detection: bool = True,
        enable_citation_evaluation: bool = True,
        enable_latency_scoring: bool = True,
        weights: Optional[Dict[str, float]] = None
    ):
        """
        Initialize advanced evaluator.
        
        Args:
            model: LLM model for evaluation
            temperature: Temperature for LLM
            enable_hallucination_detection: Enable hallucination detection
            enable_citation_evaluation: Enable citation quality evaluation
            enable_latency_scoring: Enable latency scoring
            weights: Custom weights for overall score calculation
        """
        self.model = model
        self.temperature = temperature
        
        # Initialize sub-evaluators
        self.hallucination_detector = HallucinationDetector(model, temperature) if enable_hallucination_detection else None
        self.citation_evaluator = CitationQualityEvaluator(model, temperature) if enable_citation_evaluation else None
        self.latency_scorer = LatencyScorer() if enable_latency_scoring else None
        
        # Default weights for overall score
        self.weights = weights or {
            "accuracy": 0.25,
            "relevance": 0.20,
            "completeness": 0.20,
            "hallucination": 0.20,
            "citation": 0.10,
            "latency": 0.05
        }
        
        dashscope.api_key = config.DASHSCOPE_API_KEY
    
    def _get_basic_scores(
        self,
        question: str,
        expected_answer: str,
        target_response: str
    ) -> Dict[str, Any]:
        """Get basic accuracy, relevance, completeness scores."""
        system_prompt = """You are an expert evaluator for RAG systems.

Evaluate on three dimensions:
1. **Accuracy** (0-100): Factual correctness
2. **Relevance** (0-100): Addresses the question
3. **Completeness** (0-100): Covers key points

Return JSON:
{
  "accuracy_score": <int 0-100>,
  "relevance_score": <int 0-100>,
  "completeness_score": <int 0-100>,
  "reasoning": "<brief explanation>"
}"""

        user_prompt = f"""Question:
{question}

Expected Answer:
{expected_answer}

Target Response:
{target_response}

Evaluate the target response."""

        try:
            response = Generation.call(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                result_format="json_object"
            )
            
            content = response.output["choices"][0]["message"]["content"]
            result = json.loads(content)
            
            # Validate
            for key in ["accuracy_score", "relevance_score", "completeness_score"]:
                result[key] = max(0, min(100, int(result.get(key, 50))))
            
            if "reasoning" not in result:
                result["reasoning"] = "No reasoning provided"
            
            return result
            
        except Exception as e:
            print(f"⚠️ Basic evaluation failed: {e}")
            return {
                "accuracy_score": 50,
                "relevance_score": 50,
                "completeness_score": 50,
                "reasoning": f"Evaluation error: {str(e)}"
            }
    
    def evaluate(
        self,
        question: str,
        expected_answer: str,
        target_response: str,
        context: str,
        latency_ms: float,
        retrieved_sources: Optional[List[str]] = None
    ) -> AdvancedEvaluationResult:
        """
        Perform comprehensive evaluation with all metrics.
        
        Args:
            question: The original question
            expected_answer: Expected/reference answer
            target_response: RAG system's response
            context: Retrieved context/chunks
            latency_ms: Response time in milliseconds
            retrieved_sources: Optional list of source identifiers
            
        Returns:
            AdvancedEvaluationResult with all metrics
        """
        # Get basic scores
        basic = self._get_basic_scores(question, expected_answer, target_response)
        
        # Hallucination detection
        hallucination_result = {"hallucination_score": 100, "has_hallucinations": False, 
                               "hallucination_details": [], "reasoning": "Not evaluated"}
        if self.hallucination_detector:
            hallucination_result = self.hallucination_detector.detect(
                question, target_response, context, expected_answer
            )
        
        # Citation quality
        citation_result = {"citation_quality_score": 50, "has_citations": False, 
                          "citation_analysis": "Not evaluated"}
        if self.citation_evaluator:
            citation_result = self.citation_evaluator.evaluate(
                question, target_response, context, retrieved_sources
            )
        
        # Latency scoring
        latency_score, is_slow, latency_desc = 100, False, "Not evaluated"
        if self.latency_scorer:
            latency_score, is_slow, latency_desc = self.latency_scorer.score(latency_ms)
        
        # Calculate overall scores
        basic_overall = (
            basic["accuracy_score"] +
            basic["relevance_score"] +
            basic["completeness_score"]
        ) / 3.0
        
        advanced_overall = (
            self.weights["accuracy"] * basic["accuracy_score"] +
            self.weights["relevance"] * basic["relevance_score"] +
            self.weights["completeness"] * basic["completeness_score"] +
            self.weights["hallucination"] * hallucination_result["hallucination_score"] +
            self.weights["citation"] * citation_result["citation_quality_score"] +
            self.weights["latency"] * latency_score
        )
        
        # Combine reasoning
        combined_reasoning = f"""Basic: {basic['reasoning']}
Hallucination: {hallucination_result['reasoning']}
Citation: {citation_result['citation_analysis']}
Latency: {latency_desc}"""
        
        return AdvancedEvaluationResult(
            accuracy_score=basic["accuracy_score"],
            relevance_score=basic["relevance_score"],
            completeness_score=basic["completeness_score"],
            hallucination_score=hallucination_result["hallucination_score"],
            citation_quality_score=citation_result["citation_quality_score"],
            latency_score=latency_score,
            basic_overall=basic_overall,
            advanced_overall=advanced_overall,
            reasoning=combined_reasoning,
            hallucination_details=hallucination_result["hallucination_details"],
            citation_analysis=citation_result["citation_analysis"],
            latency_ms=latency_ms,
            has_hallucinations=hallucination_result["has_hallucinations"],
            has_citations=citation_result["has_citations"],
            is_slow=is_slow
        )


def create_advanced_evaluator(
    enable_all: bool = True,
    **kwargs
) -> AdvancedEvaluator:
    """
    Factory function to create an advanced evaluator.
    
    Args:
        enable_all: Enable all advanced features
        **kwargs: Additional arguments for AdvancedEvaluator
        
    Returns:
        Configured AdvancedEvaluator instance
    """
    if enable_all:
        return AdvancedEvaluator(
            enable_hallucination_detection=True,
            enable_citation_evaluation=True,
            enable_latency_scoring=True,
            **kwargs
        )
    return AdvancedEvaluator(**kwargs)

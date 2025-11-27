"""
RAG Assessment Module - Part 2 of RAG Evaluation Pipeline

This module handles:
1. Loading generated QA pairs from Part 1
2. Calling target RAG endpoints with questions
3. Collecting responses from the target system
4. Comparing target responses with expected answers using LLM-as-judge
5. Generating comprehensive evaluation metrics and reports
"""

import json
import time
import os
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
import pandas as pd

from . import config


@dataclass
class QAPair:
    """Represents a question-answer pair from the generated dataset."""
    id: str
    question: str
    answer: str
    rationale: str = ""
    support_span: str = ""
    doc_id: str = ""
    chunk_id: str = ""
    source_path: str = ""
    difficulty: str = ""


@dataclass
class AssessmentResult:
    """Represents the result of assessing a single QA pair."""
    qa_id: str
    question: str
    expected_answer: str
    target_response: str
    accuracy_score: int  # 0-100
    relevance_score: int  # 0-100
    completeness_score: int  # 0-100
    overall_score: float  # Average of above
    evaluation_reasoning: str
    response_time_ms: float
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None


class RAGEndpointClient:
    """Client for interacting with RAG endpoints."""
    
    def __init__(
        self,
        endpoint_url: str,
        login_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Tuple[int, int] = (5, 40),
        max_retries: int = 3
    ):
        """
        Initialize RAG endpoint client.
        
        Args:
            endpoint_url: The URL of the RAG query endpoint
            login_url: Optional login URL for authentication
            username: Username for authentication
            password: Password for authentication
            headers: Additional headers to include in requests
            timeout: Request timeout (connect, read) in seconds
            max_retries: Maximum number of retry attempts
        """
        self.endpoint_url = endpoint_url
        self.login_url = login_url
        self.timeout = timeout
        
        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.8,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=frozenset(['GET', 'POST'])
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set headers
        default_headers = {"Accept": "application/json", "Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        self.session.headers.update(default_headers)
        
        # Authenticate if credentials provided
        if login_url and username and password:
            self._authenticate(username, password)
    
    def _authenticate(self, username: str, password: str):
        """Authenticate with the RAG service."""
        try:
            response = self.session.post(
                self.login_url,
                data={"username": username, "password": password},
                timeout=self.timeout
            )
            response.raise_for_status()
            print("✅ Authentication successful")
        except Exception as e:
            print(f"⚠️ Authentication failed: {e}")
            raise
    
    def _is_streaming(self, response: requests.Response) -> bool:
        """Check if response is streaming."""
        ct = response.headers.get("Content-Type", "").lower()
        te = response.headers.get("Transfer-Encoding", "").lower()
        return ("text/event-stream" in ct) or ("chunked" in te)
    
    def _parse_answer(self, res_json: Dict[str, Any]) -> str:
        """Extract answer from various response formats."""
        # Try common field names
        candidates = [
            res_json.get("answer"),
            res_json.get("response"),
            res_json.get("result"),
            res_json.get("msg"),
        ]
        
        # Try nested data object
        if not any(candidates):
            data = res_json.get("data") or {}
            if isinstance(data, dict):
                candidates += [
                    data.get("answer"),
                    data.get("response"),
                    data.get("result"),
                ]
        
        # Try OpenAI-style choices format
        if not any(candidates):
            choices = res_json.get("choices")
            if isinstance(choices, list) and choices:
                msg = choices[0].get("message") or {}
                candidates.append(msg.get("content"))
            elif "output_text" in res_json:
                candidates.append(res_json.get("output_text"))
        
        answer = next((c for c in candidates if isinstance(c, str) and c.strip()), None)
        return answer or ""
    
    def query(self, question: str, query_params: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, Any], float]:
        """
        Send a question to the RAG endpoint and return the response.
        
        Args:
            question: The question to ask
            query_params: Additional parameters for the query
            
        Returns:
            Tuple of (answer_text, raw_response_dict, response_time_ms)
        """
        payload = {"query": question}
        if query_params:
            payload.update(query_params)
        
        start_time = time.time()
        
        try:
            response = self.session.post(
                self.endpoint_url,
                json=payload,
                timeout=self.timeout,
                stream=True
            )
            response.raise_for_status()
            
            # Handle streaming vs non-streaming responses
            if self._is_streaming(response):
                chunks = []
                for chunk in response.iter_content(chunk_size=4096, decode_unicode=True):
                    if chunk:
                        chunks.append(chunk)
                body = "".join(chunks)
            else:
                body = response.text
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if not body or not body.strip():
                return "", {"error": "Empty response body"}, response_time_ms
            
            try:
                res_json = json.loads(body)
            except json.JSONDecodeError as je:
                return "", {"error": f"JSON parse error: {je}", "body_preview": body[:500]}, response_time_ms
            
            answer = self._parse_answer(res_json)
            return answer, res_json, response_time_ms
            
        except requests.exceptions.Timeout:
            response_time_ms = (time.time() - start_time) * 1000
            return "", {"error": "Request timeout"}, response_time_ms
        except requests.exceptions.RequestException as e:
            response_time_ms = (time.time() - start_time) * 1000
            return "", {"error": f"HTTP error: {str(e)}"}, response_time_ms
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return "", {"error": f"Unexpected error: {str(e)}"}, response_time_ms


class LLMEvaluator:
    """LLM-based evaluator for comparing target responses with expected answers."""
    
    def __init__(self, model: str = "qwen-turbo", temperature: float = 0.0):
        """
        Initialize LLM evaluator.
        
        Args:
            model: The LLM model to use for evaluation
            temperature: Temperature for LLM generation (0 for deterministic)
        """
        self.model = model
        self.temperature = temperature
        
        # Import here to avoid dependency issues if not using DashScope
        try:
            import dashscope
            from dashscope import Generation
            self.dashscope = dashscope
            self.Generation = Generation
            self.dashscope.api_key = config.DASHSCOPE_API_KEY
        except ImportError:
            print("⚠️ DashScope not available. Install with: pip install dashscope")
            raise
    
    def evaluate(
        self,
        question: str,
        expected_answer: str,
        target_response: str
    ) -> Dict[str, Any]:
        """
        Evaluate target response against expected answer using LLM.
        
        Returns dict with:
        - accuracy_score: 0-100 (factual correctness)
        - relevance_score: 0-100 (relevance to question)
        - completeness_score: 0-100 (completeness of answer)
        - reasoning: Explanation of scores
        """
        if not target_response or not target_response.strip():
            return {
                "accuracy_score": 0,
                "relevance_score": 0,
                "completeness_score": 0,
                "reasoning": "Target response is empty"
            }
        
        if not expected_answer or not expected_answer.strip():
            return {
                "accuracy_score": 50,
                "relevance_score": 50,
                "completeness_score": 50,
                "reasoning": "No expected answer provided for comparison"
            }
        
        system_prompt = """You are an expert evaluator for RAG (Retrieval-Augmented Generation) systems.
Your task is to evaluate the quality of a target system's response by comparing it with an expected answer.

Evaluate on three dimensions:
1. **Accuracy** (0-100): Factual correctness and semantic equivalence with expected answer
2. **Relevance** (0-100): How well the response addresses the question
3. **Completeness** (0-100): Whether all key points from expected answer are covered

Return a JSON object with this exact structure:
{
  "accuracy_score": <int 0-100>,
  "relevance_score": <int 0-100>,
  "completeness_score": <int 0-100>,
  "reasoning": "<brief explanation of scores>"
}"""

        user_prompt = f"""Question:
{question}

Expected Answer:
{expected_answer}

Target System Response:
{target_response}

Evaluate the target response and return scores as JSON."""

        try:
            response = self.Generation.call(
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
            
            # Validate and clamp scores
            for key in ["accuracy_score", "relevance_score", "completeness_score"]:
                if key not in result:
                    result[key] = 50
                result[key] = max(0, min(100, int(result[key])))
            
            if "reasoning" not in result:
                result["reasoning"] = "No reasoning provided"
            
            return result
            
        except Exception as e:
            print(f"⚠️ Evaluation failed: {e}")
            return {
                "accuracy_score": 50,
                "relevance_score": 50,
                "completeness_score": 50,
                "reasoning": f"Evaluation error: {str(e)}"
            }


class RAGAssessment:
    """Main class for running RAG assessment pipeline."""
    
    def __init__(
        self,
        endpoint_client: RAGEndpointClient,
        evaluator: LLMEvaluator,
        qa_file_path: Optional[Path] = None,
        rate_limit_delay: float = 0.05
    ):
        """
        Initialize RAG assessment.
        
        Args:
            endpoint_client: Client for querying RAG endpoint
            evaluator: LLM evaluator for scoring responses
            qa_file_path: Path to generated QA pairs file (defaults to config)
            rate_limit_delay: Delay between requests in seconds
        """
        self.client = endpoint_client
        self.evaluator = evaluator
        self.qa_file_path = qa_file_path or config.GENERATED_QAS_PATH
        self.rate_limit_delay = rate_limit_delay
    
    def load_qa_pairs(self) -> List[QAPair]:
        """Load QA pairs from JSONL file."""
        if not self.qa_file_path.exists():
            raise FileNotFoundError(f"QA file not found: {self.qa_file_path}")
        
        qa_pairs = []
        with open(self.qa_file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    qa_pairs.append(QAPair(**data))
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"⚠️ Skipping invalid QA pair: {e}")
                    continue
        
        print(f"✅ Loaded {len(qa_pairs)} QA pairs from {self.qa_file_path}")
        return qa_pairs
    
    def assess_single(self, qa: QAPair) -> AssessmentResult:
        """Assess a single QA pair."""
        # Query target endpoint
        target_response, raw_response, response_time = self.client.query(qa.question)
        
        # Check for errors
        error = raw_response.get("error") if isinstance(raw_response, dict) else None
        
        # Evaluate response
        if error or not target_response:
            eval_result = {
                "accuracy_score": 0,
                "relevance_score": 0,
                "completeness_score": 0,
                "reasoning": error or "Empty response"
            }
        else:
            eval_result = self.evaluator.evaluate(
                question=qa.question,
                expected_answer=qa.answer,
                target_response=target_response
            )
        
        # Calculate overall score
        overall_score = (
            eval_result["accuracy_score"] +
            eval_result["relevance_score"] +
            eval_result["completeness_score"]
        ) / 3.0
        
        return AssessmentResult(
            qa_id=qa.id,
            question=qa.question,
            expected_answer=qa.answer,
            target_response=target_response,
            accuracy_score=eval_result["accuracy_score"],
            relevance_score=eval_result["relevance_score"],
            completeness_score=eval_result["completeness_score"],
            overall_score=overall_score,
            evaluation_reasoning=eval_result["reasoning"],
            response_time_ms=response_time,
            error=error,
            raw_response=raw_response
        )
    
    def run_assessment(self, max_samples: Optional[int] = None) -> List[AssessmentResult]:
        """
        Run full assessment on all QA pairs.
        
        Args:
            max_samples: Optional limit on number of samples to assess
            
        Returns:
            List of assessment results
        """
        qa_pairs = self.load_qa_pairs()
        
        if max_samples:
            qa_pairs = qa_pairs[:max_samples]
            print(f"ℹ️ Limiting assessment to {max_samples} samples")
        
        results = []
        print(f"\n--- Starting RAG Assessment on {len(qa_pairs)} QA pairs ---")
        
        for qa in tqdm(qa_pairs, desc="Assessing QA pairs"):
            result = self.assess_single(qa)
            results.append(result)
            time.sleep(self.rate_limit_delay)
        
        return results
    
    def generate_report(
        self,
        results: List[AssessmentResult],
        output_path: Optional[Path] = None
    ) -> pd.DataFrame:
        """
        Generate comprehensive assessment report.
        
        Args:
            results: List of assessment results
            output_path: Optional path to save Excel report
            
        Returns:
            DataFrame with detailed results
        """
        if not results:
            print("⚠️ No results to report")
            return pd.DataFrame()
        
        # Convert results to DataFrame
        df = pd.DataFrame([asdict(r) for r in results])
        
        # Calculate summary statistics
        total_questions = len(df)
        answered_questions = df['target_response'].astype(str).str.strip().astype(bool).sum()
        avg_accuracy = df['accuracy_score'].mean()
        avg_relevance = df['relevance_score'].mean()
        avg_completeness = df['completeness_score'].mean()
        avg_overall = df['overall_score'].mean()
        avg_response_time = df['response_time_ms'].mean()
        
        # Score distribution
        excellent = (df['overall_score'] >= 80).sum()
        good = ((df['overall_score'] >= 60) & (df['overall_score'] < 80)).sum()
        poor = (df['overall_score'] < 60).sum()
        
        # Create summary
        summary_data = {
            'Metric': [
                'Total Questions',
                'Answered Questions',
                'Answer Rate (%)',
                'Avg Accuracy Score',
                'Avg Relevance Score',
                'Avg Completeness Score',
                'Avg Overall Score',
                'Avg Response Time (ms)',
                'Excellent (≥80)',
                'Good (60-79)',
                'Poor (<60)'
            ],
            'Value': [
                total_questions,
                answered_questions,
                f"{(answered_questions/total_questions*100):.2f}",
                f"{avg_accuracy:.2f}",
                f"{avg_relevance:.2f}",
                f"{avg_completeness:.2f}",
                f"{avg_overall:.2f}",
                f"{avg_response_time:.2f}",
                excellent,
                good,
                poor
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Filter poor performers
        poor_performers = df[df['overall_score'] < 60].copy()
        
        # Save to Excel if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                # Summary sheet
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Detailed results
                df_display = df.drop(columns=['raw_response'], errors='ignore')
                df_display.to_excel(writer, sheet_name='Detailed Results', index=False)
                
                # Poor performers
                if not poor_performers.empty:
                    poor_display = poor_performers[['question', 'expected_answer', 'target_response', 
                                                     'accuracy_score', 'relevance_score', 'completeness_score',
                                                     'overall_score', 'evaluation_reasoning']]
                    poor_display.to_excel(writer, sheet_name='Poor Performers', index=False)
                else:
                    pd.DataFrame({'Message': ['No poor performers (all scores ≥ 60)']}).to_excel(
                        writer, sheet_name='Poor Performers', index=False
                    )
            
            print(f"✅ Assessment report saved to {output_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("RAG ASSESSMENT SUMMARY")
        print("="*60)
        for _, row in summary_df.iterrows():
            print(f"{row['Metric']:.<40} {row['Value']}")
        print("="*60)
        
        return df

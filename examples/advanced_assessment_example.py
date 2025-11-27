"""
Example: Advanced RAG Assessment with Hallucination Detection, 
Citation Quality, and Latency Scoring

This demonstrates how to use the advanced evaluator for comprehensive
RAG system evaluation.
"""

from pathlib import Path
import pandas as pd
from ragscore.assessment import RAGEndpointClient, RAGAssessment
from ragscore.advanced_evaluator import (
    AdvancedEvaluator,
    HallucinationDetector,
    CitationQualityEvaluator,
    LatencyScorer
)


def example_1_basic_advanced_evaluation():
    """Example 1: Using the advanced evaluator directly."""
    print("=" * 70)
    print("Example 1: Advanced Evaluation with All Metrics")
    print("=" * 70)
    
    # Initialize advanced evaluator
    evaluator = AdvancedEvaluator(
        model="qwen-turbo",
        temperature=0.0,
        enable_hallucination_detection=True,
        enable_citation_evaluation=True,
        enable_latency_scoring=True
    )
    
    # Example data
    question = "What is the capital of France?"
    expected_answer = "The capital of France is Paris, located in the north-central part of the country."
    target_response = "The capital of France is Paris. It is home to the Eiffel Tower and has a population of over 2 million people in the city proper."
    context = "France is a country in Western Europe. Its capital and largest city is Paris, which is located in the north-central part of the country. Paris is known for landmarks like the Eiffel Tower."
    latency_ms = 1234.5
    
    # Evaluate
    result = evaluator.evaluate(
        question=question,
        expected_answer=expected_answer,
        target_response=target_response,
        context=context,
        latency_ms=latency_ms
    )
    
    # Display results
    print(f"\n📊 Evaluation Results:")
    print(f"   Accuracy:       {result.accuracy_score}/100")
    print(f"   Relevance:      {result.relevance_score}/100")
    print(f"   Completeness:   {result.completeness_score}/100")
    print(f"   Hallucination:  {result.hallucination_score}/100 {'⚠️' if result.has_hallucinations else '✅'}")
    print(f"   Citation:       {result.citation_quality_score}/100 {'✅' if result.has_citations else '❌'}")
    print(f"   Latency:        {result.latency_score}/100 {'⚠️' if result.is_slow else '✅'}")
    print(f"\n   Basic Overall:    {result.basic_overall:.2f}/100")
    print(f"   Advanced Overall: {result.advanced_overall:.2f}/100")
    
    if result.has_hallucinations:
        print(f"\n⚠️  Detected Hallucinations:")
        for h in result.hallucination_details:
            print(f"   • {h}")
    
    print(f"\n📝 Reasoning:\n{result.reasoning}")
    print("\n" + "=" * 70)


def example_2_individual_detectors():
    """Example 2: Using individual detectors separately."""
    print("\n" + "=" * 70)
    print("Example 2: Individual Detector Usage")
    print("=" * 70)
    
    # Test data with potential hallucination
    question = "When was the company founded?"
    response = "The company was founded in 1995 by John Smith in California. It started with 50 employees."
    context = "The company was established in the late 1990s in California."
    
    # 1. Hallucination Detection
    print("\n🔍 Hallucination Detection:")
    detector = HallucinationDetector()
    halluc_result = detector.detect(question, response, context)
    
    print(f"   Score: {halluc_result['hallucination_score']}/100")
    print(f"   Has Hallucinations: {halluc_result['has_hallucinations']}")
    if halluc_result['hallucination_details']:
        print(f"   Details:")
        for detail in halluc_result['hallucination_details']:
            print(f"   • {detail}")
    print(f"   Reasoning: {halluc_result['reasoning']}")
    
    # 2. Citation Quality
    print("\n📚 Citation Quality Evaluation:")
    response_with_citation = "According to the document, the company was founded in 1995 [1]. It was started by John Smith in California [1]."
    citation_eval = CitationQualityEvaluator()
    citation_result = citation_eval.evaluate(question, response_with_citation, context)
    
    print(f"   Score: {citation_result['citation_quality_score']}/100")
    print(f"   Has Citations: {citation_result['has_citations']}")
    print(f"   Analysis: {citation_result['citation_analysis']}")
    
    # 3. Latency Scoring
    print("\n⚡ Latency Scoring:")
    latency_scorer = LatencyScorer(
        excellent_threshold_ms=500,
        good_threshold_ms=2000,
        acceptable_threshold_ms=5000
    )
    
    test_latencies = [300, 1000, 3000, 7000]
    for latency in test_latencies:
        score, is_slow, desc = latency_scorer.score(latency)
        print(f"   {latency}ms → Score: {score}/100 - {desc}")
    
    print("\n" + "=" * 70)


def example_3_custom_weights():
    """Example 3: Custom weight configuration for different priorities."""
    print("\n" + "=" * 70)
    print("Example 3: Custom Weight Configuration")
    print("=" * 70)
    
    # Scenario 1: Prioritize accuracy and hallucination detection (e.g., medical/legal)
    print("\n📋 Scenario 1: High-stakes domain (medical/legal)")
    print("   Priority: Accuracy and No Hallucinations")
    
    evaluator_highstakes = AdvancedEvaluator(
        weights={
            "accuracy": 0.35,      # High weight
            "relevance": 0.10,
            "completeness": 0.15,
            "hallucination": 0.35,  # High weight
            "citation": 0.05,
            "latency": 0.00        # Don't care about speed
        }
    )
    print("   Weights:", evaluator_highstakes.weights)
    
    # Scenario 2: Prioritize speed and relevance (e.g., chatbot)
    print("\n💬 Scenario 2: Conversational chatbot")
    print("   Priority: Speed and Relevance")
    
    evaluator_chatbot = AdvancedEvaluator(
        weights={
            "accuracy": 0.20,
            "relevance": 0.35,      # High weight
            "completeness": 0.10,
            "hallucination": 0.15,
            "citation": 0.00,       # Don't need citations
            "latency": 0.20         # High weight on speed
        }
    )
    print("   Weights:", evaluator_chatbot.weights)
    
    # Scenario 3: Research/academic (need citations)
    print("\n🎓 Scenario 3: Research/Academic")
    print("   Priority: Citations and Completeness")
    
    evaluator_research = AdvancedEvaluator(
        weights={
            "accuracy": 0.25,
            "relevance": 0.15,
            "completeness": 0.30,   # High weight
            "hallucination": 0.15,
            "citation": 0.15,       # High weight
            "latency": 0.00         # Don't care about speed
        }
    )
    print("   Weights:", evaluator_research.weights)
    
    print("\n" + "=" * 70)


def example_4_full_assessment_with_advanced_metrics():
    """Example 4: Full assessment pipeline with advanced metrics."""
    print("\n" + "=" * 70)
    print("Example 4: Full Assessment with Advanced Metrics")
    print("=" * 70)
    
    # Note: This is a conceptual example showing how to integrate
    # You would need to modify the RAGAssessment class to use AdvancedEvaluator
    
    print("""
To use advanced metrics in the full assessment pipeline:

1. Modify RAGAssessment to accept AdvancedEvaluator:
   
   from ragscore.advanced_evaluator import AdvancedEvaluator
   
   assessment = RAGAssessment(
       endpoint_client=client,
       evaluator=AdvancedEvaluator(enable_all=True),
       qa_file_path=Path("output/generated_qas.jsonl")
   )

2. Update assess_single() to pass context and use advanced results:
   
   # In assess_single method:
   result = self.evaluator.evaluate(
       question=qa.question,
       expected_answer=qa.answer,
       target_response=target_response,
       context=retrieved_context,  # Need to capture this
       latency_ms=response_time
   )

3. Update AssessmentResult dataclass to include advanced metrics:
   
   @dataclass
   class AssessmentResult:
       # ... existing fields ...
       hallucination_score: int
       citation_quality_score: int
       latency_score: int
       has_hallucinations: bool
       has_citations: bool
       hallucination_details: List[str]

4. Update report generation to include new columns:
   
   df = pd.DataFrame([asdict(r) for r in results])
   # Now includes hallucination_score, citation_quality_score, etc.
    """)
    
    print("=" * 70)


def example_5_analyzing_results():
    """Example 5: Analyzing results to find specific issues."""
    print("\n" + "=" * 70)
    print("Example 5: Analyzing Advanced Metrics")
    print("=" * 70)
    
    # Simulate some results
    print("""
After running assessment with advanced metrics, you can analyze:

# Load results
df = pd.read_excel("output/advanced_assessment_report.xlsx")

# 1. Find responses with hallucinations
hallucinated = df[df['has_hallucinations'] == True]
print(f"Found {len(hallucinated)} responses with hallucinations")

# 2. Find slow responses with good accuracy
slow_but_accurate = df[
    (df['latency_score'] < 60) & 
    (df['accuracy_score'] >= 80)
]
print(f"Found {len(slow_but_accurate)} accurate but slow responses")
# → Optimization opportunity: These are correct but need speed improvement

# 3. Find responses without citations
no_citations = df[df['has_citations'] == False]
print(f"Found {len(no_citations)} responses without citations")
# → May need to improve citation generation

# 4. Find high-risk responses (hallucinations + no citations)
high_risk = df[
    (df['has_hallucinations'] == True) & 
    (df['has_citations'] == False)
]
print(f"Found {len(high_risk)} high-risk responses")
# → Critical: Making unsupported claims without attribution

# 5. Correlation analysis
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.scatter(df['hallucination_score'], df['citation_quality_score'])
plt.xlabel('Hallucination Score (higher = better)')
plt.ylabel('Citation Quality Score')
plt.title('Hallucination vs Citation Quality')
plt.savefig('hallucination_vs_citation.png')

# 6. Performance vs Quality tradeoff
plt.figure(figsize=(10, 6))
plt.scatter(df['latency_score'], df['accuracy_score'], 
           c=df['advanced_overall'], cmap='viridis')
plt.xlabel('Latency Score (higher = faster)')
plt.ylabel('Accuracy Score')
plt.colorbar(label='Overall Score')
plt.title('Speed vs Accuracy Tradeoff')
plt.savefig('speed_vs_accuracy.png')

# 7. Generate insights report
insights = {
    'total_questions': len(df),
    'hallucination_rate': (df['has_hallucinations'].sum() / len(df) * 100),
    'citation_rate': (df['has_citations'].sum() / len(df) * 100),
    'avg_latency_ms': df['latency_ms'].mean(),
    'slow_response_rate': (df['is_slow'].sum() / len(df) * 100),
}

print("\\nKey Insights:")
for key, value in insights.items():
    print(f"  {key}: {value:.2f}")
    """)
    
    print("\n" + "=" * 70)


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("ADVANCED RAG ASSESSMENT EXAMPLES")
    print("=" * 70)
    
    try:
        # Run examples
        example_1_basic_advanced_evaluation()
        example_2_individual_detectors()
        example_3_custom_weights()
        example_4_full_assessment_with_advanced_metrics()
        example_5_analyzing_results()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70)
        print("\nNext Steps:")
        print("1. Review the advanced_evaluator.py module")
        print("2. Integrate AdvancedEvaluator into your assessment pipeline")
        print("3. Customize weights based on your use case")
        print("4. Analyze results to identify specific improvement areas")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

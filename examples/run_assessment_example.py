"""
Example: Running RAG Assessment

This script demonstrates how to use the RAG Assessment module
to evaluate your RAG system's performance.
"""

from pathlib import Path
from ragscore.assessment import RAGEndpointClient, LLMEvaluator, RAGAssessment

def main():
    """Run a complete RAG assessment."""
    
    # ========================================
    # 1. Configure Your RAG Endpoint
    # ========================================
    print("=" * 60)
    print("RAG Assessment Example")
    print("=" * 60)
    
    # Option A: Simple endpoint (no authentication)
    endpoint_url = "http://localhost:5000/query"
    
    # Option B: With authentication (uncomment if needed)
    # endpoint_url = "http://47.99.205.203:5004/api/query"
    # login_url = "http://47.99.205.203:5004/login"
    # username = "demo"
    # password = "demo123"
    
    # ========================================
    # 2. Initialize Endpoint Client
    # ========================================
    print("\n📡 Initializing endpoint client...")
    
    client = RAGEndpointClient(
        endpoint_url=endpoint_url,
        # Uncomment for authentication:
        # login_url=login_url,
        # username=username,
        # password=password,
        timeout=(5, 40),  # (connect_timeout, read_timeout)
        max_retries=3
    )
    
    # ========================================
    # 3. Initialize LLM Evaluator
    # ========================================
    print("🤖 Initializing LLM evaluator...")
    
    evaluator = LLMEvaluator(
        model="qwen-turbo",  # Or "qwen-plus" for better quality
        temperature=0.0  # Deterministic evaluation
    )
    
    # ========================================
    # 4. Create Assessment Instance
    # ========================================
    print("⚙️  Setting up assessment...")
    
    assessment = RAGAssessment(
        endpoint_client=client,
        evaluator=evaluator,
        qa_file_path=Path("output/generated_qas.jsonl"),  # From Part 1
        rate_limit_delay=0.05  # 50ms between requests
    )
    
    # ========================================
    # 5. Run Assessment
    # ========================================
    print("\n🚀 Starting assessment...\n")
    
    # For testing, limit to first 10 samples
    # Remove max_samples parameter to assess all QA pairs
    results = assessment.run_assessment(max_samples=10)
    
    # ========================================
    # 6. Generate Report
    # ========================================
    print("\n📊 Generating report...")
    
    output_path = Path("output/assessment_report.xlsx")
    df = assessment.generate_report(results, output_path=output_path)
    
    # ========================================
    # 7. Display Key Insights
    # ========================================
    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)
    
    if not df.empty:
        # Overall performance
        avg_overall = df['overall_score'].mean()
        avg_accuracy = df['accuracy_score'].mean()
        avg_relevance = df['relevance_score'].mean()
        avg_completeness = df['completeness_score'].mean()
        
        print(f"\n📈 Average Scores:")
        print(f"   Overall:      {avg_overall:.2f}/100")
        print(f"   Accuracy:     {avg_accuracy:.2f}/100")
        print(f"   Relevance:    {avg_relevance:.2f}/100")
        print(f"   Completeness: {avg_completeness:.2f}/100")
        
        # Score distribution
        excellent = (df['overall_score'] >= 80).sum()
        good = ((df['overall_score'] >= 60) & (df['overall_score'] < 80)).sum()
        poor = (df['overall_score'] < 60).sum()
        
        print(f"\n📊 Score Distribution:")
        print(f"   Excellent (≥80): {excellent}")
        print(f"   Good (60-79):    {good}")
        print(f"   Poor (<60):      {poor}")
        
        # Performance metrics
        avg_response_time = df['response_time_ms'].mean()
        errors = df['error'].notna().sum()
        
        print(f"\n⚡ Performance:")
        print(f"   Avg Response Time: {avg_response_time:.2f}ms")
        print(f"   Errors:            {errors}")
        
        # Top 3 best and worst
        print(f"\n✅ Top 3 Best Performing Questions:")
        top_3 = df.nlargest(3, 'overall_score')[['question', 'overall_score']]
        for idx, row in top_3.iterrows():
            print(f"   • {row['question'][:60]}... (Score: {row['overall_score']:.1f})")
        
        print(f"\n⚠️  Top 3 Worst Performing Questions:")
        bottom_3 = df.nsmallest(3, 'overall_score')[['question', 'overall_score']]
        for idx, row in bottom_3.iterrows():
            print(f"   • {row['question'][:60]}... (Score: {row['overall_score']:.1f})")
    
    print("\n" + "=" * 60)
    print(f"✅ Assessment complete! Report saved to: {output_path}")
    print("=" * 60)
    
    # ========================================
    # 8. Optional: Programmatic Analysis
    # ========================================
    
    # Example: Find questions where accuracy is low but relevance is high
    # (indicates the system is on-topic but providing incorrect information)
    if not df.empty:
        problematic = df[
            (df['accuracy_score'] < 60) & 
            (df['relevance_score'] >= 70)
        ]
        
        if not problematic.empty:
            print(f"\n⚠️  Found {len(problematic)} questions with low accuracy but high relevance")
            print("   (System is on-topic but providing incorrect information)")
            print("\n   These require immediate attention:")
            for idx, row in problematic.head(3).iterrows():
                print(f"   • {row['question'][:60]}...")
                print(f"     Accuracy: {row['accuracy_score']}, Relevance: {row['relevance_score']}")
    
    return df


if __name__ == "__main__":
    try:
        df = main()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you've run Part 1 (QA generation) first:")
        print("  python -m ragscore.cli generate")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

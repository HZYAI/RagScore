"""
Command-line interface for RAG Assessment
"""

import argparse
import sys
from pathlib import Path

from .assessment import RAGEndpointClient, LLMEvaluator, RAGAssessment
from . import config


def main():
    """Main CLI entry point for RAG assessment."""
    parser = argparse.ArgumentParser(
        description="RAG Assessment Tool - Evaluate RAG system performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic assessment with default settings
  python -m ragscore.assessment_cli --endpoint http://localhost:5000/query
  
  # With authentication
  python -m ragscore.assessment_cli \\
    --endpoint http://api.example.com/query \\
    --login-url http://api.example.com/login \\
    --username demo \\
    --password demo123
  
  # Limit to first 50 samples and custom output
  python -m ragscore.assessment_cli \\
    --endpoint http://localhost:5000/query \\
    --max-samples 50 \\
    --output results/assessment_report.xlsx
  
  # Use custom QA file
  python -m ragscore.assessment_cli \\
    --endpoint http://localhost:5000/query \\
    --qa-file custom_qas.jsonl
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--endpoint",
        required=True,
        help="RAG query endpoint URL (e.g., http://localhost:5000/query)"
    )
    
    # Authentication arguments
    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument(
        "--login-url",
        help="Login endpoint URL for authentication"
    )
    auth_group.add_argument(
        "--username",
        help="Username for authentication"
    )
    auth_group.add_argument(
        "--password",
        help="Password for authentication"
    )
    
    # Input/Output arguments
    io_group = parser.add_argument_group("Input/Output")
    io_group.add_argument(
        "--qa-file",
        type=Path,
        help=f"Path to QA pairs JSONL file (default: {config.GENERATED_QAS_PATH})"
    )
    io_group.add_argument(
        "--output",
        type=Path,
        default=config.OUTPUT_DIR / "assessment_report.xlsx",
        help="Output path for assessment report (default: output/assessment_report.xlsx)"
    )
    
    # Assessment parameters
    assess_group = parser.add_argument_group("Assessment Parameters")
    assess_group.add_argument(
        "--max-samples",
        type=int,
        help="Maximum number of QA pairs to assess (default: all)"
    )
    assess_group.add_argument(
        "--rate-limit",
        type=float,
        default=0.05,
        help="Delay between requests in seconds (default: 0.05)"
    )
    assess_group.add_argument(
        "--timeout",
        type=int,
        default=40,
        help="Request timeout in seconds (default: 40)"
    )
    assess_group.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retry attempts (default: 3)"
    )
    
    # Evaluator parameters
    eval_group = parser.add_argument_group("Evaluator Parameters")
    eval_group.add_argument(
        "--eval-model",
        default="qwen-turbo",
        help="LLM model for evaluation (default: qwen-turbo)"
    )
    eval_group.add_argument(
        "--eval-temperature",
        type=float,
        default=0.0,
        help="Temperature for evaluation LLM (default: 0.0)"
    )
    
    # Additional options
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip generating Excel report (only print summary)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate authentication arguments
    auth_args = [args.login_url, args.username, args.password]
    if any(auth_args) and not all(auth_args):
        parser.error("--login-url, --username, and --password must all be provided together")
    
    try:
        # Initialize endpoint client
        print(f"🔗 Connecting to endpoint: {args.endpoint}")
        client = RAGEndpointClient(
            endpoint_url=args.endpoint,
            login_url=args.login_url,
            username=args.username,
            password=args.password,
            timeout=(5, args.timeout),
            max_retries=args.max_retries
        )
        
        # Initialize evaluator
        print(f"🤖 Initializing evaluator with model: {args.eval_model}")
        evaluator = LLMEvaluator(
            model=args.eval_model,
            temperature=args.eval_temperature
        )
        
        # Initialize assessment
        assessment = RAGAssessment(
            endpoint_client=client,
            evaluator=evaluator,
            qa_file_path=args.qa_file,
            rate_limit_delay=args.rate_limit
        )
        
        # Run assessment
        results = assessment.run_assessment(max_samples=args.max_samples)
        
        if not results:
            print("❌ No results generated")
            sys.exit(1)
        
        # Generate report
        output_path = None if args.no_report else args.output
        df = assessment.generate_report(results, output_path=output_path)
        
        print("\n✅ Assessment completed successfully!")
        
        if args.verbose and not df.empty:
            print("\nFirst 5 results:")
            print(df[['question', 'overall_score', 'accuracy_score', 
                     'relevance_score', 'completeness_score']].head())
        
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during assessment: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

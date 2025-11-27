# RAG Assessment Guide

## Overview

The RAG Assessment module is the **second part** of the RAGScore evaluation pipeline. After generating QA pairs in Part 1, this module:

1. **Queries your target RAG endpoint** with the generated questions
2. **Collects responses** from your RAG system
3. **Evaluates responses** using LLM-as-judge methodology
4. **Generates comprehensive reports** with multiple quality metrics

## Architecture

```
┌─────────────────────┐
│  Generated QA Pairs │  (from Part 1)
│  (output/*.jsonl)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  RAGEndpointClient  │  Queries target RAG system
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Target Response   │  Collected answers
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   LLM Evaluator     │  Multi-dimensional scoring
│  (LLM-as-Judge)     │  - Accuracy (0-100)
│                     │  - Relevance (0-100)
│                     │  - Completeness (0-100)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Assessment Report  │  Excel with multiple sheets
│  (.xlsx)            │  - Summary
│                     │  - Detailed Results
│                     │  - Poor Performers
└─────────────────────┘
```

## Key Features

### 1. Robust Endpoint Client
- **Retry logic** with exponential backoff
- **Streaming support** for SSE responses
- **Authentication** (login-based or token-based)
- **Flexible response parsing** (handles various API formats)
- **Connection pooling** for better performance

### 2. Multi-Dimensional Evaluation
Unlike simple accuracy scoring, we evaluate on **three dimensions**:

- **Accuracy Score (0-100)**: Factual correctness and semantic equivalence
- **Relevance Score (0-100)**: How well the response addresses the question
- **Completeness Score (0-100)**: Coverage of key points from expected answer

### 3. Comprehensive Reporting
Generated Excel report includes:
- **Summary Sheet**: Overall metrics and score distribution
- **Detailed Results**: All QA pairs with scores and reasoning
- **Poor Performers**: Questions scoring < 60 for focused improvement

## Quick Start

### Basic Usage

```bash
# Run assessment on your RAG endpoint
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query
```

### With Authentication

```bash
python -m ragscore.assessment_cli \
  --endpoint http://47.99.205.203:5004/api/query \
  --login-url http://47.99.205.203:5004/login \
  --username demo \
  --password demo123
```

### Limit Sample Size (for testing)

```bash
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --max-samples 50 \
  --output results/test_assessment.xlsx
```

## Programmatic Usage

For integration into your own scripts:

```python
from pathlib import Path
from ragscore.assessment import RAGEndpointClient, LLMEvaluator, RAGAssessment

# 1. Initialize endpoint client
client = RAGEndpointClient(
    endpoint_url="http://localhost:5000/query",
    login_url="http://localhost:5000/login",  # Optional
    username="demo",  # Optional
    password="demo123",  # Optional
    timeout=(5, 40),
    max_retries=3
)

# 2. Initialize LLM evaluator
evaluator = LLMEvaluator(
    model="qwen-turbo",
    temperature=0.0  # Deterministic evaluation
)

# 3. Create assessment instance
assessment = RAGAssessment(
    endpoint_client=client,
    evaluator=evaluator,
    qa_file_path=Path("output/generated_qas.jsonl"),
    rate_limit_delay=0.05
)

# 4. Run assessment
results = assessment.run_assessment(max_samples=100)

# 5. Generate report
df = assessment.generate_report(
    results,
    output_path=Path("output/assessment_report.xlsx")
)

# 6. Access results programmatically
print(f"Average overall score: {df['overall_score'].mean():.2f}")
print(f"Questions with score < 60: {(df['overall_score'] < 60).sum()}")
```

## Evaluation Methodology

### LLM-as-Judge Approach

We use a powerful LLM (default: `qwen-turbo`) to evaluate responses. The evaluator:

1. **Receives three inputs**:
   - The original question
   - Expected answer (from Part 1 generation)
   - Target system's response

2. **Scores on three dimensions** (0-100 each):
   - **Accuracy**: Is the information factually correct?
   - **Relevance**: Does it answer the question asked?
   - **Completeness**: Are all key points covered?

3. **Provides reasoning**: Explains why scores were assigned

4. **Returns structured JSON**:
   ```json
   {
     "accuracy_score": 85,
     "relevance_score": 90,
     "completeness_score": 80,
     "reasoning": "Response is factually correct and relevant..."
   }
   ```

### Why Multi-Dimensional Scoring?

Single accuracy scores can be misleading. Consider:

- **High accuracy, low relevance**: Correct but off-topic answer
- **High relevance, low completeness**: On-topic but missing key details
- **High completeness, low accuracy**: Comprehensive but contains errors

Our approach provides **granular insights** for targeted improvements.

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Required
DASHSCOPE_API_KEY=your_dashscope_key

# Optional (for default endpoint)
RAG_ENDPOINT_URL=http://localhost:5000/query
RAG_LOGIN_URL=http://localhost:5000/login
RAG_USERNAME=demo
RAG_PASSWORD=demo123
```

### CLI Options

```
Required:
  --endpoint URL              RAG query endpoint URL

Authentication:
  --login-url URL            Login endpoint for authentication
  --username USERNAME        Username for authentication
  --password PASSWORD        Password for authentication

Input/Output:
  --qa-file PATH             Path to QA pairs JSONL file
  --output PATH              Output path for assessment report

Assessment Parameters:
  --max-samples N            Maximum number of QA pairs to assess
  --rate-limit SECONDS       Delay between requests (default: 0.05)
  --timeout SECONDS          Request timeout (default: 40)
  --max-retries N            Maximum retry attempts (default: 3)

Evaluator Parameters:
  --eval-model MODEL         LLM model for evaluation (default: qwen-turbo)
  --eval-temperature TEMP    Temperature for evaluation (default: 0.0)

Options:
  --no-report                Skip generating Excel report
  --verbose                  Enable verbose output
```

## Understanding the Report

### Summary Sheet

| Metric | Value |
|--------|-------|
| Total Questions | 250 |
| Answered Questions | 248 |
| Answer Rate (%) | 99.20 |
| Avg Accuracy Score | 78.45 |
| Avg Relevance Score | 82.30 |
| Avg Completeness Score | 75.60 |
| Avg Overall Score | 78.78 |
| Avg Response Time (ms) | 1234.56 |
| Excellent (≥80) | 120 |
| Good (60-79) | 95 |
| Poor (<60) | 33 |

### Detailed Results Sheet

Contains all QA pairs with:
- Question and expected answer
- Target system response
- All three scores (accuracy, relevance, completeness)
- Overall score
- Evaluation reasoning
- Response time
- Any errors

### Poor Performers Sheet

Filtered view of questions scoring < 60, helping you:
- Identify problematic question types
- Find gaps in your RAG system's knowledge
- Prioritize improvements

## Best Practices

### 1. Start Small
```bash
# Test with 10 samples first
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --max-samples 10
```

### 2. Adjust Rate Limiting
```bash
# If your endpoint has rate limits
python -m ragscore.assessment_cli \
  --endpoint http://api.example.com/query \
  --rate-limit 0.5  # 500ms between requests
```

### 3. Use Deterministic Evaluation
```bash
# For reproducible results
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --eval-temperature 0.0
```

### 4. Monitor Response Times
Check the "Avg Response Time" metric to identify performance issues.

### 5. Focus on Poor Performers
Use the "Poor Performers" sheet to guide improvements.

## Advanced: Custom Response Parsing

If your endpoint uses a non-standard response format, you can customize parsing:

```python
from ragscore.assessment import RAGEndpointClient

class CustomEndpointClient(RAGEndpointClient):
    def _parse_answer(self, res_json):
        # Custom parsing logic
        return res_json.get("data", {}).get("custom_field", "")

# Use custom client
client = CustomEndpointClient(endpoint_url="http://localhost:5000/query")
```

## Troubleshooting

### Issue: "Authentication failed"
**Solution**: Verify credentials and login URL are correct.

### Issue: "Empty response body"
**Solution**: Check if endpoint is running and accessible.

### Issue: "JSON parse error"
**Solution**: Your endpoint might return non-JSON. Check response format.

### Issue: "Evaluation failed"
**Solution**: Verify DASHSCOPE_API_KEY is set and valid.

### Issue: Low scores across the board
**Possible causes**:
1. RAG system needs tuning
2. Generated QA pairs are too difficult
3. Endpoint is returning generic/irrelevant responses

## Comparison with Original Script

The original `ragscore_aas_p3-2.py` had:
- ✅ Endpoint querying
- ✅ Basic LLM evaluation
- ❌ Single accuracy score only
- ❌ No modular design
- ❌ Limited error handling
- ❌ Hardcoded configuration

Our new module provides:
- ✅ **Multi-dimensional scoring** (accuracy, relevance, completeness)
- ✅ **Modular, reusable components**
- ✅ **Robust error handling and retries**
- ✅ **Flexible configuration** (CLI + env vars)
- ✅ **Better reporting** (3 sheets with insights)
- ✅ **Programmatic API** for integration
- ✅ **Production-ready code** with proper structure

## Suggestions for Further Improvements

### 1. Add More Evaluation Metrics
Consider adding:
- **Hallucination Detection**: Does response contain unsupported claims?
- **Citation Quality**: Are sources properly cited?
- **Latency Score**: Penalize slow responses
- **Consistency Score**: Compare multiple runs for same question

### 2. Implement A/B Testing
Compare two RAG systems side-by-side:
```python
results_v1 = assessment_v1.run_assessment()
results_v2 = assessment_v2.run_assessment()
compare_results(results_v1, results_v2)
```

### 3. Add Human-in-the-Loop
For critical applications:
```python
# Flag uncertain evaluations for human review
uncertain = df[df['evaluation_confidence'] < 0.7]
```

### 4. Continuous Monitoring
Set up automated assessment runs:
```bash
# Run daily assessment
0 2 * * * cd /path/to/ragscore && python -m ragscore.assessment_cli ...
```

### 5. Custom Evaluation Prompts
Allow domain-specific evaluation criteria:
```python
evaluator = LLMEvaluator(
    model="qwen-turbo",
    custom_prompt="Evaluate medical accuracy..."
)
```

## Next Steps

1. **Run your first assessment** with the Quick Start guide
2. **Analyze the report** to identify improvement areas
3. **Iterate on your RAG system** based on insights
4. **Re-run assessment** to measure improvements
5. **Set up continuous monitoring** for production systems

## Support

For issues or questions:
- Check the [main README](../README.md)
- Review [QUICK_START.md](../QUICK_START.md)
- Examine example code in `ragscore_aas_p3-2.py`

---

**Remember**: Assessment is iterative. Use these insights to continuously improve your RAG system!

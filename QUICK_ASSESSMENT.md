# Quick Assessment Reference

## 🚀 Quick Start (3 Steps)

### 1. Generate QA Pairs (Part 1)
```bash
python -m ragscore.cli generate
```

### 2. Run Assessment (Part 2)
```bash
python -m ragscore.assessment_cli --endpoint YOUR_ENDPOINT_URL
```

### 3. Check Report
```bash
open output/assessment_report.xlsx
```

---

## 📋 Common Commands

### Basic Assessment
```bash
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query
```

### With Authentication
```bash
python -m ragscore.assessment_cli \
  --endpoint http://api.example.com/query \
  --login-url http://api.example.com/login \
  --username demo \
  --password demo123
```

### Test Mode (Limited Samples)
```bash
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --max-samples 10
```

### Custom Output Path
```bash
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --output results/my_report.xlsx
```

### Slower Rate Limit
```bash
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --rate-limit 0.5
```

---

## 📊 Understanding Scores

Each response gets **4 scores** (all 0-100):

| Score | Measures | Good Score |
|-------|----------|------------|
| **Accuracy** | Factual correctness | ≥ 80 |
| **Relevance** | Answers the question | ≥ 80 |
| **Completeness** | Covers all key points | ≥ 80 |
| **Overall** | Average of above 3 | ≥ 80 |

### Score Ranges
- **80-100**: Excellent ✅
- **60-79**: Good ⚠️
- **0-59**: Poor ❌

---

## 📈 Report Structure

### Sheet 1: Summary
- Total questions
- Answer rate
- Average scores
- Score distribution

### Sheet 2: Detailed Results
- All QA pairs
- All scores
- Evaluation reasoning
- Response times

### Sheet 3: Poor Performers
- Questions scoring < 60
- Helps identify issues
- Guides improvements

---

## 🔧 Environment Variables

Add to `.env`:
```bash
# Required
DASHSCOPE_API_KEY=your_key_here

# Optional defaults
RAG_ENDPOINT_URL=http://localhost:5000/query
RAG_LOGIN_URL=http://localhost:5000/login
RAG_USERNAME=demo
RAG_PASSWORD=demo123
```

---

## 💻 Programmatic Usage

```python
from ragscore.assessment import (
    RAGEndpointClient, 
    LLMEvaluator, 
    RAGAssessment
)

# Setup
client = RAGEndpointClient(
    endpoint_url="http://localhost:5000/query"
)
evaluator = LLMEvaluator(model="qwen-turbo")
assessment = RAGAssessment(client, evaluator)

# Run
results = assessment.run_assessment(max_samples=100)
df = assessment.generate_report(results)

# Analyze
print(f"Average score: {df['overall_score'].mean():.2f}")
```

---

## 🎯 Key Features

### Multi-Dimensional Evaluation
- **Not just accuracy** - evaluates 3 dimensions
- **Actionable insights** - know what to improve
- **LLM-as-judge** - intelligent evaluation

### Robust Client
- **Retry logic** - handles transient failures
- **Authentication** - supports login-based auth
- **Streaming** - handles SSE responses
- **Flexible parsing** - works with various APIs

### Rich Reporting
- **Excel format** - easy to share and analyze
- **3 sheets** - summary, details, poor performers
- **Visual insights** - score distributions

---

## 🐛 Troubleshooting

### "QA file not found"
→ Run Part 1 first: `python -m ragscore.cli generate`

### "Authentication failed"
→ Check credentials and login URL

### "Empty response body"
→ Verify endpoint is running and accessible

### "JSON parse error"
→ Check if endpoint returns valid JSON

### Low scores everywhere
→ Check if endpoint is working correctly
→ Try with `--max-samples 5` first

---

## 📚 More Information

- **Detailed Guide**: `docs/ASSESSMENT_GUIDE.md`
- **Example Script**: `examples/run_assessment_example.py`
- **Main README**: `README.md`
- **Summary**: `ASSESSMENT_SUMMARY.md`

---

## 🎓 Best Practices

1. **Start small**: Test with `--max-samples 10` first
2. **Check endpoint**: Verify it's working before full assessment
3. **Use rate limiting**: Respect API limits with `--rate-limit`
4. **Review poor performers**: Focus on questions scoring < 60
5. **Iterate**: Run assessment → improve system → repeat

---

## 🔥 Pro Tips

### Compare Before/After
```bash
# Before improvements
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --output before.xlsx

# After improvements
python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --output after.xlsx
```

### Find Specific Issues
```python
# Load report
df = pd.read_excel("output/assessment_report.xlsx", 
                   sheet_name="Detailed Results")

# High relevance but low accuracy = wrong information
problematic = df[
    (df['relevance_score'] >= 70) & 
    (df['accuracy_score'] < 60)
]
print(f"Found {len(problematic)} responses with wrong info")
```

### Automate Daily Checks
```bash
# Add to crontab
0 2 * * * cd /path/to/ragscore && \
  python -m ragscore.assessment_cli \
  --endpoint http://localhost:5000/query \
  --output daily_$(date +\%Y\%m\%d).xlsx
```

---

**Need help?** Check the detailed guide: `docs/ASSESSMENT_GUIDE.md`

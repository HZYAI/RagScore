# Advanced Metrics Summary

## Quick Overview

I've implemented **three advanced evaluation metrics** for comprehensive RAG assessment:

### 1. 🔍 Hallucination Detection
**Identifies unsupported or fabricated claims in responses**

- **Score**: 0-100 (higher = fewer hallucinations)
- **Detects**: Claims not supported by retrieved context
- **Critical for**: Medical, legal, financial applications
- **Output**: List of specific hallucinated claims

```python
from ragscore.advanced_evaluator import HallucinationDetector

detector = HallucinationDetector()
result = detector.detect(question, response, context)

print(f"Score: {result['hallucination_score']}/100")
print(f"Hallucinations found: {result['hallucination_details']}")
```

### 2. 📚 Citation Quality Evaluation
**Evaluates source attribution and traceability**

- **Score**: 0-100 (higher = better citations)
- **Checks**: Presence, accuracy, completeness, format
- **Critical for**: Research, academic, compliance
- **Output**: Detailed citation analysis

```python
from ragscore.advanced_evaluator import CitationQualityEvaluator

evaluator = CitationQualityEvaluator()
result = evaluator.evaluate(question, response, context)

print(f"Score: {result['citation_quality_score']}/100")
print(f"Has citations: {result['has_citations']}")
```

### 3. ⚡ Latency Scoring
**Measures and scores response time performance**

- **Score**: 0-100 (higher = faster)
- **Configurable thresholds**: Excellent/Good/Acceptable
- **Critical for**: Chatbots, real-time applications
- **Output**: Score + performance category

```python
from ragscore.advanced_evaluator import LatencyScorer

scorer = LatencyScorer(
    excellent_threshold_ms=500,
    good_threshold_ms=2000,
    acceptable_threshold_ms=5000
)

score, is_slow, desc = scorer.score(latency_ms)
print(f"Latency: {score}/100 - {desc}")
```

---

## Complete Solution: AdvancedEvaluator

Combines all metrics into one evaluator:

```python
from ragscore.advanced_evaluator import AdvancedEvaluator

# Initialize with all metrics
evaluator = AdvancedEvaluator(
    model="qwen-turbo",
    temperature=0.0,
    enable_hallucination_detection=True,
    enable_citation_evaluation=True,
    enable_latency_scoring=True
)

# Evaluate
result = evaluator.evaluate(
    question="What is the capital of France?",
    expected_answer="Paris",
    target_response="The capital is Paris [1].",
    context="France's capital is Paris.",
    latency_ms=1234.5
)

# Access all metrics
print(f"Accuracy:       {result.accuracy_score}/100")
print(f"Relevance:      {result.relevance_score}/100")
print(f"Completeness:   {result.completeness_score}/100")
print(f"Hallucination:  {result.hallucination_score}/100")
print(f"Citation:       {result.citation_quality_score}/100")
print(f"Latency:        {result.latency_score}/100")
print(f"Overall:        {result.advanced_overall:.2f}/100")
```

---

## Custom Weights for Different Use Cases

### Medical/Legal (High Stakes)
```python
evaluator = AdvancedEvaluator(
    weights={
        "accuracy": 0.35,      # Critical
        "relevance": 0.10,
        "completeness": 0.15,
        "hallucination": 0.35, # Critical - no false info!
        "citation": 0.05,
        "latency": 0.00        # Speed not important
    }
)
```

### Chatbot (Speed & Relevance)
```python
evaluator = AdvancedEvaluator(
    weights={
        "accuracy": 0.20,
        "relevance": 0.35,     # Must be on-topic
        "completeness": 0.10,
        "hallucination": 0.15,
        "citation": 0.00,      # No citations needed
        "latency": 0.20        # Must be fast!
    }
)
```

### Research (Citations & Completeness)
```python
evaluator = AdvancedEvaluator(
    weights={
        "accuracy": 0.25,
        "relevance": 0.15,
        "completeness": 0.30,  # Comprehensive answers
        "hallucination": 0.15,
        "citation": 0.15,      # Must cite sources
        "latency": 0.00        # Can be slow
    }
)
```

---

## Key Analysis Patterns

### 1. Find High-Risk Responses
```python
# Hallucinations + No Citations = High Risk
high_risk = df[
    (df['has_hallucinations'] == True) & 
    (df['has_citations'] == False)
]
print(f"⚠️ {len(high_risk)} high-risk responses found")
```

### 2. Identify Optimization Opportunities
```python
# Accurate but slow = needs optimization
slow_accurate = df[
    (df['latency_score'] < 60) & 
    (df['accuracy_score'] >= 80)
]
print(f"🔧 {len(slow_accurate)} responses need speed optimization")
```

### 3. Citation Coverage
```python
citation_rate = (df['has_citations'].sum() / len(df)) * 100
print(f"📚 Citation coverage: {citation_rate:.1f}%")
```

### 4. Hallucination Rate
```python
halluc_rate = (df['has_hallucinations'].sum() / len(df)) * 100
print(f"🔍 Hallucination rate: {halluc_rate:.1f}%")
```

---

## Files Created

### 1. Core Module
**`src/ragscore/advanced_evaluator.py`** (700+ lines)
- `HallucinationDetector` class
- `CitationQualityEvaluator` class
- `LatencyScorer` class
- `AdvancedEvaluator` class (combines all)
- `AdvancedEvaluationResult` dataclass

### 2. Examples
**`examples/advanced_assessment_example.py`** (300+ lines)
- Example 1: Basic advanced evaluation
- Example 2: Individual detector usage
- Example 3: Custom weight configuration
- Example 4: Full pipeline integration
- Example 5: Result analysis patterns

### 3. Documentation
**`docs/ADVANCED_METRICS_GUIDE.md`** (600+ lines)
- Detailed explanation of each metric
- How each metric works
- Interpretation guidelines
- Integration guide
- Custom weights guide
- Analysis examples
- Best practices

---

## How Each Metric Works

### Hallucination Detection
1. **Compares** response against retrieved context
2. **Uses LLM** to identify unsupported claims
3. **Returns**:
   - Score (0-100)
   - Boolean flag (has_hallucinations)
   - List of specific hallucinations
   - Reasoning

**Example Detection**:
- Context: "Company founded in late 1990s"
- Response: "Company founded in 1995 by John Smith"
- Detected: ["1995" (too specific), "John Smith" (not in context)]

### Citation Quality
1. **Detects** citation markers ([1], "according to", etc.)
2. **Evaluates** accuracy and completeness
3. **Returns**:
   - Score (0-100)
   - Boolean flag (has_citations)
   - Detailed analysis

**Citation Patterns Recognized**:
- `[1]`, `[2]` - Numbered references
- `(1)`, `(2)` - Parenthetical
- `[source]` - Named references
- "according to", "as stated in" - Textual attribution

### Latency Scoring
1. **Measures** response time in milliseconds
2. **Compares** against configurable thresholds
3. **Returns**:
   - Score (0-100)
   - Boolean flag (is_slow)
   - Performance description

**Scoring Thresholds** (default):
- < 500ms: 100 (Excellent)
- 500-2000ms: 80-100 (Good)
- 2000-5000ms: 60-80 (Acceptable)
- > 5000ms: < 60 (Slow)

---

## Integration with Existing Assessment

To integrate into your existing assessment pipeline:

### Option 1: Replace Basic Evaluator
```python
from ragscore.assessment import RAGEndpointClient, RAGAssessment
from ragscore.advanced_evaluator import AdvancedEvaluator

client = RAGEndpointClient(endpoint_url="http://localhost:5000/query")
evaluator = AdvancedEvaluator(enable_all=True)  # Use advanced evaluator

assessment = RAGAssessment(client, evaluator)
results = assessment.run_assessment()
```

### Option 2: Use Alongside Basic Evaluator
```python
from ragscore.assessment import LLMEvaluator
from ragscore.advanced_evaluator import (
    HallucinationDetector,
    CitationQualityEvaluator,
    LatencyScorer
)

# Basic evaluation
basic_evaluator = LLMEvaluator()
basic_result = basic_evaluator.evaluate(question, expected, response)

# Add advanced metrics
halluc_detector = HallucinationDetector()
halluc_result = halluc_detector.detect(question, response, context)

citation_eval = CitationQualityEvaluator()
citation_result = citation_eval.evaluate(question, response, context)

latency_scorer = LatencyScorer()
latency_score, is_slow, desc = latency_scorer.score(latency_ms)
```

---

## When to Use Each Metric

| Metric | Use When | Skip When |
|--------|----------|-----------|
| **Hallucination** | High-stakes domains, factual accuracy critical | Casual chat, creative writing |
| **Citation** | Research, compliance, fact-checking needed | Conversational AI, no source tracking |
| **Latency** | Real-time apps, user-facing systems | Batch processing, background jobs |

---

## Performance Considerations

### LLM Calls per Evaluation

- **Basic evaluation**: 1 LLM call
- **+ Hallucination detection**: +1 LLM call
- **+ Citation evaluation**: +1 LLM call
- **Total with all metrics**: 3 LLM calls

### Optimization Tips

1. **Disable unused metrics**:
   ```python
   evaluator = AdvancedEvaluator(
       enable_hallucination_detection=True,
       enable_citation_evaluation=False,  # Skip if not needed
       enable_latency_scoring=True
   )
   ```

2. **Use faster model for non-critical evaluations**:
   ```python
   evaluator = AdvancedEvaluator(model="qwen-turbo")  # Fast
   # vs
   evaluator = AdvancedEvaluator(model="qwen-plus")   # More accurate
   ```

3. **Batch processing**: Evaluate multiple responses in parallel

---

## Example Output

```
📊 Advanced Evaluation Results:
   Accuracy:       85/100
   Relevance:      90/100
   Completeness:   80/100
   Hallucination:  95/100 ✅
   Citation:       70/100 ✅
   Latency:        88/100 ✅

   Basic Overall:    85.00/100
   Advanced Overall: 84.50/100

⚠️  Detected Hallucinations: None

📚 Citation Analysis:
   Response includes citations using [1] format.
   Most key claims are properly attributed.
   Consider adding citations for the population figure.

⚡ Latency: Good (1234ms)
```

---

## Next Steps

1. **Review the guide**: Read `docs/ADVANCED_METRICS_GUIDE.md`
2. **Try examples**: Run `examples/advanced_assessment_example.py`
3. **Integrate**: Use `AdvancedEvaluator` in your pipeline
4. **Customize**: Adjust weights for your use case
5. **Analyze**: Use analysis patterns to find issues

---

## Quick Reference

```python
# Import
from ragscore.advanced_evaluator import AdvancedEvaluator

# Create
evaluator = AdvancedEvaluator(enable_all=True)

# Evaluate
result = evaluator.evaluate(
    question=q,
    expected_answer=expected,
    target_response=response,
    context=context,
    latency_ms=latency
)

# Access metrics
print(result.hallucination_score)  # 0-100
print(result.citation_quality_score)  # 0-100
print(result.latency_score)  # 0-100
print(result.has_hallucinations)  # bool
print(result.has_citations)  # bool
print(result.is_slow)  # bool
```

---

**These advanced metrics provide deeper insights into RAG system quality beyond basic accuracy scoring!**

# Advanced Metrics Guide

## Overview

This guide explains the three advanced evaluation metrics for RAG systems:

1. **Hallucination Detection** - Identifies unsupported or fabricated claims
2. **Citation Quality** - Evaluates source attribution and traceability
3. **Latency Scoring** - Measures and scores response time performance

## Table of Contents

- [Hallucination Detection](#hallucination-detection)
- [Citation Quality Evaluation](#citation-quality-evaluation)
- [Latency Scoring](#latency-scoring)
- [Integration Guide](#integration-guide)
- [Custom Weights](#custom-weights)
- [Analysis Examples](#analysis-examples)

---

## Hallucination Detection

### What is a Hallucination?

In RAG systems, a **hallucination** is information in the response that:

1. **Is NOT supported** by the retrieved context
2. **Makes claims beyond** what the context states
3. **Contradicts** the context
4. **Invents** facts, dates, names, or numbers not in the context

### Why It Matters

Hallucinations are dangerous because:
- They erode user trust
- Can lead to incorrect decisions
- Are especially problematic in high-stakes domains (medical, legal, financial)
- May not be obvious to end users

### How It Works

The `HallucinationDetector` uses an LLM to:

1. **Compare** the response against the retrieved context
2. **Identify** specific claims not supported by context
3. **Score** from 0-100 (higher = fewer hallucinations)
4. **List** detected hallucinations for review

### Example

```python
from ragscore.advanced_evaluator import HallucinationDetector

detector = HallucinationDetector(model="qwen-turbo", temperature=0.0)

question = "When was the company founded?"
response = "The company was founded in 1995 by John Smith with 50 employees."
context = "The company was established in the late 1990s in California."

result = detector.detect(question, response, context)

print(f"Hallucination Score: {result['hallucination_score']}/100")
print(f"Has Hallucinations: {result['has_hallucinations']}")
print(f"Details: {result['hallucination_details']}")
# Output might show:
# - "1995" (context says "late 1990s", not specifically 1995)
# - "John Smith" (name not mentioned in context)
# - "50 employees" (number not in context)
```

### Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100 | Excellent - No or minimal hallucinations | ✅ Safe to use |
| 70-89 | Good - Minor unsupported details | ⚠️ Review flagged items |
| 50-69 | Fair - Some fabricated information | ⚠️ Needs improvement |
| 0-49 | Poor - Significant hallucinations | ❌ Do not use |

### Best Practices

1. **Always check context quality**: Poor retrieval → more hallucinations
2. **Review flagged items**: LLM detector may have false positives
3. **Track over time**: Monitor hallucination rate trends
4. **Use in high-stakes domains**: Essential for medical/legal/financial

---

## Citation Quality Evaluation

### What is Citation Quality?

Citation quality measures how well a RAG system **attributes information to sources**:

1. **Presence**: Are sources cited?
2. **Accuracy**: Do citations match the context?
3. **Completeness**: Are all key claims cited?
4. **Format**: Are citations clear and consistent?
5. **Traceability**: Can claims be traced to sources?

### Why It Matters

Good citations:
- Enable fact-checking
- Build user trust
- Support accountability
- Are required in academic/research contexts
- Help identify information sources

### How It Works

The `CitationQualityEvaluator`:

1. **Detects** citation markers (e.g., [1], [source], "according to")
2. **Evaluates** citation accuracy and completeness
3. **Scores** from 0-100 (higher = better citations)
4. **Provides** detailed analysis

### Citation Patterns Detected

```python
# Common citation formats recognized:
[1], [2], [3]                    # Numbered references
(1), (2), (3)                    # Parenthetical numbers
[source], [doc1]                 # Named references
"according to..."                # Textual attribution
"as stated in..."
"the document states..."
"source: ..."
```

### Example

```python
from ragscore.advanced_evaluator import CitationQualityEvaluator

evaluator = CitationQualityEvaluator()

question = "What is the capital of France?"
response_no_cite = "The capital of France is Paris."
response_with_cite = "According to the document, the capital of France is Paris [1]."
context = "France's capital is Paris, located in the north."

# Without citations
result1 = evaluator.evaluate(question, response_no_cite, context)
print(f"Score: {result1['citation_quality_score']}/100")  # Low score
print(f"Has Citations: {result1['has_citations']}")       # False

# With citations
result2 = evaluator.evaluate(question, response_with_cite, context)
print(f"Score: {result2['citation_quality_score']}/100")  # High score
print(f"Has Citations: {result2['has_citations']}")       # True
```

### Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100 | Excellent - Comprehensive, accurate citations | ✅ Ideal |
| 70-89 | Good - Most claims cited | ✅ Acceptable |
| 50-69 | Fair - Some citations missing | ⚠️ Improve citation generation |
| 0-49 | Poor - Few or no citations | ❌ Add citation support |

### Best Practices

1. **Configure your RAG system** to include citations
2. **Use consistent format**: Choose one citation style
3. **Cite key claims**: Not every sentence needs citation
4. **Make citations traceable**: Link to specific sources
5. **Consider domain**: Research needs more citations than chat

---

## Latency Scoring

### What is Latency Scoring?

Latency scoring evaluates **response time performance**:

- Measures time from query to response
- Scores based on configurable thresholds
- Identifies slow responses
- Helps balance quality vs speed

### Why It Matters

Response time affects:
- **User experience**: Slow = frustration
- **Scalability**: Fast = more concurrent users
- **Cost**: Faster = cheaper infrastructure
- **Use case fit**: Chat needs speed, research can be slower

### How It Works

The `LatencyScorer` uses configurable thresholds:

```python
from ragscore.advanced_evaluator import LatencyScorer

scorer = LatencyScorer(
    excellent_threshold_ms=500,    # 100 score
    good_threshold_ms=2000,        # 80 score
    acceptable_threshold_ms=5000   # 60 score
)

# Test different latencies
latencies = [300, 1000, 3000, 7000]
for latency in latencies:
    score, is_slow, desc = scorer.score(latency)
    print(f"{latency}ms → {score}/100 - {desc}")

# Output:
# 300ms → 100/100 - Excellent (300ms)
# 1000ms → 93/100 - Good (1000ms)
# 3000ms → 70/100 - Acceptable (3000ms)
# 7000ms → 40/100 - Slow (7000ms) ⚠️
```

### Scoring Formula

```
if latency <= excellent_threshold:
    score = 100

elif latency <= good_threshold:
    # Linear interpolation 100 → 80
    score = 100 - ((latency - excellent) / (good - excellent)) * 20

elif latency <= acceptable_threshold:
    # Linear interpolation 80 → 60
    score = 80 - ((latency - good) / (acceptable - good)) * 20

else:
    # Exponential decay below 60
    score = max(0, 60 - ((latency - acceptable) / 1000) * 10)
```

### Interpretation

| Latency | Score | Category | User Experience |
|---------|-------|----------|-----------------|
| < 500ms | 100 | Excellent | Instant, feels responsive |
| 500-2000ms | 80-100 | Good | Acceptable, slight delay |
| 2000-5000ms | 60-80 | Acceptable | Noticeable wait |
| > 5000ms | < 60 | Slow | Frustrating, too slow |

### Best Practices

1. **Set domain-appropriate thresholds**:
   - Chatbot: 500/1500/3000ms
   - Search: 1000/3000/5000ms
   - Research: 2000/5000/10000ms

2. **Monitor P95/P99 latencies**: Not just averages

3. **Identify bottlenecks**:
   ```python
   # Find slow but accurate responses
   slow_accurate = df[
       (df['latency_score'] < 60) & 
       (df['accuracy_score'] >= 80)
   ]
   # These need optimization, not quality improvement
   ```

4. **Balance quality vs speed**: Use custom weights

---

## Integration Guide

### Step 1: Use AdvancedEvaluator

```python
from ragscore.advanced_evaluator import AdvancedEvaluator

# Create evaluator with all metrics enabled
evaluator = AdvancedEvaluator(
    model="qwen-turbo",
    temperature=0.0,
    enable_hallucination_detection=True,
    enable_citation_evaluation=True,
    enable_latency_scoring=True
)

# Evaluate a response
result = evaluator.evaluate(
    question="What is the capital of France?",
    expected_answer="Paris",
    target_response="The capital is Paris [1].",
    context="France's capital is Paris.",
    latency_ms=1234.5
)

# Access all metrics
print(f"Accuracy: {result.accuracy_score}")
print(f"Hallucination: {result.hallucination_score}")
print(f"Citation: {result.citation_quality_score}")
print(f"Latency: {result.latency_score}")
print(f"Overall: {result.advanced_overall}")
```

### Step 2: Customize for Your Use Case

```python
# High-stakes domain (medical/legal)
evaluator_highstakes = AdvancedEvaluator(
    weights={
        "accuracy": 0.35,
        "relevance": 0.10,
        "completeness": 0.15,
        "hallucination": 0.35,  # Critical!
        "citation": 0.05,
        "latency": 0.00         # Don't care about speed
    }
)

# Conversational chatbot
evaluator_chatbot = AdvancedEvaluator(
    weights={
        "accuracy": 0.20,
        "relevance": 0.35,      # Must be on-topic
        "completeness": 0.10,
        "hallucination": 0.15,
        "citation": 0.00,       # No citations needed
        "latency": 0.20         # Speed matters!
    }
)

# Research/academic
evaluator_research = AdvancedEvaluator(
    weights={
        "accuracy": 0.25,
        "relevance": 0.15,
        "completeness": 0.30,   # Comprehensive answers
        "citation": 0.15,       # Must cite sources
        "hallucination": 0.15,
        "latency": 0.00         # Can be slow
    }
)
```

### Step 3: Generate Enhanced Reports

```python
import pandas as pd
from dataclasses import asdict

# Run assessment with advanced evaluator
results = []
for qa in qa_pairs:
    result = evaluator.evaluate(...)
    results.append(asdict(result))

# Create DataFrame
df = pd.DataFrame(results)

# Save with all metrics
df.to_excel("advanced_assessment_report.xlsx", index=False)
```

---

## Custom Weights

### Understanding Weight Configuration

The overall score is calculated as:

```python
overall_score = (
    w_accuracy * accuracy_score +
    w_relevance * relevance_score +
    w_completeness * completeness_score +
    w_hallucination * hallucination_score +
    w_citation * citation_quality_score +
    w_latency * latency_score
)
```

Where weights must sum to 1.0.

### Default Weights

```python
default_weights = {
    "accuracy": 0.25,      # 25%
    "relevance": 0.20,     # 20%
    "completeness": 0.20,  # 20%
    "hallucination": 0.20, # 20%
    "citation": 0.10,      # 10%
    "latency": 0.05        # 5%
}
```

### Use Case Examples

#### 1. Medical/Legal (High Stakes)
```python
weights = {
    "accuracy": 0.35,      # Critical
    "relevance": 0.10,
    "completeness": 0.15,
    "hallucination": 0.35, # Critical - no false info!
    "citation": 0.05,
    "latency": 0.00        # Speed not important
}
```

#### 2. Customer Support Chatbot
```python
weights = {
    "accuracy": 0.20,
    "relevance": 0.35,     # Must answer the question
    "completeness": 0.10,  # Brief is okay
    "hallucination": 0.15,
    "citation": 0.00,      # No citations needed
    "latency": 0.20        # Must be fast!
}
```

#### 3. Research Assistant
```python
weights = {
    "accuracy": 0.25,
    "relevance": 0.15,
    "completeness": 0.30,  # Comprehensive answers
    "hallucination": 0.15,
    "citation": 0.15,      # Must cite sources
    "latency": 0.00        # Can take time
}
```

#### 4. E-commerce Search
```python
weights = {
    "accuracy": 0.25,
    "relevance": 0.40,     # Show relevant products
    "completeness": 0.05,  # Brief descriptions okay
    "hallucination": 0.10,
    "citation": 0.00,
    "latency": 0.20        # Fast search results
}
```

---

## Analysis Examples

### 1. Find High-Risk Responses

```python
# Responses with hallucinations AND no citations
high_risk = df[
    (df['has_hallucinations'] == True) & 
    (df['has_citations'] == False)
]

print(f"⚠️ Found {len(high_risk)} high-risk responses")
print("These are making unsupported claims without attribution!")
```

### 2. Identify Optimization Opportunities

```python
# Slow but accurate responses
slow_accurate = df[
    (df['latency_score'] < 60) & 
    (df['accuracy_score'] >= 80)
]

print(f"Found {len(slow_accurate)} responses that need optimization")
print("Quality is good, but speed needs improvement")
```

### 3. Citation Coverage Analysis

```python
# Questions without citations
no_citations = df[df['has_citations'] == False]

print(f"Citation rate: {(1 - len(no_citations)/len(df)) * 100:.1f}%")

# Group by question type
citation_by_type = df.groupby('question_type')['has_citations'].mean()
print("\nCitation rate by question type:")
print(citation_by_type)
```

### 4. Hallucination Patterns

```python
# Analyze which question types have more hallucinations
halluc_by_difficulty = df.groupby('difficulty')['has_hallucinations'].mean()

print("Hallucination rate by difficulty:")
print(halluc_by_difficulty)

# Find common hallucination patterns
hallucinated = df[df['has_hallucinations'] == True]
print("\nMost common hallucination types:")
# Analyze hallucination_details field
```

### 5. Speed vs Quality Tradeoff

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.scatter(
    df['latency_ms'], 
    df['accuracy_score'],
    c=df['advanced_overall'],
    cmap='viridis',
    alpha=0.6
)
plt.xlabel('Response Time (ms)')
plt.ylabel('Accuracy Score')
plt.colorbar(label='Overall Score')
plt.title('Speed vs Accuracy Tradeoff')
plt.axvline(x=2000, color='r', linestyle='--', label='2s threshold')
plt.legend()
plt.savefig('speed_vs_accuracy.png')
```

### 6. Generate Insights Report

```python
insights = {
    'Total Questions': len(df),
    'Avg Accuracy': df['accuracy_score'].mean(),
    'Avg Hallucination Score': df['hallucination_score'].mean(),
    'Hallucination Rate (%)': (df['has_hallucinations'].sum() / len(df) * 100),
    'Citation Rate (%)': (df['has_citations'].sum() / len(df) * 100),
    'Avg Latency (ms)': df['latency_ms'].mean(),
    'Slow Response Rate (%)': (df['is_slow'].sum() / len(df) * 100),
    'High Risk Responses': len(df[
        (df['has_hallucinations'] == True) & 
        (df['has_citations'] == False)
    ])
}

print("\n" + "="*50)
print("ASSESSMENT INSIGHTS")
print("="*50)
for key, value in insights.items():
    print(f"{key:.<40} {value:.2f}")
print("="*50)
```

---

## Best Practices Summary

### 1. Choose Appropriate Metrics

| Use Case | Hallucination | Citation | Latency |
|----------|--------------|----------|---------|
| Medical/Legal | ✅ Critical | ✅ Important | ❌ Optional |
| Chatbot | ⚠️ Important | ❌ Optional | ✅ Critical |
| Research | ✅ Important | ✅ Critical | ❌ Optional |
| E-commerce | ⚠️ Important | ❌ Optional | ✅ Important |

### 2. Set Realistic Thresholds

- **Hallucination**: Aim for >90 in high-stakes domains
- **Citation**: Aim for >70 in research/academic contexts
- **Latency**: Set based on user expectations

### 3. Monitor Trends

- Track metrics over time
- Set up alerts for degradation
- Compare before/after improvements

### 4. Take Action

- **High hallucination rate** → Improve retrieval quality
- **Low citation rate** → Add citation generation
- **High latency** → Optimize retrieval/generation
- **High risk responses** → Add safety filters

---

## Next Steps

1. **Try the examples**: Run `examples/advanced_assessment_example.py`
2. **Integrate into pipeline**: Use `AdvancedEvaluator` in your assessment
3. **Customize weights**: Match your use case priorities
4. **Analyze results**: Use the analysis patterns above
5. **Iterate**: Improve based on insights

---

## Support

- **Module**: `src/ragscore/advanced_evaluator.py`
- **Examples**: `examples/advanced_assessment_example.py`
- **Main Guide**: `docs/ASSESSMENT_GUIDE.md`

For questions or issues, review the example code and documentation.

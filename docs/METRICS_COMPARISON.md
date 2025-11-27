# RAG Evaluation Metrics Comparison

## Overview: Basic vs Advanced Metrics

### Basic Metrics (3 dimensions)
```
┌─────────────────────────────────────────────┐
│         BASIC EVALUATION                    │
├─────────────────────────────────────────────┤
│ 1. Accuracy (0-100)                         │
│    └─ Factual correctness                   │
│                                             │
│ 2. Relevance (0-100)                        │
│    └─ Addresses the question                │
│                                             │
│ 3. Completeness (0-100)                     │
│    └─ Covers key points                     │
│                                             │
│ Overall = Average of 3                      │
└─────────────────────────────────────────────┘
```

### Advanced Metrics (6 dimensions)
```
┌─────────────────────────────────────────────┐
│       ADVANCED EVALUATION                   │
├─────────────────────────────────────────────┤
│ 1. Accuracy (0-100)                         │
│ 2. Relevance (0-100)                        │
│ 3. Completeness (0-100)                     │
│                                             │
│ 4. Hallucination (0-100) 🆕                 │
│    └─ Detects unsupported claims            │
│    └─ Lists specific hallucinations         │
│                                             │
│ 5. Citation Quality (0-100) 🆕              │
│    └─ Evaluates source attribution          │
│    └─ Checks traceability                   │
│                                             │
│ 6. Latency (0-100) 🆕                       │
│    └─ Scores response time                  │
│    └─ Configurable thresholds               │
│                                             │
│ Overall = Weighted average of 6             │
└─────────────────────────────────────────────┘
```

---

## Detailed Comparison Table

| Aspect | Basic Metrics | Advanced Metrics |
|--------|--------------|------------------|
| **Dimensions** | 3 (Accuracy, Relevance, Completeness) | 6 (+ Hallucination, Citation, Latency) |
| **LLM Calls** | 1 per evaluation | 3 per evaluation |
| **Evaluation Time** | ~2-3 seconds | ~6-8 seconds |
| **Detects Hallucinations** | ❌ No | ✅ Yes, with specific examples |
| **Evaluates Citations** | ❌ No | ✅ Yes, with analysis |
| **Measures Speed** | ❌ No | ✅ Yes, with scoring |
| **Customizable Weights** | ❌ No (equal weights) | ✅ Yes (per use case) |
| **Risk Identification** | Limited | High-risk response detection |
| **Use Case Flexibility** | General purpose | Domain-specific tuning |
| **Cost** | Lower (1 LLM call) | Higher (3 LLM calls) |
| **Insights Depth** | Basic quality metrics | Comprehensive analysis |

---

## When to Use Each

### Use Basic Metrics When:
- ✅ Quick evaluation needed
- ✅ Cost is a concern
- ✅ General quality assessment sufficient
- ✅ Simple pass/fail criteria
- ✅ Prototyping/testing phase

### Use Advanced Metrics When:
- ✅ High-stakes domain (medical, legal, financial)
- ✅ Need to detect hallucinations
- ✅ Citations are required
- ✅ Performance optimization needed
- ✅ Detailed insights required
- ✅ Production deployment

---

## Example Scenarios

### Scenario 1: Medical Q&A System

**Question**: "What are the side effects of aspirin?"

**Response**: "Aspirin can cause stomach bleeding, allergic reactions, and in rare cases, Reye's syndrome in children. It may also interact with blood thinners [1]."

**Context**: "Aspirin side effects include gastrointestinal bleeding, allergic reactions, and Reye's syndrome in children. It can interact with anticoagulants."

#### Basic Evaluation:
```
Accuracy:     90/100  ✅
Relevance:    95/100  ✅
Completeness: 85/100  ✅
Overall:      90/100  ✅
```
**Verdict**: Looks good!

#### Advanced Evaluation:
```
Accuracy:       90/100  ✅
Relevance:      95/100  ✅
Completeness:   85/100  ✅
Hallucination:  100/100 ✅ (No unsupported claims)
Citation:       80/100  ✅ (Has citations)
Latency:        70/100  ⚠️  (2.5s - acceptable but slow)
Overall:        88/100  ✅
```
**Verdict**: Good quality, no hallucinations, has citations. Could optimize speed.

**Key Insight**: Advanced metrics confirm safety (no hallucinations) and proper attribution (citations) - critical for medical domain!

---

### Scenario 2: Chatbot with Hallucination

**Question**: "Who founded Microsoft?"

**Response**: "Microsoft was founded in 1975 by Bill Gates and Steve Jobs in Seattle, Washington."

**Context**: "Microsoft was founded by Bill Gates and Paul Allen in 1975 in Albuquerque, New Mexico."

#### Basic Evaluation:
```
Accuracy:     70/100  ⚠️  (Some errors)
Relevance:    100/100 ✅
Completeness: 90/100  ✅
Overall:      87/100  ✅
```
**Verdict**: Decent score, might pass

#### Advanced Evaluation:
```
Accuracy:       70/100  ⚠️
Relevance:      100/100 ✅
Completeness:   90/100  ✅
Hallucination:  40/100  ❌ CRITICAL!
Citation:       0/100   ❌
Latency:        100/100 ✅

Detected Hallucinations:
• "Steve Jobs" - Should be "Paul Allen"
• "Seattle, Washington" - Should be "Albuquerque, New Mexico"

Overall: 67/100 ⚠️
```
**Verdict**: FAILS - Contains factual errors (hallucinations)

**Key Insight**: Advanced metrics caught the hallucinations that basic metrics missed! The response seemed "good enough" but contained false information.

---

### Scenario 3: Research Assistant

**Question**: "What is quantum entanglement?"

**Response A** (No citations):
"Quantum entanglement is a phenomenon where particles become correlated. When you measure one particle, it instantly affects the other, regardless of distance."

**Response B** (With citations):
"Quantum entanglement is a phenomenon where particles become correlated [1]. When you measure one particle, it instantly affects the other, regardless of distance [2]."

#### Basic Evaluation (Both responses):
```
Response A:
  Accuracy:     85/100
  Relevance:    90/100
  Completeness: 80/100
  Overall:      85/100

Response B:
  Accuracy:     85/100
  Relevance:    90/100
  Completeness: 80/100
  Overall:      85/100
```
**Verdict**: Both score the same!

#### Advanced Evaluation:
```
Response A:
  Citation: 0/100 ❌ (No citations)
  Overall:  72/100 ⚠️

Response B:
  Citation: 90/100 ✅ (Good citations)
  Overall:  86/100 ✅
```
**Verdict**: Response B is better for research context

**Key Insight**: In research/academic contexts, citations matter! Advanced metrics capture this requirement.

---

## Cost-Benefit Analysis

### Basic Metrics
```
Cost per evaluation:    1 LLM call  (~$0.001)
Time per evaluation:    2-3 seconds
Insights provided:      3 scores
Best for:              General assessment
```

### Advanced Metrics
```
Cost per evaluation:    3 LLM calls (~$0.003)
Time per evaluation:    6-8 seconds
Insights provided:      6 scores + detailed analysis
Best for:              Production systems, high-stakes domains
```

### ROI Calculation

For a system with 1000 evaluations:

**Basic Metrics**:
- Cost: $1
- Time: 40 minutes
- Catches: General quality issues

**Advanced Metrics**:
- Cost: $3 (+$2)
- Time: 2 hours (+1h 20m)
- Catches: Hallucinations, citation issues, performance problems

**Value**: The extra $2 and 80 minutes can prevent:
- ❌ Deploying a system with hallucinations
- ❌ Missing citation requirements
- ❌ Performance issues in production
- ❌ User trust erosion
- ❌ Potential legal/compliance issues

**Verdict**: Advanced metrics worth it for production systems!

---

## Hybrid Approach

### Strategy: Use Both Strategically

```python
# Phase 1: Development - Use Basic (Fast iteration)
basic_evaluator = LLMEvaluator()
quick_results = basic_evaluator.evaluate(...)

# Phase 2: Pre-production - Use Advanced (Thorough check)
advanced_evaluator = AdvancedEvaluator(enable_all=True)
detailed_results = advanced_evaluator.evaluate(...)

# Phase 3: Production - Use Selective Advanced
# Only enable metrics that matter for your use case
production_evaluator = AdvancedEvaluator(
    enable_hallucination_detection=True,  # Critical
    enable_citation_evaluation=False,     # Not needed
    enable_latency_scoring=True           # Important
)
```

### Sampling Strategy

```python
# Evaluate 100% with basic metrics
all_results_basic = assess_with_basic(all_qa_pairs)

# Evaluate 10% with advanced metrics (random sample)
sample = random.sample(all_qa_pairs, k=len(all_qa_pairs)//10)
sample_results_advanced = assess_with_advanced(sample)

# Deep dive on failures
failures = [r for r in all_results_basic if r.overall_score < 60]
failure_results_advanced = assess_with_advanced(failures)
```

---

## Decision Matrix

### Choose Basic Metrics If:
| Criteria | Answer |
|----------|--------|
| Is this a high-stakes domain? | ❌ No |
| Are hallucinations a major concern? | ❌ No |
| Do you need citations? | ❌ No |
| Is performance critical? | ❌ No |
| Is this for production? | ❌ No |
| Need detailed insights? | ❌ No |

### Choose Advanced Metrics If:
| Criteria | Answer |
|----------|--------|
| Is this a high-stakes domain? | ✅ Yes |
| Are hallucinations a major concern? | ✅ Yes |
| Do you need citations? | ✅ Yes |
| Is performance critical? | ✅ Yes |
| Is this for production? | ✅ Yes |
| Need detailed insights? | ✅ Yes |

**Rule of Thumb**: If you answered "Yes" to 2+ questions, use Advanced Metrics.

---

## Migration Path

### Step 1: Start with Basic
```python
from ragscore.assessment import LLMEvaluator

evaluator = LLMEvaluator()
results = evaluate_all(evaluator)
```

### Step 2: Add Hallucination Detection
```python
from ragscore.advanced_evaluator import AdvancedEvaluator

evaluator = AdvancedEvaluator(
    enable_hallucination_detection=True,
    enable_citation_evaluation=False,
    enable_latency_scoring=False
)
```

### Step 3: Add Citation Evaluation
```python
evaluator = AdvancedEvaluator(
    enable_hallucination_detection=True,
    enable_citation_evaluation=True,
    enable_latency_scoring=False
)
```

### Step 4: Add Latency Scoring
```python
evaluator = AdvancedEvaluator(enable_all=True)
```

### Step 5: Customize Weights
```python
evaluator = AdvancedEvaluator(
    enable_all=True,
    weights={
        "accuracy": 0.30,
        "relevance": 0.20,
        "completeness": 0.20,
        "hallucination": 0.20,
        "citation": 0.05,
        "latency": 0.05
    }
)
```

---

## Summary

### Basic Metrics: The Foundation
- ✅ Fast and cost-effective
- ✅ Good for general assessment
- ✅ Sufficient for many use cases
- ⚠️ Misses hallucinations
- ⚠️ Doesn't evaluate citations
- ⚠️ Ignores performance

### Advanced Metrics: The Complete Picture
- ✅ Detects hallucinations
- ✅ Evaluates citations
- ✅ Measures performance
- ✅ Customizable for use case
- ✅ Production-ready insights
- ⚠️ Higher cost
- ⚠️ Slower evaluation

### Recommendation
- **Development**: Start with Basic
- **Testing**: Use Advanced on samples
- **Production**: Use Advanced with custom weights
- **High-stakes**: Always use Advanced with hallucination detection

---

**Choose the right metrics for your use case. When in doubt, start with Basic and upgrade to Advanced as needed!**

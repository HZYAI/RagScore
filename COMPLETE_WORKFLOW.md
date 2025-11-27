# Complete RAG Evaluation Workflow

## 📋 Two-Part Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PART 1: QA GENERATION                            │
│                    (Document → QA Pairs)                            │
└─────────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    PART 2: RAG ASSESSMENT                           │
│                    (QA Pairs → Evaluation Report)                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 PART 1: QA Generation

### Input
- 📄 Documents (PDF, TXT, MD, HTML)

### Process
```
Upload Documents
    ↓
Extract Text
    ↓
Split into Chunks
    ↓
Build Vector Index
    ↓
Generate QA Pairs (using LLM)
    ↓
Save to JSONL file
```

### Output
- `output/generated_qas.jsonl` - Contains all generated QA pairs

### Frontend View
```
┌─────────────────────────────────────────────────────────────────┐
│  Left Panel                  │  Right Panel                     │
│                              │                                  │
│  📁 Upload Documents         │  📊 Dashboard Stats              │
│  [Drag & Drop Area]          │  ┌────────┬────────┬────────┐   │
│                              │  │ 160    │ 01:03  │ 100%   │   │
│  📄 document.pdf        ×    │  │ QA Pairs│ Time  │Progress│   │
│                              │  └────────┴────────┴────────┘   │
│  ⚙️ Configuration            │                                  │
│  Questions per Chunk: 5      │  Q: What is...?                 │
│  Difficulty: Easy Medium Hard│  A: The answer is...            │
│  Speed: 5                    │  [easy] 📄 document.pdf         │
│                              │                                  │
│  🚀 Generate QA Pairs        │  Q: How does...?                │
│  💾 Download JSON            │  A: It works by...              │
│  🗑️ Clear All               │  [medium] 📄 document.pdf       │
│                              │                                  │
│                              │  ... (more QA pairs)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 PART 2: RAG Assessment

### Input
- `output/generated_qas.jsonl` - QA pairs from Part 1
- RAG endpoint URL
- Authentication credentials (optional)

### Process
```
Load QA Pairs
    ↓
For each QA pair:
    ├─ Query RAG endpoint with question
    ├─ Measure response time
    ├─ Get target system's response
    ├─ Compare with expected answer (using LLM)
    ├─ Score on 3 dimensions:
    │   ├─ Accuracy (0-100)
    │   ├─ Relevance (0-100)
    │   └─ Completeness (0-100)
    └─ Calculate overall score
    ↓
Generate Excel Report
```

### Output
- `output/assessment_report.xlsx` - Comprehensive evaluation report

### Frontend View (NEW!)
```
┌─────────────────────────────────────────────────────────────────┐
│  Left Panel (continued)      │  Right Panel                     │
│                              │                                  │
│  ─────────────────────────   │  (QA pairs displayed above)     │
│                              │                                  │
│  📊 RAG Assessment (Part 2)  │                                  │
│                              │                                  │
│  RAG Endpoint URL            │                                  │
│  [http://localhost:5000/...] │                                  │
│                              │                                  │
│  Login URL (Optional)        │                                  │
│  [http://localhost:5000/...] │                                  │
│                              │                                  │
│  Username (Optional)         │                                  │
│  [demo]                      │                                  │
│                              │                                  │
│  Password (Optional)         │                                  │
│  [••••••]                    │                                  │
│                              │                                  │
│  Max Samples (Optional)      │                                  │
│  [10]                        │                                  │
│                              │                                  │
│  🎯 Start Assessment         │                                  │
│                              │                                  │
│  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░ 50%   │                                  │
│  Assessing QA pairs... (5/10)│                                  │
│                              │                                  │
│  📈 Assessment Results       │                                  │
│  ┌──────────┬──────────┐    │                                  │
│  │ Total: 10│ Answered:│    │                                  │
│  │          │ 10       │    │                                  │
│  ├──────────┼──────────┤    │                                  │
│  │ Accuracy │ Relevance│    │                                  │
│  │ 85.3     │ 90.2     │    │                                  │
│  ├──────────┼──────────┤    │                                  │
│  │ Complete │ Overall  │    │                                  │
│  │ 80.1     │ 85.2     │    │                                  │
│  ├──────────┼──────────┤    │                                  │
│  │ Avg Time │ Excellent│    │                                  │
│  │ 1234ms   │ 7        │    │                                  │
│  ├──────────┼──────────┤    │                                  │
│  │ Good: 2  │ Poor: 1  │    │                                  │
│  └──────────┴──────────┘    │                                  │
│                              │                                  │
│  📄 Download Report          │                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete End-to-End Flow

### Step-by-Step User Journey

```
1. USER UPLOADS DOCUMENT
   └─> Frontend: Shows file in list
   └─> Backend: Saves to data/docs/

2. USER CLICKS "GENERATE QA PAIRS"
   └─> Frontend: Shows progress bar
   └─> Backend: 
       ├─ Reads document
       ├─ Chunks text
       ├─ Builds vector index
       ├─ Generates QA pairs with LLM
       └─ Saves to output/generated_qas.jsonl
   └─> Frontend: Displays QA pairs in real-time
   └─> Frontend: Shows "Assessment Section" ✨ NEW!

3. USER ENTERS RAG ENDPOINT DETAILS
   └─> Endpoint URL: http://47.99.205.203:5004/api/query
   └─> Login URL: http://47.99.205.203:5004/login
   └─> Username: demo
   └─> Password: demo123
   └─> Max Samples: 10 (for quick test)

4. USER CLICKS "START ASSESSMENT"
   └─> Frontend: Shows progress bar
   └─> Backend:
       ├─ Loads QA pairs from JSONL
       ├─ For each QA pair:
       │   ├─ Authenticates with RAG endpoint
       │   ├─ Sends question to endpoint
       │   ├─ Measures response time
       │   ├─ Gets response
       │   ├─ Evaluates with LLM (accuracy, relevance, completeness)
       │   └─ Sends progress update to frontend
       └─ Generates Excel report
   └─> Frontend: Updates progress bar in real-time
   └─> Frontend: Displays results when complete

5. USER VIEWS RESULTS
   └─> Frontend: Shows color-coded metrics
   └─> Green scores (≥80): Excellent
   └─> Blue scores (60-79): Good
   └─> Red scores (<60): Poor

6. USER DOWNLOADS REPORT
   └─> Frontend: Triggers download
   └─> Backend: Sends assessment_report.xlsx
   └─> User gets comprehensive Excel report with:
       ├─ Summary sheet
       ├─ Detailed results sheet
       └─ Poor performers sheet
```

---

## 📊 Data Flow Diagram

```
┌──────────────┐
│  Documents   │
│  (PDF, TXT)  │
└──────┬───────┘
       │
       ↓ PART 1: QA Generation
┌──────────────────────┐
│  Text Extraction     │
│  & Chunking          │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  Vector Index        │
│  (FAISS)             │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  LLM QA Generation   │
│  (DashScope)         │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  generated_qas.jsonl │ ← Intermediate Output
└──────┬───────────────┘
       │
       ↓ PART 2: Assessment
┌──────────────────────┐
│  RAG Endpoint Query  │
│  (User's System)     │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  LLM Evaluation      │
│  (DashScope)         │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│  assessment_report   │ ← Final Output
│  .xlsx               │
└──────────────────────┘
```

---

## 🎨 Frontend Architecture

### Components

```
index.html
├─ Left Panel (Controls)
│  ├─ Header
│  ├─ Upload Section
│  ├─ Configuration Section
│  ├─ Action Buttons
│  └─ Assessment Section ✨ NEW!
│     ├─ Endpoint Configuration
│     ├─ Progress Display
│     └─ Results Display
│
└─ Right Panel (Results)
   ├─ Dashboard Stats
   └─ QA Pairs List
```

### JavaScript Functions

```javascript
// Part 1: QA Generation
- handleFiles()          // Upload documents
- startGeneration()      // Start QA generation
- displayQA()            // Display QA pairs

// Part 2: Assessment ✨ NEW!
- startAssessmentBtn.click()  // Start assessment
- generate_assessment()        // Run assessment with SSE
- displayAssessmentResults()   // Show results
- downloadReportBtn.click()    // Download Excel report
```

---

## 🔧 Backend Architecture

### API Endpoints

```
FastAPI Application
├─ /                          # Main page
├─ /login                     # Login page
├─ POST /api/upload           # Upload documents
├─ POST /api/generate         # Trigger QA generation
├─ WebSocket /ws/generate     # QA generation with progress
├─ GET /api/download          # Download QA pairs JSON
├─ GET /api/results           # Get QA pairs
├─ DELETE /api/clear          # Clear all data
├─ POST /api/assess           # Run assessment ✨ NEW!
└─ GET /api/download-report   # Download Excel report ✨ NEW!
```

### Python Modules

```
src/ragscore/
├─ data_processing.py    # Document reading & chunking
├─ vector_store.py       # FAISS index building
├─ llm.py                # LLM QA generation
├─ assessment.py         # RAG assessment ✨ Part 2
├─ advanced_evaluator.py # Advanced metrics (hallucination, citation, latency)
└─ web/
   ├─ app.py             # FastAPI application
   └─ templates/
      └─ index.html      # Frontend UI
```

---

## 📈 Evaluation Metrics

### Basic Metrics (Always Included)
1. **Accuracy** (0-100)
   - Factual correctness
   - Semantic equivalence with expected answer

2. **Relevance** (0-100)
   - How well response addresses the question
   - On-topic vs off-topic

3. **Completeness** (0-100)
   - Coverage of key points from expected answer
   - Comprehensive vs partial

### Advanced Metrics (Optional)
4. **Hallucination Detection** (0-100)
   - Identifies unsupported claims
   - Compares response to retrieved context

5. **Citation Quality** (0-100)
   - Evaluates source attribution
   - Checks citation presence and accuracy

6. **Latency Scoring** (0-100)
   - Measures response time
   - Scores based on configurable thresholds

---

## 🎯 Use Cases

### 1. Development & Testing
```
- Upload test documents
- Generate small QA set (max_samples: 10)
- Quick assessment to verify system works
- Iterate on RAG system improvements
```

### 2. Quality Assurance
```
- Upload representative documents
- Generate full QA set (all samples)
- Comprehensive assessment
- Identify problem areas (poor performers)
```

### 3. Benchmarking
```
- Use same QA set across different RAG systems
- Compare scores (accuracy, relevance, completeness)
- Measure performance (response time)
- Make data-driven decisions
```

### 4. Production Monitoring
```
- Regular assessments with fixed QA set
- Track score trends over time
- Detect regressions
- Ensure consistent quality
```

---

## 🚀 Quick Start Commands

### CLI Mode (Part 2 Only)
```bash
# Run assessment from command line
python -m ragscore.assessment_cli \
  --endpoint http://47.99.205.203:5004/api/query \
  --login-url http://47.99.205.203:5004/login \
  --username demo \
  --password demo123 \
  --max-samples 10
```

### Web Mode (Part 1 + Part 2)
```bash
# Start web server
python -m ragscore.web.app

# Open browser
# http://localhost:8000
```

---

## 📦 Output Files

### Generated Files
```
RAGScore/
├─ data/
│  └─ docs/
│     └─ uploaded_document.pdf
│
└─ output/
   ├─ generated_qas.jsonl          # Part 1 output
   ├─ assessment_report.xlsx       # Part 2 output
   ├─ index.faiss                  # Vector index
   └─ meta.json                    # Chunk metadata
```

### Excel Report Structure
```
assessment_report.xlsx
├─ Sheet 1: Summary
│  └─ Overall statistics and score distribution
│
├─ Sheet 2: Detailed Results
│  └─ Every QA pair with all scores and responses
│
└─ Sheet 3: Poor Performers
   └─ QA pairs with overall score < 60
```

---

## 🎉 Summary

**You now have a complete, production-ready RAG evaluation system with:**

✅ Beautiful web interface  
✅ Two-part evaluation pipeline  
✅ Real-time progress tracking  
✅ Comprehensive scoring (6 dimensions)  
✅ Detailed Excel reports  
✅ CLI and web modes  
✅ Bilingual support (EN/中文)  
✅ Error handling and validation  
✅ Authentication support  
✅ Flexible configuration  

**Ready to evaluate your RAG system! 🚀**

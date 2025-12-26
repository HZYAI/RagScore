"""RAGScore Web Application

Provides a web interface for QA pair generation.
"""

import json
import asyncio
import shutil
from pathlib import Path
from typing import List

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
    Request,
)
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .. import config
from ..data_processing import read_docs, initialize_nltk
from ..vector_store import build_index, save_index
from ..llm import generate_qa_for_chunk
import random

app = FastAPI(title="RAGScore API", description="QA Dataset Generation for RAG Systems")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Store active WebSocket connections and uploaded files
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.uploaded_files: List[str] = []  # Track uploaded filenames

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_file = Path(__file__).parent / "templates" / "index.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text())
    return HTMLResponse(content="<h1>RAGScore Web Interface</h1><p>Template not found</p>")

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serve the login page"""
    html_file = Path(__file__).parent / "templates" / "login.html"
    if html_file.exists():
        return HTMLResponse(content=html_file.read_text())
    return HTMLResponse(content="<h1>Login</h1><p>Template not found</p>")

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Handle file uploads"""
    try:
        # Ensure docs directory exists
        config.DOCS_DIR.mkdir(parents=True, exist_ok=True)
        
        uploaded_files = []
        for file in files:
            file_path = config.DOCS_DIR / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append(file.filename)
        
        # Store uploaded filenames for this session
        manager.uploaded_files = uploaded_files
        
        return JSONResponse({
            "status": "success",
            "message": f"Uploaded {len(uploaded_files)} file(s)",
            "files": uploaded_files
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate")
async def start_generation():
    """Start the QA generation process"""
    return JSONResponse({
        "status": "started",
        "message": "QA generation started. Connect to WebSocket for progress updates."
    })

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """WebSocket endpoint for real-time QA generation with progress updates"""
    await manager.connect(websocket)
    try:
        # Receive configuration from client
        config_data = await websocket.receive_json()
        questions_per_chunk = config_data.get('questionsPerChunk', config.NUM_Q_PER_CHUNK)
        
        # Initialize NLTK
        await manager.send_message({"type": "progress", "step": "init", "message": "Initializing..."}, websocket)
        initialize_nltk()
        
        # Read documents - only process uploaded files if available
        await manager.send_message({"type": "progress", "step": "reading", "message": "Reading documents..."}, websocket)
        
        if manager.uploaded_files:
            # Only process the uploaded files
            await manager.send_message({
                "type": "progress",
                "step": "reading",
                "message": f"Processing {len(manager.uploaded_files)} uploaded file(s)..."
            }, websocket)
            docs = read_docs(dir_path=config.DOCS_DIR, specific_files=manager.uploaded_files)
        else:
            # Fallback to processing all documents
            docs = read_docs()
        
        if not docs:
            await manager.send_message({"type": "error", "message": "No documents found"}, websocket)
            return
        
        await manager.send_message({
            "type": "progress",
            "step": "indexing",
            "message": f"Building index for {len(docs)} documents..."
        }, websocket)
        
        # Build index
        index, meta = build_index(docs)
        if index is None:
            await manager.send_message({"type": "error", "message": "Failed to build index"}, websocket)
            return
        
        save_index(index, meta)
        
        # Generate QA pairs
        await manager.send_message({
            "type": "progress",
            "step": "generating",
            "message": f"Generating QA pairs for {len(meta)} chunks...",
            "total": len(meta)
        }, websocket)
        
        all_qas = []
        processed_count = 0
        
        # Process chunks concurrently with a semaphore to limit concurrent requests
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent API calls
        
        async def process_chunk(idx, m):
            nonlocal processed_count
            if len(m["text"].split()) < 40:
                return []
            
            difficulty = random.choice(config.DIFFICULTY_MIX)
            
            async with semaphore:
                try:
                    # Run the blocking API call in a thread pool
                    loop = asyncio.get_event_loop()
                    with ThreadPoolExecutor() as executor:
                        items = await loop.run_in_executor(
                            executor,
                            generate_qa_for_chunk,
                            m["text"],
                            difficulty,
                            questions_per_chunk
                        )
                    
                    chunk_qas = []
                    for item in items:
                        item.update({
                            "doc_id": m["doc_id"],
                            "chunk_id": m["chunk_id"],
                            "source_path": m["path"],
                            "difficulty": difficulty,
                        })
                        chunk_qas.append(item)
                        
                        # Send each QA pair immediately as it's created
                        await manager.send_message({
                            "type": "qa_created",
                            "qa": item
                        }, websocket)
                    
                    processed_count += 1
                    # Send progress update
                    await manager.send_message({
                        "type": "progress",
                        "step": "generating",
                        "current": processed_count,
                        "total": len(meta),
                        "message": f"Generated {len(all_qas) + len(chunk_qas)} QA pairs so far..."
                    }, websocket)
                    
                    return chunk_qas
                    
                except Exception as e:
                    print(f"Error generating QA for chunk {m['chunk_id']}: {e}")
                    return []
        
        # Create tasks for all chunks
        tasks = [process_chunk(idx, m) for idx, m in enumerate(meta)]
        
        # Process all chunks concurrently
        results = await asyncio.gather(*tasks)
        
        # Flatten results
        for chunk_qas in results:
            all_qas.extend(chunk_qas)
        
        # Save results
        await manager.send_message({
            "type": "progress",
            "step": "saving",
            "message": "Saving results..."
        }, websocket)
        
        with open(config.GENERATED_QAS_PATH, "w", encoding="utf-8") as f:
            for qa in all_qas:
                f.write(json.dumps(qa, ensure_ascii=False) + "\n")
        
        # Send completion message
        await manager.send_message({
            "type": "complete",
            "message": f"Successfully generated {len(all_qas)} QA pairs!",
            "count": len(all_qas),
            "file": str(config.GENERATED_QAS_PATH)
        }, websocket)
        
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_message({"type": "error", "message": str(e)}, websocket)
        manager.disconnect(websocket)

@app.get("/api/download")
async def download_results():
    """Download the generated QA pairs as JSON"""
    if not config.GENERATED_QAS_PATH.exists():
        raise HTTPException(status_code=404, detail="No results found. Please generate QA pairs first.")
    
    return FileResponse(
        path=config.GENERATED_QAS_PATH,
        filename="generated_qas.jsonl",
        media_type="application/json"
    )

@app.get("/api/results")
async def get_results():
    """Get the generated QA pairs"""
    if not config.GENERATED_QAS_PATH.exists():
        return JSONResponse({"status": "not_found", "data": []})
    
    results = []
    with open(config.GENERATED_QAS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    
    return JSONResponse({"status": "success", "count": len(results), "data": results})

@app.delete("/api/clear")
async def clear_data():
    """Clear uploaded documents and generated results"""
    try:
        # Clear documents
        if config.DOCS_DIR.exists():
            for file in config.DOCS_DIR.iterdir():
                if file.is_file():
                    file.unlink()
        
        # Clear outputs
        if config.GENERATED_QAS_PATH.exists():
            config.GENERATED_QAS_PATH.unlink()
        if config.INDEX_PATH.exists():
            config.INDEX_PATH.unlink()
        if config.META_PATH.exists():
            config.META_PATH.unlink()
        
        # Clear uploaded files tracking
        manager.uploaded_files = []
        
        return JSONResponse({"status": "success", "message": "All data cleared"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assess")
async def run_assessment(request: Request):
    """Run RAG assessment with streaming progress updates"""
    try:
        from ..assessment import RAGEndpointClient, LLMEvaluator, RAGAssessment
        
        # Parse request body
        body = await request.json()
        endpoint_url = body.get('endpoint_url')
        login_url = body.get('login_url')
        username = body.get('username')
        password = body.get('password')
        max_samples = body.get('max_samples')
        
        if not endpoint_url:
            return JSONResponse({"type": "error", "message": "Endpoint URL is required"}, status_code=400)
        
        async def generate_assessment():
            try:
                # Send initial status
                yield f"data: {json.dumps({'type': 'progress', 'current': 0, 'total': 1, 'message': 'Initializing assessment...'})}\n\n"
                
                # Initialize client and evaluator
                client = RAGEndpointClient(
                    endpoint_url=endpoint_url,
                    login_url=login_url,
                    username=username,
                    password=password
                )
                
                evaluator = LLMEvaluator()
                assessment = RAGAssessment(client, evaluator)
                
                # Load QA pairs
                qa_pairs = assessment.load_qa_pairs()
                
                if max_samples:
                    qa_pairs = qa_pairs[:max_samples]
                
                total = len(qa_pairs)
                yield f"data: {json.dumps({'type': 'progress', 'current': 0, 'total': total, 'message': f'Assessing {total} QA pairs...'})}\n\n"
                
                # Run assessment with progress updates
                results = []
                for idx, qa in enumerate(qa_pairs, 1):
                    result = assessment.assess_single(qa)
                    results.append(result)
                    
                    # Send individual result
                    result_data = {
                        'question': result.question,
                        'expected_answer': result.expected_answer,
                        'target_response': result.target_response,
                        'accuracy_score': result.accuracy_score,
                        'relevance_score': result.relevance_score,
                        'completeness_score': result.completeness_score,
                        'overall_score': result.overall_score,
                        'response_time_ms': result.response_time_ms,
                        'evaluation_reasoning': result.evaluation_reasoning,
                        'error': result.error
                    }
                    yield f"data: {json.dumps({'type': 'result', 'result': result_data})}\n\n"
                    
                    # Send progress update
                    yield f"data: {json.dumps({'type': 'progress', 'current': idx, 'total': total, 'message': f'Assessing QA pairs...'})}\n\n"
                    
                    # Small delay to avoid overwhelming the client
                    await asyncio.sleep(0.01)
                
                # Generate report
                df = assessment.generate_report(results, output_path=config.ASSESSMENT_REPORT_PATH)
                
                # Calculate summary
                summary = {
                    'total_questions': len(df),
                    'answered_questions': int(df['target_response'].astype(str).str.strip().astype(bool).sum()),
                    'avg_accuracy': float(df['accuracy_score'].mean()),
                    'avg_relevance': float(df['relevance_score'].mean()),
                    'avg_completeness': float(df['completeness_score'].mean()),
                    'avg_overall': float(df['overall_score'].mean()),
                    'avg_response_time': float(df['response_time_ms'].mean()),
                    'excellent': int((df['overall_score'] >= 80).sum()),
                    'good': int(((df['overall_score'] >= 60) & (df['overall_score'] < 80)).sum()),
                    'poor': int((df['overall_score'] < 60).sum())
                }
                
                # Send completion
                yield f"data: {json.dumps({'type': 'complete', 'summary': summary})}\n\n"
                
            except Exception as e:
                import traceback
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                print(f"Assessment error: {error_msg}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return StreamingResponse(generate_assessment(), media_type="text/event-stream")
        
    except Exception as e:
        return JSONResponse({"type": "error", "message": str(e)}, status_code=500)

@app.get("/api/download-report")
async def download_assessment_report():
    """Download the assessment report Excel file"""
    if not config.ASSESSMENT_REPORT_PATH.exists():
        raise HTTPException(status_code=404, detail="No assessment report found. Please run assessment first.")
    
    return FileResponse(
        path=config.ASSESSMENT_REPORT_PATH,
        filename="assessment_report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

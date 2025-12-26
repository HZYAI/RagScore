#!/usr/bin/env python3
"""Test script to run the pipeline and see detailed errors.

This is a manual test script, not part of the automated test suite.
For automated tests, see the tests/ directory.
"""

print("Starting pipeline test...")

try:
    print("1. Importing modules...")
    from ragscore.data_processing import read_docs, initialize_nltk
    from ragscore.vector_store import build_index, save_index
    from ragscore.llm import generate_qa_for_chunk
    from ragscore import config
    import random
    
    print("2. Initializing NLTK...")
    initialize_nltk()
    
    print("3. Reading documents...")
    docs = read_docs()
    print(f"   Found {len(docs)} documents")
    
    if not docs:
        print("   ERROR: No documents found!")
        sys.exit(1)
    
    print("4. Building index...")
    index, meta = build_index(docs)
    
    if index is None:
        print("   ERROR: Failed to build index!")
        sys.exit(1)
    
    print(f"   Index built with {len(meta)} chunks")
    
    print("5. Saving index...")
    save_index(index, meta)
    
    print("6. Generating QA pairs (testing with first 3 chunks)...")
    all_qas = []
    
    for i, m in enumerate(meta[:3]):  # Test with just 3 chunks
        if len(m["text"].split()) < 40:
            print(f"   Skipping chunk {i} (too short)")
            continue
        
        difficulty = random.choice(config.DIFFICULTY_MIX)
        print(f"   Generating QA for chunk {i} (difficulty: {difficulty})...")
        
        try:
            items = generate_qa_for_chunk(m["text"], difficulty, n=2)
            print(f"   Generated {len(items)} QA pairs")
            
            for item in items:
                item.update({
                    "doc_id": m["doc_id"],
                    "chunk_id": m["chunk_id"],
                    "source_path": m["path"],
                    "difficulty": difficulty,
                })
                all_qas.append(item)
        except Exception as e:
            print(f"   ERROR generating QA: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n7. Total QA pairs generated: {len(all_qas)}")
    
    if all_qas:
        print("\nSample QA pair:")
        print(f"Q: {all_qas[0]['question']}")
        print(f"A: {all_qas[0]['answer']}")
    
    print("\n✅ Pipeline test completed successfully!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

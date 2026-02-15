# ============================================================
# RAGScore Detailed Evaluation - Colab Test Script
# ============================================================
# Run this in Google Colab to test the feature/detailed-evaluation branch.
#
# Copy-paste each section into separate Colab cells.
# ============================================================

# --- Cell 1: Install from branch ---
# !pip install git+https://github.com/HZYAI/RagScore.git@feature/detailed-evaluation

# --- Cell 2: Setup ---
# import os
# os.environ["OPENAI_API_KEY"] = "sk-..."  # or use Ollama

# --- Cell 3: Quick test (default mode - should work same as before) ---
# from ragscore import quick_test
#
# def dummy_rag(question):
#     return "I don't know the answer to that question."
#
# result = quick_test(dummy_rag, docs="sample.txt", n=3)
# print(result)
# result.plot()

# --- Cell 4: Quick test (detailed mode - NEW) ---
# result = quick_test(dummy_rag, docs="sample.txt", n=3, detailed=True)
# print(result)
# print()
# print("DataFrame columns:", list(result.df.columns))
# print()
# display(result.df[["question", "score", "correctness", "completeness",
#                     "relevance", "conciseness", "faithfulness"]])
# result.plot()  # Should show 4-panel with radar chart

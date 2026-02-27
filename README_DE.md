<div align="center">
  <img src="RAGScore.png" alt="RAGScore Logo" width="400"/>
  
  [![PyPI version](https://badge.fury.io/py/ragscore.svg)](https://pypi.org/project/ragscore/)
  [![PyPI Downloads](https://static.pepy.tech/personalized-badge/ragscore?period=total&units=international_system&left_color=black&right_color=green&left_text=downloads)](https://pepy.tech/projects/ragscore)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
  [![Ollama](https://img.shields.io/badge/Ollama-Supported-orange)](https://ollama.ai)
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/HZYAI/RagScore/blob/main/examples/detailed_evaluation_demo.ipynb)
  [![MCP](https://img.shields.io/badge/MCP-Server-purple)](https://modelcontextprotocol.io)
  
  **QA-Datensätze generieren & RAG-Systeme bewerten – in 2 Befehlen**
  
  🔒 Datenschutz zuerst • ⚡ Blitzschnell • 🤖 Jedes LLM • 🏠 Lokal oder Cloud • 🌍 Mehrsprachig
  
  [English](README.md) | [中文](README_CN.md) | [日本語](README_JP.md) | [Deutsch](README_DE.md)
</div>

---

## ⚡ RAG-Bewertung in 2 Zeilen

```bash
# Schritt 1: QA-Paare aus Dokumenten generieren
ragscore generate docs/

# Schritt 2: RAG-System bewerten
ragscore evaluate http://localhost:8000/query
```

**Das war's.** Erhalten Sie sofort Genauigkeitswerte und fehlerhafte QA-Paare.

```
============================================================
✅ AUSGEZEICHNET: 85/100 korrekt (85,0%)
Durchschnittliche Bewertung: 4,20/5,0
============================================================

❌ 15 fehlerhafte Paare:

  1. F: "Was ist RAG?"
     Bewertung: 2/5 - Sachlich falsch

  2. F: "Wie funktioniert die Suche?"
     Bewertung: 3/5 - Unvollständige Antwort
```

---

## 🚀 Schnellstart

### Installation

```bash
pip install ragscore              # Kernversion (Ollama-kompatibel)
pip install "ragscore[openai]"    # + OpenAI-Unterstützung
pip install "ragscore[notebook]"  # + Jupyter/Colab-Unterstützung
pip install "ragscore[all]"       # + Alle Anbieter
```

### Option 1: Python API (Notebook-freundlich)

Perfekt für **Jupyter, Colab und schnelle Iteration**. Sofortige Visualisierungen.

```python
from ragscore import quick_test

# 1. RAG in einer Zeile prüfen
result = quick_test(
    endpoint="http://localhost:8000/query",  # Ihre RAG-API
    docs="docs/",                            # Ihre Dokumente
    n=10,                                    # Anzahl Testfragen
)

# 1b. Zielgruppenspezifische QA-Generierung
result = quick_test(
    endpoint="http://localhost:8000/query",
    docs="docs/",
    audience="Entwickler",                   # Wer stellt die Fragen?
    purpose="API-Integration",               # Wofür ist das Dokument?
)

# 2. Bericht anzeigen
result.plot()

# 3. Fehler untersuchen
bad_rows = result.df[result.df['score'] < 3]
display(bad_rows[['question', 'rag_answer', 'reason']])
```

**Rich Object API:**
- `result.accuracy` - Genauigkeitswert
- `result.df` - Pandas DataFrame aller Ergebnisse
- `result.plot()` - 3-Panel-Visualisierung (4-Panel mit `detailed=True`)
- `result.corrections` - Liste der zu korrigierenden Elemente

### Option 2: CLI (Produktion)

### QA-Paare generieren

```bash
# API-Schlüssel setzen (oder lokales Ollama verwenden – kein Schlüssel nötig!)
export OPENAI_API_KEY="sk-..."

# Aus beliebigen Dokumenten generieren
ragscore generate paper.pdf
ragscore generate docs/*.pdf --concurrency 10

# Zielgruppenspezifische QA-Generierung
ragscore generate docs/ --audience Entwickler --purpose FAQ
ragscore generate docs/ --audience Kunden --purpose Vertrieb
ragscore generate docs/ --audience "Compliance-Prüfer" --purpose "Sicherheitsaudit"
```

### RAG bewerten

```bash
# RAG-Endpunkt angeben
ragscore evaluate http://localhost:8000/query

# Benutzerdefinierte Optionen
ragscore evaluate http://api/ask --model gpt-4o --output results.json
```

---

## 🔬 Detaillierte Multi-Metrik-Bewertung

Gehen Sie über einen einzelnen Score hinaus. Fügen Sie `detailed=True` hinzu, um **5 diagnostische Dimensionen** pro Antwort zu erhalten — im selben LLM-Aufruf.

```python
result = quick_test(
    endpoint=my_rag,
    docs="docs/",
    n=10,
    detailed=True,  # ⭐ Multi-Metrik-Bewertung aktivieren
)

# Detaillierte Metriken pro Frage
display(result.df[[
    "question", "score", "correctness", "completeness",
    "relevance", "conciseness", "faithfulness"
]])

# Radarchart + 4-Panel-Visualisierung
result.plot()
```

```
==================================================
✅ BESTANDEN: 9/10 korrekt (90%)
Durchschnittliche Bewertung: 4,3/5,0
Schwellenwert: 70%
──────────────────────────────────────────────────
  Korrektheit: 4,5/5,0
  Vollständigkeit: 4,2/5,0
  Relevanz: 4,8/5,0
  Prägnanz: 4,1/5,0
  Treue: 4,6/5,0
==================================================
```

| Metrik | Messung | Skala |
|--------|---------|-------|
| **Korrektheit** | Semantische Übereinstimmung mit Referenzantwort | 5 = vollständig korrekt |
| **Vollständigkeit** | Alle Kernpunkte abgedeckt | 5 = vollständig abgedeckt |
| **Relevanz** | Beantwortet die gestellte Frage | 5 = perfekt passend |
| **Prägnanz** | Fokussiert, kein Fülltext | 5 = prägnant und präzise |
| **Treue** | Quellengetreu, keine Erfindungen | 5 = vollständig treu |

**CLI:**
```bash
ragscore evaluate http://localhost:8000/query --detailed
```

> 📓 [Vollständiges Demo-Notebook](examples/detailed_evaluation_demo.ipynb) — Mini-RAG erstellen und mit detaillierten Metriken testen.
>
> 🎯 [Zielgruppen- & Zweck-Demo](examples/audience_purpose_demo.ipynb) — QA-Generierung für Entwickler, Kunden, Prüfer und mehr.

---

## 🏠 100% privat mit lokalen LLMs

```bash
# Ollama verwenden – keine API-Schlüssel, keine Cloud, 100% privat
ollama pull llama3.1
ragscore generate vertrauliche_docs/*.pdf
ragscore evaluate http://localhost:8000/query
```

**Perfekt für:** Gesundheitswesen 🏥 • Recht ⚖️ • Finanzen 🏦 • Forschung 🔬

---

## 🔌 Unterstützte LLMs

| Anbieter | Einrichtung | Hinweise |
|----------|-------------|----------|
| **Ollama** | `ollama serve` | Lokal, kostenlos, privat |
| **OpenAI** | `export OPENAI_API_KEY="sk-..."` | Beste Qualität |
| **Anthropic** | `export ANTHROPIC_API_KEY="..."` | Langer Kontext |
| **DashScope** | `export DASHSCOPE_API_KEY="..."` | Qwen-Modelle |
| **vLLM** | `export LLM_BASE_URL="..."` | Produktionsreif |
| **OpenAI-kompatibel** | `export LLM_BASE_URL="..."` | Groq, Together usw. |

---

## 📊 Ausgabeformate

### Generierte QA-Paare (`output/generated_qas.jsonl`)

```json
{
  "id": "abc123",
  "question": "Was ist RAG?",
  "answer": "RAG (Retrieval-Augmented Generation) kombiniert...",
  "rationale": "Dies wird in der Einleitung explizit erwähnt...",
  "support_span": "RAG-Systeme rufen relevante Dokumente ab...",
  "difficulty": "medium",
  "source_path": "docs/rag_intro.pdf"
}
```

### Bewertungsergebnisse (`--output results.json`)

```json
{
  "summary": {
    "total": 100,
    "correct": 85,
    "incorrect": 15,
    "accuracy": 0.85,
    "avg_score": 4.2
  },
  "incorrect_pairs": [
    {
      "question": "Was ist RAG?",
      "golden_answer": "RAG kombiniert Suche mit Generierung...",
      "rag_answer": "RAG ist ein Datenbanksystem.",
      "score": 2,
      "reason": "Sachlich falsch – RAG ist keine Datenbank"
    }
  ]
}
```

---

## 🧪 Python API

```python
from ragscore import run_pipeline, run_evaluation

# QA-Paare generieren
run_pipeline(paths=["docs/"], concurrency=10)

# Zielgruppenspezifische QA-Paare generieren
run_pipeline(
    paths=["docs/"],
    audience="Support-Ingenieure",
    purpose="Chatbot-Feinabstimmung",
)

# RAG bewerten
results = run_evaluation(
    endpoint="http://localhost:8000/query",
    model="gpt-4o",  # LLM für Bewertung
)
print(f"Genauigkeit: {results.accuracy:.1%}")
```

---

## 🤖 KI-Agent-Integration

RAGScore ist für KI-Agenten und Automatisierung konzipiert:

```bash
# Strukturierte CLI mit vorhersagbarer Ausgabe
ragscore generate docs/ --concurrency 5
ragscore evaluate http://api/query --output results.json

# Exit-Codes: 0 = Erfolg, 1 = Fehler
# JSON-Ausgabe für programmatische Auswertung
```

**CLI-Referenz:**

| Befehl | Beschreibung |
|--------|--------------|
| `ragscore generate <Pfade>` | QA-Paare aus Dokumenten generieren |
| `ragscore generate <Pfade> --audience <Wer>` | Zielgruppenspezifische QA-Generierung |
| `ragscore generate <Pfade> --purpose <Warum>` | Zweckbezogene QA-Generierung |
| `ragscore evaluate <Endpunkt>` | RAG gegen Referenz-QAs bewerten |
| `ragscore evaluate <Endpunkt> --detailed` | Multi-Metrik-Bewertung |
| `ragscore --help` | Alle Befehle und Optionen anzeigen |
| `ragscore generate --help` | Generierungsoptionen anzeigen |
| `ragscore evaluate --help` | Bewertungsoptionen anzeigen |

---

## ⚙️ Konfiguration

Funktioniert ohne Konfiguration. Optionale Umgebungsvariablen:

```bash
export RAGSCORE_CHUNK_SIZE=512          # Chunk-Größe für Dokumente
export RAGSCORE_QUESTIONS_PER_CHUNK=5   # QAs pro Chunk
export RAGSCORE_WORK_DIR=/path/to/dir   # Arbeitsverzeichnis
```

---

## 🔐 Datenschutz & Sicherheit

| Daten | Cloud-LLM | Lokales LLM |
|-------|-----------|-------------|
| Dokumente | ✅ Lokal | ✅ Lokal |
| Textchunks | ⚠️ An LLM gesendet | ✅ Lokal |
| Generierte QAs | ✅ Lokal | ✅ Lokal |
| Bewertungsergebnisse | ✅ Lokal | ✅ Lokal |

**Compliance:** DSGVO ✅ • HIPAA ✅ (mit lokalen LLMs) • SOC 2 ✅

---

## 🧪 Entwicklung

```bash
git clone https://github.com/HZYAI/RagScore.git
cd RagScore
pip install -e ".[dev,all]"
pytest
```

---

## 🔗 Links

- [GitHub](https://github.com/HZYAI/RagScore) • [PyPI](https://pypi.org/project/ragscore/) • [Issues](https://github.com/HZYAI/RagScore/issues) • [Discussions](https://github.com/HZYAI/RagScore/discussions)

---

<p align="center">
  <b>⭐ Wenn RAGScore Ihnen hilft, geben Sie uns einen Stern auf GitHub!</b><br>
  Mit ❤️ für die RAG-Community erstellt
</p>

# RAG-Based Phishing URL Awareness Checker

An educational cybersecurity project that combines **Rule-Based URL Analysis, Retrieval-Augmented Generation (RAG), Sentence Transformers, ChromaDB, and a Local LLM** to help users understand suspicious URL characteristics and phishing-related security concepts.

The application analyzes URL text without visiting websites or downloading files. Its RAG assistant retrieves relevant information from an ingested cybersecurity knowledge base and uses a locally hosted language model to explain phishing-related questions.

---

## Project Overview

Phishing attacks use deceptive URLs and websites to trick users into revealing sensitive information, downloading malicious files, or interacting with fraudulent services.

This project provides two complementary capabilities:

1. **URL Awareness Checker:** Examines a submitted URL for predefined suspicious characteristics.
2. **RAG-Based Phishing Assistant:** Retrieves relevant passages from a cybersecurity PDF knowledge base and provides contextual explanations using a local LLM.

The application is designed for cybersecurity awareness and educational purposes. It is not a commercial threat-intelligence platform or a replacement for antivirus, browser protection, or professional security analysis.

## Key Features

- Rule-based suspicious URL analysis.
- Detection of six predefined URL warning indicators.
- URL structure and hostname analysis.
- Phishing knowledge retrieval using semantic search.
- PDF-based knowledge ingestion.
- Sentence Transformer embeddings.
- ChromaDB vector database.
- Local LLM integration through Ollama.
- Interactive Streamlit interface.
- Retrieved knowledge passages displayed to the user.
- Unit testing for URL detection.
- No automatic URL visiting or file downloading.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web application interface |
| Sentence Transformers | Text embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| ChromaDB | Vector database |
| PyPDF | PDF text extraction |
| Ollama | Local LLM runtime |
| Llama 3.2 | Local language model |
| Requests | Communication with Ollama |
| unittest | Unit testing |

## System Architecture

```text
                 USER
                   |
                   v
          STREAMLIT APPLICATION
                   |
          +--------+--------+
          |                 |
          v                 v
     URL CHECKER        RAG ASSISTANT
          |                 |
          v                 v
   URL PARSING       USER QUESTION
          |                 |
          v                 v
   RULE-BASED       SENTENCE TRANSFORMER
   DETECTION                |
          |                 v
          v              CHROMADB
   WARNING SIGNS             |
          |                 v
          |           RETRIEVED CONTEXT
          |                 |
          |                 v
          |             OLLAMA
          |                 |
          |                 v
          |            LLAMA 3.2
          |                 |
          +--------+--------+
                   |
                   v
              USER RESULTS


        PDF KNOWLEDGE BASE
                 |
                 v
           PDF EXTRACTION
                 |
                 v
             CHUNKING
                 |
                 v
          EMBEDDING MODEL
                 |
                 v
             CHROMADB
```

## URL Warning Indicators

The URL checker examines the following characteristics:

| Indicator | Description |
|---|---|
| @ Symbol | Checks whether the URL contains an @ symbol. |
| Long URL | Flags URLs longer than 100 characters. |
| IP Address | Checks whether the hostname is an IPv4 address. |
| Multiple Subdomains | Flags hostnames containing five or more labels. |
| Punycode | Detects hostnames containing the `xn--` prefix. |
| HTTP Protocol | Identifies URLs using HTTP instead of HTTPS. |

### Important

These are heuristic warning indicators, not definitive evidence of phishing or malware.

A URL without these indicators is not guaranteed to be safe. HTTPS also does not guarantee that a website is trustworthy.

The checker does not visit URLs, perform network scans, download files, or execute submitted content.

## RAG Knowledge Base

The project uses a PDF knowledge base containing educational information about:

- Phishing fundamentals.
- URL anatomy and structure.
- Suspicious URL indicators.
- URL analysis examples.
- Phishing awareness.
- Safe investigation practices.
- Security terminology.

### RAG Workflow

1. Extract text from the PDF using PyPDF.
2. Split the extracted text into overlapping chunks.
3. Generate semantic embeddings using `all-MiniLM-L6-v2`.
4. Store embeddings and text in ChromaDB.
5. Convert user questions into embeddings.
6. Retrieve relevant knowledge passages.
7. Pass retrieved context to the local LLM.
8. Generate an answer grounded in the retrieved material.

## Project Setup

### Prerequisites

Install the following:

- Python 3.10 or later.
- Visual Studio Code.
- Git.
- Ollama for local LLM execution.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/phishing-rag-system.git
cd phishing-rag-system
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Ingest the PDF Knowledge Base

Ensure the PDF exists at:

```text
data/phishing_url_rag_knowledge_base.pdf
```

Run:

```powershell
python -m ingestion.ingest
```

This command extracts PDF content, creates text chunks, generates embeddings, and stores them in ChromaDB.

### 5. Install and Configure Ollama

Download Ollama:

https://ollama.com/download/windows

Download the Llama 3.2 model:

```powershell
ollama pull llama3.2
```

Verify the model:

```powershell
ollama list
```

Test the model:

```powershell
ollama run llama3.2
```

Exit the interactive model using:

```text
/bye
```

Ollama should be running locally before using the RAG assistant.

### 6. Launch the Application

From the project root:

```powershell
streamlit run app/main.py
```

Open the application in your browser:

http://localhost:8501

## Running Unit Tests

Execute:

```powershell
python -m unittest discover -s tests -v
```

The tests validate the URL detector's behavior against predefined cases.

## Sample URL Test Cases

| Test | Sample URL | Expected observations |
|---|---|---|
| 1 | `https://www.example.com/login` | No listed indicators |
| 2 | `http://192.0.2.10/account` | IP address and HTTP |
| 3 | `http://example.com@sample.invalid/login` | @ symbol and HTTP |
| 4 | `https://a.b.c.d.e.example.invalid/path` | Multiple hostname labels |
| 5 | `https://xn--example.invalid/` | Punycode |

These examples use reserved or illustrative domains. They are intended for testing and should not be treated as live threat intelligence.

## Important Project Commands

| Purpose | Command |
|---|---|
| Activate environment | `.\.venv\Scripts\Activate.ps1` |
| Install packages | `pip install -r requirements.txt` |
| Ingest PDF | `python -m ingestion.ingest` |
| Re-ingest PDF | `python -m ingestion.ingest` |
| Run tests | `python -m unittest discover -s tests -v` |
| Check Ollama | `ollama --version` |
| List models | `ollama list` |
| Download LLM | `ollama pull llama3.2` |
| Test LLM | `ollama run llama3.2` |
| Run application | `streamlit run app/main.py` |

## Project Limitations

- URL analysis is based on predefined heuristic rules.
- The application does not verify whether a website is currently malicious.
- No live threat-intelligence feeds are integrated.
- RAG responses depend on the quality and coverage of the ingested knowledge base.
- Local LLM responses may occasionally be inaccurate.
- No URL is opened or scanned automatically.
- No executable or malware sample is downloaded or executed.

## Future Enhancements

- Integration with trusted threat-intelligence APIs.
- Expanded URL feature analysis.
- Explainable risk indicators.
- Improved RAG evaluation and retrieval quality.
- Additional cybersecurity knowledge sources.
- Support for multiple local LLM models.
- Enhanced logging and report generation.
- More comprehensive unit and integration tests.

## Security and Responsible Use

This project is intended strictly for cybersecurity education, awareness, and authorized testing.

Never submit confidential URLs or sensitive information to external services without authorization.

The application analyzes URL text only. It does not access submitted websites or execute their contents.

## Author

**Manikanta Badrisetty**

B.Tech Computer Science and Engineering – Cyber Security

SRM Institute of Science and Technology

GitHub: https://github.com/YOUR_USERNAME

---

## License

This project is intended for educational and research purposes. Add a license file if you wish to specify the terms under which others may use, modify, and distribute the project.

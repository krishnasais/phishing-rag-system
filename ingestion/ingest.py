import argparse
import re

from pathlib import Path
import chromadb

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]

PDF_PATH = (
    ROOT / "data" /
    "phishing_url_rag_knowledge_base.pdf"
)

DB_PATH = ROOT / "vectorstore" / "chroma"

COLLECTION_NAME = "phishing_knowledge"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ----------------------------------
# 1. PDF TEXT EXTRACTION
# ----------------------------------

def extract_pdf_text(pdf_path):

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(
        reader.pages, start=1
    ):

        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                f"[Page {page_number}]\n{text}"
            )

    full_text = "\n\n".join(pages)

    if not full_text.strip():
        raise ValueError(
            "No extractable text found in PDF."
        )

    return full_text


# ----------------------------------
# 2. TEXT CHUNKING
# ----------------------------------

def chunk_text(
    text,
    chunk_size=180,
    overlap=35
):

    if (
        chunk_size <= 0
        or overlap < 0
        or overlap >= chunk_size
    ):
        raise ValueError(
            "Require chunk_size > overlap >= 0."
        )

    words = re.findall(r"\S+", text)

    chunks = []

    start = 0

    while start < len(words):

        end = min(
            start + chunk_size,
            len(words)
        )

        chunk = " ".join(
            words[start:end]
        ).strip()

        if chunk:
            chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks


# ----------------------------------
# 3. INGESTION PIPELINE
# ----------------------------------

def ingest(pdf_path=PDF_PATH, reset=True):

    print("\n[1/4] Extracting PDF text...")

    text = extract_pdf_text(pdf_path)

    print("[2/4] Creating text chunks...")

    chunks = chunk_text(text)

    print("Total chunks:", len(chunks))

    print("\n[3/4] Generating embeddings...")

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    print("\n[4/4] Storing in ChromaDB...")

    DB_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    client = chromadb.PersistentClient(
        path=str(DB_PATH)
    )

    if reset:

        try:
            client.delete_collection(
                COLLECTION_NAME
            )
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description":
            "Phishing URL Awareness Knowledge Base"
        }
    )

    batch_size = 100

    for offset in range(
        0, len(chunks), batch_size
    ):

        batch_chunks = chunks[
            offset:offset + batch_size
        ]

        batch_embeddings = embeddings[
            offset:offset + batch_size
        ].tolist()

        ids = [
            f"phishing-kb-{i}"
            for i in range(
                offset,
                offset + len(batch_chunks)
            )
        ]

        metadatas = [
            {
                "source": pdf_path.name,
                "chunk": offset + i
            }
            for i in range(
                len(batch_chunks)
            )
        ]

        collection.add(
            ids=ids,
            documents=batch_chunks,
            embeddings=batch_embeddings,
            metadatas=metadatas
        )

    print("\nIngestion completed successfully!")

    print(
        "Stored chunks:",
        collection.count()
    )


# ----------------------------------
# 4. EXECUTION
# ----------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--pdf",
        type=Path,
        default=PDF_PATH
    )

    parser.add_argument(
        "--append",
        action="store_true"
    )

    args = parser.parse_args()

    ingest(
        args.pdf,
        reset=not args.append
    )
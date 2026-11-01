import os
from pathlib import Path

import requests
import chromadb

from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parents[1]

DB_PATH = ROOT / "vectorstore" / "chroma"

COLLECTION_NAME = "phishing_knowledge"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


class RAGAssistant:

    def __init__(self):

        if not DB_PATH.exists():
            raise FileNotFoundError(
                "Vector database not found. "
                "Run: python -m ingestion.ingest"
            )

        self.client = chromadb.PersistentClient(
            path=str(DB_PATH)
        )

        self.collection = (
            self.client.get_collection(
                COLLECTION_NAME
            )
        )

        self.embedder = SentenceTransformer(
            EMBEDDING_MODEL
        )

    # --------------------------------
    # 1. RETRIEVE RELEVANT DOCUMENTS
    # --------------------------------

    def retrieve(self, question, top_k=4):

        if self.collection.count() == 0:
            return []

        query_embedding = self.embedder.encode(
            [question],
            normalize_embeddings=True
        )[0].tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(
                top_k,
                self.collection.count()
            ),
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = results["documents"][0]

        metadatas = results["metadatas"][0]

        distances = results["distances"][0]

        retrieved = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):

            retrieved.append({
                "text": document,
                "metadata": metadata,
                "distance": distance
            })

        return retrieved

    # --------------------------------
    # 2. GENERATE ANSWER USING OLLAMA
    # --------------------------------

    def answer(self, question, top_k=4):

        retrieved_docs = self.retrieve(
            question,
            top_k
        )

        if not retrieved_docs:

            return {
                "answer":
                "No relevant knowledge was retrieved.",
                "sources": []
            }

        context = "\n\n".join(
            f"""
            Source: {doc['metadata'].get('source')}
            Chunk: {doc['metadata'].get('chunk')}

            {doc['text']}
            """
            for doc in retrieved_docs
        )

        prompt = f"""
You are a cybersecurity educational assistant.

Answer the user's question using ONLY the
provided knowledge base context.

Rules:
1. Explain concepts in simple language.
2. Do not invent facts.
3. If information is unavailable, say so.
4. Do not declare a URL completely safe.
5. Explain the limitations of phishing indicators.
6. Do not suggest opening suspicious URLs.

KNOWLEDGE BASE CONTEXT:

{context}

USER QUESTION:

{question}

ANSWER:
"""

        ollama_host = os.getenv(
            "OLLAMA_HOST",
            "http://localhost:11434"
        )

        model_name = os.getenv(
            "OLLAMA_MODEL",
            "llama3.2"
        )

        try:

            response = requests.post(
                f"{ollama_host.rstrip('/')}/api/generate",

                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                },

                timeout=120
            )

            response.raise_for_status()

            answer_text = response.json().get(
                "response", ""
            ).strip()

            if not answer_text:
                raise RuntimeError(
                    "Ollama returned an empty response."
                )

        except requests.RequestException as error:

            answer_text = (
                "Relevant knowledge was retrieved, "
                "but Ollama could not be reached. "
                "Check whether Ollama is running. "
                f"Details: {error}"
            )

        except (ValueError, RuntimeError) as error:

            answer_text = (
                f"Answer generation failed: {error}"
            )

        sources = []

        for doc in retrieved_docs:

            sources.append({
                "source": doc["metadata"].get(
                    "source",
                    "knowledge base"
                ),

                "chunk": doc["metadata"].get(
                    "chunk",
                    "?"
                ),

                "text": doc["text"]
            })

        return {
            "answer": answer_text,
            "sources": sources
        }
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import streamlit as st

from app.detector import inspect_url


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="Phishing URL RAG Assistant",
    page_icon="🛡️",
    layout="wide"
)


# --------------------------------
# HEADER
# --------------------------------

st.title(
    "🛡️ Phishing URL Awareness System"
)

st.subheader(
    "RAG-Based Cybersecurity Assistant"
)

st.caption(
    "Intelligent URL analysis with "
    "Retrieval-Augmented Generation."
)


# --------------------------------
# SIDEBAR
# --------------------------------

with st.sidebar:

    st.header("About")

    st.write(
        """
        This application combines:

        - URL heuristic detection
        - PDF knowledge ingestion
        - Semantic search
        - ChromaDB vector storage
        - Local LLM explanations
        """
    )

    st.warning(
        "The application only inspects URL text. "
        "It never opens submitted URLs."
    )


# --------------------------------
# TABS
# --------------------------------

tab1, tab2, tab3 = st.tabs([
    "🔎 URL Checker",
    "💬 RAG Assistant",
    "ℹ️ About"
])


# =================================
# TAB 1: URL CHECKER
# =================================

with tab1:

    st.header("Phishing URL Detection")

    url = st.text_input(
        "Enter URL",
        placeholder="https://www.example.com/login"
    )

    if st.button(
        "Analyze URL",
        type="primary"
    ):

        result = inspect_url(url)

        if not result["is_valid_format"]:

            st.error(result["findings"][0])

        else:

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Warning Indicators",
                result["warning_count"]
            )

            col2.metric(
                "Heuristic Score",
                f"{result['risk_score']}/100"
            )

            col3.metric(
                "Indicator Category",
                result["risk_label"]
            )

            st.write(
                "**Hostname:**",
                result["hostname"]
            )

            st.write(
                "**Scheme:**",
                result["scheme"]
            )

            st.subheader("Detection Results")

            for finding in result["findings"]:

                if finding.startswith(
                    "No listed"
                ):

                    st.info(finding)

                else:

                    st.warning(finding)

            st.info(
                "The score is a heuristic indicator, "
                "not a probability or proof of maliciousness."
            )


# =================================
# TAB 2: RAG ASSISTANT
# =================================

with tab2:

    st.header(
        "Cybersecurity Knowledge Assistant"
    )

    st.write(
        "Ask questions about phishing, "
        "URL manipulation and security indicators."
    )

    question = st.text_area(
        "Enter your question",

        placeholder=(
            "Why is the @ symbol suspicious "
            "in a URL?"
        ),

        height=100
    )

    top_k = st.slider(
        "Number of retrieved chunks",
        min_value=1,
        max_value=8,
        value=4
    )

    if st.button(
        "Ask Knowledge Base",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            try:

                from app.rag_pipeline import (
                    RAGAssistant
                )

                with st.spinner(
                    "Retrieving knowledge..."
                ):

                    assistant = RAGAssistant()

                    result = assistant.answer(
                        question.strip(),
                        top_k=top_k
                    )

                st.subheader("Generated Answer")

                st.write(
                    result["answer"]
                )

                with st.expander(
                    "Retrieved Source Passages",
                    expanded=True
                ):

                    for index, source in enumerate(
                        result["sources"],
                        start=1
                    ):

                        st.markdown(
                            f"""
                            **Source {index}**

                            File: {source['source']}

                            Chunk: {source['chunk']}
                            """
                        )

                        st.write(
                            source["text"]
                        )

                        st.divider()

            except Exception as error:

                st.error(
                    f"RAG system error: {error}"
                )

                st.info(
                    "Run the PDF ingestion module "
                    "before using the RAG assistant."
                )


# =================================
# TAB 3: ABOUT
# =================================

with tab3:

    st.header("Project Architecture")

    st.markdown(
        """
        ### 1. URL Detection Engine

        Uses six heuristic checks to identify
        visible URL warning signs.

        ### 2. Data Ingestion

        Extracts text from cybersecurity PDF files.

        ### 3. Text Chunking

        Splits documents into smaller sections.

        ### 4. Embedding Generation

        Uses Sentence Transformers to generate
        semantic vector representations.

        ### 5. Vector Database

        Stores embeddings in ChromaDB.

        ### 6. Retrieval and Generation

        Retrieves relevant passages and uses
        Ollama to generate explanations.

        ### Limitations

        This application does not:

        - Visit URLs
        - Scan websites
        - Check live domain reputation
        - Prove that a URL is safe
        """
    )
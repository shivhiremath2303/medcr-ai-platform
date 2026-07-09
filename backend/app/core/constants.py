"""
Application-wide constants.
"""

# ----------------------------
# Supported document types
# ----------------------------
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
}

# ----------------------------
# Chunking
# ----------------------------
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ----------------------------
# Embedding model
# ----------------------------
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ----------------------------
# Vector store
# ----------------------------
FAISS_INDEX_NAME = "legal_documents"

# ----------------------------
# Search
# ----------------------------
DEFAULT_TOP_K = 3

# ----------------------------
# Retrieval
# ----------------------------
RETRIEVAL_CANDIDATE_MULTIPLIER = 4
MIN_RETRIEVAL_CANDIDATES = 20

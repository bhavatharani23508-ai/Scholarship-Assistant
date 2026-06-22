"""
rag_pipeline.py — Advanced RAG Pipeline
SentenceTransformer embeddings + FAISS vector DB + cosine similarity search.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import re


class RAGPipeline:
    """
    Complete RAG pipeline:
    - Encode chunks with SentenceTransformer
    - Store in FAISS index (cosine similarity)
    - Retrieve top-k relevant chunks
    - Memory-enhanced retrieval
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.index = None
        self.chunks: List[str] = []
        self.embeddings: Optional[np.ndarray] = None
        self.memory_queries: List[str] = []
        self.memory_limit = 5
        self._load_model()

    def _load_model(self):
        """Load SentenceTransformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model: {e}")

    def _normalize(self, vectors: np.ndarray) -> np.ndarray:
        """L2-normalize vectors for cosine similarity via inner product."""
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1e-10, norms)
        return vectors / norms

    def build_index(self, chunks: List[str]) -> Dict:
        """
        Encode all chunks and build FAISS index.

        Args:
            chunks: List of text chunks from PDF

        Returns:
            dict with index stats
        """
        try:
            import faiss
        except ImportError:
            raise ImportError(
                "faiss-cpu not installed. Run: pip install faiss-cpu"
            )

        if not chunks:
            return {"status": "error", "message": "No chunks provided"}

        self.chunks = chunks

        # Encode all chunks
        raw_embeddings = self.model.encode(
            chunks,
            batch_size=32,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        raw_embeddings = raw_embeddings.astype(np.float32)

        # Normalize for cosine similarity
        self.embeddings = self._normalize(raw_embeddings)

        # Build FAISS index (Inner Product = cosine after normalization)
        dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(self.embeddings)

        return {
            "status": "success",
            "num_chunks": len(chunks),
            "embedding_dim": dim,
            "total_embeddings": self.index.ntotal,
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        use_memory: bool = True,
        min_score: float = 0.1,
    ) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks for a query.

        Args:
            query: User question
            top_k: Number of results
            use_memory: Whether to fuse with memory queries
            min_score: Minimum similarity threshold

        Returns:
            List of dicts with chunk text and score
        """
        if self.index is None or not self.chunks:
            return []

        # Fuse query with memory for context-aware retrieval
        if use_memory and self.memory_queries:
            recent = " ".join(self.memory_queries[-2:])
            fused_query = f"{query} {recent}"
        else:
            fused_query = query

        # Encode and normalize query
        query_vec = self.model.encode([fused_query], convert_to_numpy=True)
        query_vec = query_vec.astype(np.float32)
        query_vec = self._normalize(query_vec)

        # Search FAISS index
        k = min(top_k + 2, len(self.chunks))  # retrieve extra, then filter
        scores, indices = self.index.search(query_vec, k)

        results = []
        seen_texts = set()

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            if float(score) < min_score:
                continue

            chunk_text = self.chunks[idx]

            # Deduplicate similar chunks
            chunk_key = chunk_text[:80].lower().strip()
            if chunk_key in seen_texts:
                continue
            seen_texts.add(chunk_key)

            results.append({
                "chunk": chunk_text,
                "score": float(score),
                "index": int(idx),
                "rank": len(results) + 1,
            })

            if len(results) >= top_k:
                break

        # Update memory
        self.memory_queries.append(query)
        if len(self.memory_queries) > self.memory_limit:
            self.memory_queries.pop(0)

        return results

    def keyword_search(self, keyword: str, top_n: int = 5) -> List[Dict]:
        """
        Simple keyword/regex search with highlighting.

        Args:
            keyword: Search term
            top_n: Max results

        Returns:
            List of dicts with chunk, snippet, and match count
        """
        if not self.chunks or not keyword:
            return []

        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        results = []

        for idx, chunk in enumerate(self.chunks):
            matches = pattern.findall(chunk)
            if matches:
                # Highlight matches
                highlighted = pattern.sub(
                    lambda m: f"**{m.group()}**", chunk
                )
                results.append({
                    "chunk": chunk,
                    "highlighted": highlighted,
                    "match_count": len(matches),
                    "index": idx,
                })

        # Sort by match count descending
        results.sort(key=lambda x: x["match_count"], reverse=True)
        return results[:top_n]

    def hybrid_search(
        self, query: str, keyword: str = "", top_k: int = 5
    ) -> List[Dict]:
        """
        Hybrid: semantic search with optional keyword boost.
        """
        semantic_results = self.retrieve(query, top_k=top_k)

        if not keyword:
            return semantic_results

        keyword_results = self.keyword_search(keyword, top_n=top_k)
        kw_indices = {r["index"] for r in keyword_results}

        # Boost semantic results that also have keyword matches
        for r in semantic_results:
            if r["index"] in kw_indices:
                r["score"] = min(1.0, r["score"] * 1.2)  # 20% boost
                r["keyword_match"] = True

        # Re-rank by score
        semantic_results.sort(key=lambda x: x["score"], reverse=True)
        return semantic_results[:top_k]

    def get_context(self, query: str, top_k: int = 4) -> str:
        """
        Retrieve and format context string for LLM.
        """
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return ""

        context_parts = []
        for i, r in enumerate(results):
            context_parts.append(f"[Context {i+1}]\n{r['chunk']}")

        return "\n\n".join(context_parts)

    def clear_memory(self):
        """Reset memory buffer."""
        self.memory_queries = []

    def reset(self):
        """Full reset of index and data."""
        self.index = None
        self.chunks = []
        self.embeddings = None
        self.memory_queries = []

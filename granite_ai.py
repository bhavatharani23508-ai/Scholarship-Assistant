"""
granite_ai.py — AI LLM Engine
HuggingFace FLAN-T5 + strict RAG prompt engineering + chat memory.
"""

import re
from typing import List, Dict, Optional


NOT_FOUND_RESPONSES = [
    "Not mentioned in the document.",
    "This information is not available in the provided scholarship document.",
    "The document does not contain information about this.",
]


class ScholarshipLLM:
    """
    FLAN-T5 based LLM with strict RAG prompt engineering.
    - Context-only answers (no hallucination)
    - Chat memory fusion
    - Clean response formatting
    """

    def __init__(self, model_name: str = "google/flan-t5-base", max_new_tokens: int = 300):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.model = None
        self.tokenizer = None
        self.chat_history: List[Dict[str, str]] = []
        self.max_history = 6
        self._loaded = False
        self._load_model()

    def _load_model(self):
        """Load FLAN-T5 model and tokenizer from HuggingFace."""
        try:
            from transformers import T5ForConditionalGeneration, T5Tokenizer
            import torch

            self.tokenizer = T5Tokenizer.from_pretrained(
                self.model_name, legacy=False
            )
            self.model = T5ForConditionalGeneration.from_pretrained(
                self.model_name
            )
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = self.model.to(self.device)
            self.model.eval()
            self._loaded = True

        except ImportError:
            raise ImportError(
                "transformers not installed. Run: pip install transformers"
            )
        except Exception as e:
            # Non-fatal — degrade gracefully to context-only mode
            self._loaded = False
            self._load_error = str(e)

    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build strict RAG prompt.
        Instructs model to ONLY use context, never hallucinate.
        """
        # Build a brief history summary
        history_summary = ""
        if self.chat_history:
            recent = self.chat_history[-2:]
            parts = []
            for turn in recent:
                parts.append(f"Q: {turn['user']}\nA: {turn['assistant']}")
            history_summary = (
                "Previous conversation:\n"
                + "\n".join(parts)
                + "\n\n"
            )

        prompt = (
            "You are an expert scholarship advisor AI assistant. "
            "Answer ONLY using the provided context from the scholarship document. "
            "If the answer is not in the context, say exactly: "
            "'Not mentioned in the document.' "
            "Do NOT add information from outside the context. "
            "Be concise, clear, and helpful.\n\n"
            f"{history_summary}"
            f"Context from scholarship document:\n{context}\n\n"
            f"Student Question: {query}\n\n"
            "Answer:"
        )
        return prompt

    def _clean_response(self, raw: str, query: str) -> str:
        """
        Post-process model output:
        - Remove prompt echoes
        - Remove repetition
        - Ensure non-empty response
        """
        # Remove common prompt artifacts
        raw = re.sub(r'^Answer:\s*', '', raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r'^Student Question:.*', '', raw, flags=re.IGNORECASE).strip()

        # Remove excessive newlines
        raw = re.sub(r'\n{3,}', '\n\n', raw).strip()

        # Check for empty or too-short output
        if not raw or len(raw) < 5:
            return NOT_FOUND_RESPONSES[0]

        # If the model just echoed the question
        if raw.lower().strip() == query.lower().strip():
            return NOT_FOUND_RESPONSES[0]

        # Remove repetitive sentences
        sentences = raw.split('. ')
        seen = set()
        unique_sentences = []
        for s in sentences:
            key = s.lower().strip()
            if key not in seen and key:
                seen.add(key)
                unique_sentences.append(s)
        raw = '. '.join(unique_sentences)

        return raw

    def _context_only_answer(self, query: str, context: str) -> str:
        """
        Fallback when model fails: extract answer directly from context using heuristics.
        """
        if not context:
            return NOT_FOUND_RESPONSES[0]

        query_lower = query.lower()
        context_chunks = context.split("\n\n")

        # Score chunks by keyword overlap
        query_words = set(re.findall(r'\b\w{3,}\b', query_lower))
        scored = []
        for chunk in context_chunks:
            chunk_words = set(re.findall(r'\b\w{3,}\b', chunk.lower()))
            score = len(query_words & chunk_words)
            if score > 0:
                scored.append((score, chunk))

        if not scored:
            return NOT_FOUND_RESPONSES[0]

        scored.sort(reverse=True)
        best_chunk = scored[0][1]

        # Remove context tags
        best_chunk = re.sub(r'\[Context \d+\]\n?', '', best_chunk).strip()

        # Return first 2 sentences
        sentences = re.split(r'(?<=[.!?])\s+', best_chunk)
        answer = ' '.join(sentences[:3]).strip()

        return answer if answer else NOT_FOUND_RESPONSES[0]

    def answer(self, query: str, context: str) -> str:
        """
        Main QA method. Uses FLAN-T5 if available, else falls back.

        Args:
            query: User question
            context: Retrieved context from RAG

        Returns:
            Clean answer string
        """
        if not context.strip():
            response = NOT_FOUND_RESPONSES[0]
            self._update_history(query, response)
            return response

        if not self._loaded:
            # Graceful degradation
            response = self._context_only_answer(query, context)
            self._update_history(query, response)
            return response

        try:
            import torch

            prompt = self._build_prompt(query, context)

            # Tokenize with truncation to avoid overflow
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                max_length=1024,
                truncation=True,
                padding=False,
            ).to(self.device)

            with torch.no_grad():
                output_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    num_beams=4,
                    early_stopping=True,
                    no_repeat_ngram_size=3,
                    temperature=0.7,
                    do_sample=False,
                )

            raw_answer = self.tokenizer.decode(
                output_ids[0], skip_special_tokens=True
            )
            response = self._clean_response(raw_answer, query)

        except Exception as e:
            # Fallback on any inference error
            response = self._context_only_answer(query, context)

        self._update_history(query, response)
        return response

    def _update_history(self, query: str, answer: str):
        """Maintain bounded chat history."""
        self.chat_history.append({
            "user": query,
            "assistant": answer,
        })
        if len(self.chat_history) > self.max_history:
            self.chat_history.pop(0)

    def clear_history(self):
        """Reset chat history."""
        self.chat_history = []

    def get_history(self) -> List[Dict[str, str]]:
        return list(self.chat_history)

    def is_ready(self) -> bool:
        return True  # Always ready (degrades gracefully)

    def model_status(self) -> str:
        if self._loaded:
            return f"✅ {self.model_name} loaded"
        return f"⚠️ Running in context-extraction mode (LLM unavailable)"

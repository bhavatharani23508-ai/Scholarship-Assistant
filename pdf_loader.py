"""
pdf_loader.py — PDF Intelligence System
Handles PDF upload, text extraction, noise cleaning, and smart sentence chunking.
"""

import re
import io
from typing import List, Tuple, Optional


def extract_text_from_pdf(pdf_bytes: bytes) -> Tuple[str, dict]:
    """
    Extract raw text from PDF bytes using PyMuPDF.
    Returns (full_text, metadata_dict).
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    metadata = {
        "page_count": 0,
        "word_count": 0,
        "char_count": 0,
        "file_size_kb": round(len(pdf_bytes) / 1024, 2),
        "extraction_status": "success",
        "pages_text": [],
    }

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        metadata["page_count"] = len(doc)

        all_pages_text = []
        for page_num, page in enumerate(doc):
            try:
                page_text = page.get_text("text")
                if page_text and page_text.strip():
                    all_pages_text.append(page_text)
                    metadata["pages_text"].append({
                        "page": page_num + 1,
                        "char_count": len(page_text),
                    })
            except Exception:
                # Skip corrupted pages gracefully
                continue

        doc.close()

        if not all_pages_text:
            metadata["extraction_status"] = "empty_or_scanned"
            return "", metadata

        full_text = "\n".join(all_pages_text)
        metadata["word_count"] = len(full_text.split())
        metadata["char_count"] = len(full_text)
        return full_text, metadata

    except Exception as e:
        metadata["extraction_status"] = f"error: {str(e)}"
        return "", metadata


def clean_text(raw_text: str) -> str:
    """
    Remove noise: headers, footers, excessive whitespace, page numbers, duplicates.
    """
    if not raw_text:
        return ""

    lines = raw_text.split("\n")
    cleaned_lines = []
    seen_lines = set()

    for line in lines:
        line = line.strip()

        # Skip empty lines (will handle spacing separately)
        if not line:
            continue

        # Skip standalone page numbers (e.g., "1", "Page 1", "- 1 -")
        if re.match(r'^[-–—]?\s*(page\s*)?\d+\s*[-–—]?$', line, re.IGNORECASE):
            continue

        # Skip very short lines that are likely artifacts
        if len(line) < 3:
            continue

        # Skip lines that are all special characters / borders
        if re.match(r'^[=\-_*#|~\s]{5,}$', line):
            continue

        # Deduplicate repeated lines (headers/footers)
        line_key = re.sub(r'\s+', ' ', line.lower())
        if line_key in seen_lines:
            continue
        seen_lines.add(line_key)

        cleaned_lines.append(line)

    # Join and normalize whitespace
    text = " ".join(cleaned_lines)

    # Fix multiple spaces
    text = re.sub(r' {2,}', ' ', text)

    # Fix common OCR artifacts
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # camelCase split

    # Normalize unicode quotes and dashes
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2013', '-').replace('\u2014', '-')

    return text.strip()


def sentence_chunker(
    text: str,
    chunk_size: int = 4,
    overlap: int = 1,
    min_chunk_length: int = 30,
) -> List[str]:
    """
    Sentence-based smart chunking.
    Groups N sentences per chunk with overlap for context continuity.

    Args:
        text: Clean input text
        chunk_size: Number of sentences per chunk
        overlap: Number of sentences to overlap between chunks
        min_chunk_length: Minimum character length to keep a chunk

    Returns:
        List of text chunks
    """
    if not text:
        return []

    # Split into sentences using simple regex (no spaCy dependency)
    sentence_enders = re.compile(
        r'(?<=[.!?])\s+(?=[A-Z0-9\u0900-\u097F])'
    )
    sentences = sentence_enders.split(text)

    # Filter out empty or extremely short noise fragments
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]

    if not sentences:
        # Fallback: character-based chunking
        return _char_chunker(text, chunk_size=800, overlap=100)

    chunks = []
    i = 0
    while i < len(sentences):
        window = sentences[i: i + chunk_size]
        chunk = " ".join(window).strip()
        if len(chunk) >= min_chunk_length:
            chunks.append(chunk)
        i += max(1, chunk_size - overlap)

    return chunks


def _char_chunker(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Fallback character-based chunking."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def process_pdf(pdf_bytes: bytes) -> dict:
    """
    Full pipeline: extract → clean → chunk.
    Returns a result dict with all data.
    """
    raw_text, metadata = extract_text_from_pdf(pdf_bytes)

    if not raw_text:
        return {
            "raw_text": "",
            "clean_text": "",
            "chunks": [],
            "metadata": metadata,
            "error": metadata.get("extraction_status", "Unknown extraction error"),
        }

    clean = clean_text(raw_text)
    chunks = sentence_chunker(clean, chunk_size=4, overlap=1)

    metadata["num_chunks"] = len(chunks)
    metadata["clean_word_count"] = len(clean.split())
    metadata["clean_char_count"] = len(clean)

    return {
        "raw_text": raw_text,
        "clean_text": clean,
        "chunks": chunks,
        "metadata": metadata,
        "error": None,
    }

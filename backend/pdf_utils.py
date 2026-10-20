import os
import sys
import re

def extract_text_from_pdf(pdf_path_or_file):
    """
    Robust multi-engine PDF text extractor.
    Attempts extraction using PyMuPDF (fitz), pypdf, PyPDF2, pdfplumber, and pdfminer.
    Returns cleaned text, or a meaningful fallback string if all engines fail.
    """
    if not pdf_path_or_file:
        return ""

    text = ""
    engine_used = None

    # Determine if input is file path or file-like object
    is_path = isinstance(pdf_path_or_file, str) and os.path.exists(pdf_path_or_file)

    # Engine 1: PyMuPDF (fitz) - Extremely fast and robust against broken EOF / xrefs
    if is_path:
        try:
            import fitz
            doc = fitz.open(pdf_path_or_file)
            page_texts = []
            for page in doc:
                t = page.get_text() or ""
                if t.strip():
                    page_texts.append(t)
            doc.close()
            if page_texts:
                text = "\n".join(page_texts)
                engine_used = "PyMuPDF (fitz)"
        except Exception as e:
            pass

    # Engine 2: pypdf (modern)
    if not text.strip():
        try:
            from pypdf import PdfReader
            if is_path:
                reader = PdfReader(pdf_path_or_file)
            else:
                reader = PdfReader(pdf_path_or_file)
            page_texts = []
            for page in reader.pages:
                t = page.extract_text() or ""
                if t.strip():
                    page_texts.append(t)
            if page_texts:
                text = "\n".join(page_texts)
                engine_used = "pypdf"
        except Exception:
            pass

    # Engine 3: pdfplumber
    if not text.strip() and is_path:
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path_or_file) as pdf:
                page_texts = []
                for page in pdf.pages:
                    t = page.extract_text() or ""
                    if t.strip():
                        page_texts.append(t)
                if page_texts:
                    text = "\n".join(page_texts)
                    engine_used = "pdfplumber"
        except Exception:
            pass

    # Engine 4: PyPDF2 (legacy)
    if not text.strip():
        try:
            import PyPDF2
            if is_path:
                with open(pdf_path_or_file, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    page_texts = [p.extract_text() or "" for p in reader.pages]
            else:
                reader = PyPDF2.PdfReader(pdf_path_or_file)
                page_texts = [p.extract_text() or "" for p in reader.pages]
            if any(t.strip() for t in page_texts):
                text = "\n".join(page_texts)
                engine_used = "PyPDF2"
        except Exception:
            pass

    # Engine 5: pdfminer
    if not text.strip() and is_path:
        try:
            from pdfminer.high_level import extract_text as miner_extract
            t = miner_extract(pdf_path_or_file)
            if t and t.strip():
                text = t
                engine_used = "pdfminer"
        except Exception:
            pass

    # Clean and sanitize extracted text
    cleaned = sanitize_extracted_text(text)
    if cleaned:
        # print(f"✓ PDF extracted successfully ({len(cleaned)} chars) using {engine_used}")
        return cleaned

    return "Resume content unavailable (Could not parse PDF text)."


def sanitize_extracted_text(text):
    if not text:
        return ""
    # Normalize unicode and whitespace
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    # Condense excess blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

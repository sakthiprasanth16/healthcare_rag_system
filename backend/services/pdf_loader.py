import re
import google.generativeai as genai
from pypdf import PdfReader
from backend.config import config

# Medical keywords for fast keyword-based validation
MEDICAL_KEYWORDS = [
    "diagnosis", "prescription", "patient", "dosage", "medication",
    "treatment", "symptoms", "blood", "glucose", "cholesterol",
    "hemoglobin", "report", "laboratory", "lab", "test", "result",
    "mg", "ml", "doctor", "physician", "hospital", "clinic",
    "surgery", "therapy", "vitals", "pulse", "pressure", "temperature",
    "bilirubin", "creatinine", "urea", "insulin", "vaccine", "pathology",
    "radiology", "mri", "x-ray", "ultrasound", "ecg", "ekg",
    "thyroid", "diabetes", "hypertension", "cancer", "tumor", "biopsy"
]


class PDFLoader:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.gemini = genai.GenerativeModel(config.LLM_MODEL)

    def load_pdf(self, file_path: str) -> list:
        """
        Load PDF and return list of page dicts: {page_num, text}.
        Returns empty list if extraction fails.
        """
        try:
            reader = PdfReader(file_path)
            pages = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                text = text.strip()
                if text:
                    pages.append({"page_num": i + 1, "text": text})
            return pages
        except Exception as e:
            print(f"[PDFLoader] Error loading PDF: {e}")
            return []

    def is_medical_document(self, pages: list) -> tuple[bool, str]:
        """
        Validate if the document is a medical document.
        First tries fast keyword matching, then falls back to Gemini.
        Returns (is_medical: bool, method: str).
        """
        full_text = " ".join([p["text"] for p in pages]).lower()

        # Fast keyword check
        keyword_hits = sum(1 for kw in MEDICAL_KEYWORDS if kw in full_text)
        if keyword_hits >= 3:
            return True, "keyword"

        # Gemini LLM validation fallback
        try:
            sample_text = full_text[:2000]
            prompt = (
                "Is the following document a medical document? "
                "(e.g., lab report, prescription, clinical notes, discharge summary, radiology report, pathology report) "
                "Answer ONLY 'yes' or 'no'.\n\n"
                f"Document excerpt:\n{sample_text}"
            )
            response = self.gemini.generate_content(prompt)
            answer = response.text.strip().lower()
            if "yes" in answer:
                return True, "gemini"
            return False, "gemini"
        except Exception as e:
            print(f"[PDFLoader] Gemini validation error: {e}")
            # If Gemini fails, fall back to lenient keyword check
            return keyword_hits >= 1, "keyword-fallback"

    def chunk_text(self, text: str) -> list:
        """
        Split text into overlapping chunks for embedding.
        Returns list of text chunks.
        """
        chunk_size = config.CHUNK_SIZE
        overlap = config.CHUNK_OVERLAP

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('. ')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                if break_point > chunk_size // 2:
                    chunk = text[start:start + break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        return [c for c in chunks if len(c.strip()) > 50]

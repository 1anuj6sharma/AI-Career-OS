import io
from app.core.logging import logger
from app.modules.resumes.exceptions import ResumeParsingException


class DocumentProcessor:
    """
    Extracts raw text from PDF and DOCX file bytes without external LLM calls.
    """

    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> str:
        filename_lower = filename.lower()

        if filename_lower.endswith(".pdf"):
            return DocumentProcessor._extract_pdf(file_bytes)
        elif filename_lower.endswith(".docx") or filename_lower.endswith(".doc"):
            return DocumentProcessor._extract_docx(file_bytes)
        elif filename_lower.endswith(".txt"):
            return file_bytes.decode("utf-8", errors="ignore")
        else:
            raise ResumeParsingException("Unsupported file type. Please upload a PDF or DOCX file.")

    @staticmethod
    def _extract_pdf(file_bytes: bytes) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            extracted = "\n".join(text_parts).strip()
            if not extracted:
                raise ResumeParsingException("PDF contains no selectable text.")
            return extracted
        except Exception as e:
            logger.error(f"Error parsing PDF file: {e}")
            raise ResumeParsingException(f"Error extracting text from PDF: {str(e)}")

    @staticmethod
    def _extract_docx(file_bytes: bytes) -> str:
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            text_parts = [p.text for p in doc.paragraphs if p.text]
            return "\n".join(text_parts).strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX file: {e}")
            raise ResumeParsingException(f"Error extracting text from DOCX: {str(e)}")

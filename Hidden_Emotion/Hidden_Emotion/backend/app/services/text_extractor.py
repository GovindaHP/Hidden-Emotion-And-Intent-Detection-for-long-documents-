import io
import re
import pypdf
import docx

class TextExtractor:
    @staticmethod
    def extract_text(content: bytes, filename: str) -> str:
        return TextExtractor.extract_from_bytes(content, filename)

    @staticmethod
    def extract_from_bytes(content: bytes, filename: str) -> str:
        filename_lower = filename.lower()
        
        if filename_lower.endswith(".pdf"):
            return TextExtractor.extract_from_pdf(content)
        elif filename_lower.endswith(".docx"):
            return TextExtractor.extract_from_docx(content)
        else:
            # Plain text / Markdown / Fallback UTF-8 text reader
            try:
                return content.decode("utf-8")
            except UnicodeDecodeError:
                return content.decode("latin-1", errors="replace")

    @staticmethod
    def extract_from_pdf(content: bytes) -> str:
        text = ""
        try:
            pdf_file = io.BytesIO(content)
            reader = pypdf.PdfReader(pdf_file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            text = f"Error reading PDF: {str(e)}"
        
        return TextExtractor.clean_extracted_text(text)

    @staticmethod
    def extract_from_docx(content: bytes) -> str:
        text = ""
        try:
            docx_file = io.BytesIO(content)
            doc = docx.Document(docx_file)
            for para in doc.paragraphs:
                if para.text:
                    text += para.text + "\n"
        except Exception as e:
            text = f"Error reading DOCX: {str(e)}"
            
        return TextExtractor.clean_extracted_text(text)

    @staticmethod
    def clean_extracted_text(text: str) -> str:
        # Standardize space and linebreaks
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

text_extractor = TextExtractor()

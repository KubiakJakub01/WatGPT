import os
import pypdf

def extract_text(filepath: str) -> str:
        """
        Example: parse PDF if extension=.pdf, otherwise return empty or handle other docs.
        """
        if not os.path.exists(filepath):
            return ""
        _, ext = os.path.splitext(filepath)
        ext_lower = ext.lower()

        if ext_lower == ".pdf":
            return extract_pdf_text(filepath)
        else:
            # In real code, handle .docx, .txt, etc.
            return ""

def extract_pdf_text(pdf_path: str) -> str:
        """Simple PDF text extraction using PyPDF2."""
        text = []
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    text.append(page_text)
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
        return "\n".join(text)
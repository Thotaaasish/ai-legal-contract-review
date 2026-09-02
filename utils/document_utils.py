import io
from pypdf import PdfReader
from docx import Document

def extract_text_from_file(uploaded_file) -> str:
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8")
    elif file_name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted: text += extracted + "\n"
        return text
    elif file_name.endswith(".docx"):
        doc = Document(io.BytesIO(uploaded_file.read()))
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    else:
        raise ValueError("Unsupported file format. Please upload .txt, .pdf, or .docx")

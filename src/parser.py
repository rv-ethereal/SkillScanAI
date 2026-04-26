import PyPDF2

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text content from an uploaded PDF file.
    """
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text(file_obj) -> str:
    """
    Determines file type and extracts text accordingly.
    """
    if file_obj.name.endswith('.pdf'):
        return extract_text_from_pdf(file_obj)
    else:
        # Assume it's a text file
        return file_obj.read().decode('utf-8', errors='ignore')

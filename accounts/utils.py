import PyPDF2 # type: ignore


def extract_and_save_pdf_content(handbook_id):
    # Move the import inside the function to break the circular loop
    from .models import NCCHandbook 
    
    try:
        handbook = NCCHandbook.objects.get(id=handbook_id)
        if not handbook.file:
            return "No file found."

        with handbook.file.open('rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text() + "\n"

            handbook.content_text = extracted_text
            handbook.save()
            return f"Extracted {len(extracted_text)} characters."
    except Exception as e:
        return f"Error: {str(e)}"
    

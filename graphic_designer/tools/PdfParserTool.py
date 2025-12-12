from agency_swarm.tools import BaseTool
from pydantic import Field
import fitz  # PyMuPDF
import os

class PdfParserTool(BaseTool):
    """
    Extracts text and images from PDF files using PyMuPDF.
    Handles multi-page documents and returns structured content.
    """
    file_path: str = Field(
        ..., description="Absolute path to the PDF file to parse"
    )
    
    def run(self):
        """
        Parses PDF file and extracts text and image information.
        Returns a JSON string with structured content from all pages.
        """
        # Step 1: Validate file exists
        if not os.path.exists(self.file_path):
            return f"Error: File not found at {self.file_path}"
        
        # Step 2: Open PDF document
        try:
            pdf_document = fitz.open(self.file_path)
        except Exception as e:
            return f"Error opening PDF file: {str(e)}"
        
        # Step 3: Extract content from all pages
        results = {
            'pages': [],
            'full_text': '',
            'total_images': 0,
            'metadata': {
                'filename': os.path.basename(self.file_path),
                'total_pages': pdf_document.page_count
            }
        }
        
        all_text = []
        total_images = 0
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            
            # Extract text from page
            page_text = page.get_text()
            
            # Get image count on this page
            image_list = page.get_images(full=True)
            page_image_count = len(image_list)
            total_images += page_image_count
            
            # Store page data
            results['pages'].append({
                'page_number': page_num + 1,
                'text': page_text.strip(),
                'images_count': page_image_count
            })
            
            if page_text.strip():
                all_text.append(page_text.strip())
        
        # Step 4: Combine all text
        results['full_text'] = '\n\n=== PAGE BREAK ===\n\n'.join(all_text)
        results['total_images'] = total_images
        
        # Step 5: Close document and return results
        pdf_document.close()
        
        import json
        return json.dumps(results, indent=2)

if __name__ == "__main__":
    # Test case: Create a simple test PDF
    import tempfile
    from fpdf import FPDF
    
    # Create test PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Test PDF Document", ln=True, align='C')
    pdf.cell(200, 10, txt="This is a sample paragraph for testing.", ln=True)
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        pdf.output(f.name)
        test_file = f.name
    
    tool = PdfParserTool(file_path=test_file)
    result = tool.run()
    print(result)
    
    # Cleanup
    os.unlink(test_file)

from agency_swarm.tools import BaseTool
from pydantic import Field
from fpdf import FPDF
import os
import json

class PdfSlideGeneratorTool(BaseTool):
    """
    Creates a PDF slide deck (3-10 slides) using fpdf2.
    Includes cover, mockup slides with generated images, assets list, and usage notes.
    """
    project_title: str = Field(
        ..., description="Title for the slide deck cover"
    )
    brief: str = Field(
        ..., description="Creative brief text to include on cover slide"
    )
    image_paths: list[str] = Field(
        default=[], description="List of local file paths to generated images to include"
    )
    captions: list[str] = Field(
        default=[], description="List of captions corresponding to each image"
    )
    output_dir: str = Field(
        default="./graphic_designer/files", description="Directory to save the PDF"
    )
    filename: str = Field(
        default="slide_deck.pdf", description="Output PDF filename"
    )
    
    def run(self):
        """
        Generates a PDF slide deck with cover, image mockups, and usage notes.
        Returns the path to the generated PDF.
        """
        # Step 1: Initialize PDF
        try:
            pdf = FPDF(orientation='L', unit='mm', format='A4')  # Landscape format
            pdf.set_auto_page_break(auto=False)
            
            # Step 2: Create cover slide
            pdf.add_page()
            pdf.set_fill_color(45, 55, 72)  # Dark blue-gray background
            pdf.rect(0, 0, 297, 210, 'F')
            
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 32)
            pdf.set_y(70)
            pdf.cell(0, 20, self.project_title, 0, 1, 'C')
            
            pdf.set_font('Arial', '', 12)
            pdf.set_y(100)
            pdf.multi_cell(0, 8, 'Creative Brief:', 0, 'C')
            pdf.set_y(110)
            # Wrap brief text
            brief_wrapped = self.brief[:200] + '...' if len(self.brief) > 200 else self.brief
            pdf.multi_cell(260, 8, brief_wrapped, 0, 'C')
            
            # Step 3: Create slides for each image
            for idx, img_path in enumerate(self.image_paths):
                if not os.path.exists(img_path):
                    continue
                
                pdf.add_page()
                pdf.set_fill_color(245, 245, 245)
                pdf.rect(0, 0, 297, 210, 'F')
                
                # Add slide title
                pdf.set_text_color(30, 30, 30)
                pdf.set_font('Arial', 'B', 18)
                pdf.set_y(15)
                caption = self.captions[idx] if idx < len(self.captions) else f"Variant {idx + 1}"
                pdf.cell(0, 10, caption, 0, 1, 'C')
                
                # Add image (centered)
                try:
                    # Calculate image position to center it
                    max_width = 250
                    max_height = 160
                    pdf.image(img_path, x=23, y=35, w=max_width)
                except Exception as e:
                    pdf.set_y(100)
                    pdf.set_font('Arial', '', 12)
                    pdf.cell(0, 10, f"Error loading image: {str(e)}", 0, 1, 'C')
            
            # Step 4: Create usage notes slide
            pdf.add_page()
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(0, 0, 297, 210, 'F')
            
            pdf.set_text_color(30, 30, 30)
            pdf.set_font('Arial', 'B', 24)
            pdf.set_y(30)
            pdf.cell(0, 15, 'Usage Notes & Recommendations', 0, 1, 'C')
            
            pdf.set_font('Arial', '', 11)
            pdf.set_y(60)
            pdf.set_x(30)
            
            usage_notes = [
                'Platform Recommendations:',
                '  - Square (1080x1080): Instagram feed, Facebook posts',
                '  - Landscape (1200x628): Facebook cover, LinkedIn posts, Twitter cards',
                '  - Vertical (1080x1920): Instagram Stories, Pinterest pins',
                '',
                'Best Practices:',
                '  - Post during peak engagement hours (varies by platform)',
                '  - Use consistent hashtags aligned with your brand',
                '  - A/B test different variants to optimize performance',
                '  - Include clear call-to-action in post caption',
                '',
                'File Formats:',
                '  - PNG: Best for graphics with transparency',
                '  - JPG: Smaller file size for photos',
                '  - WebP: Modern format with best compression'
            ]
            
            for note in usage_notes:
                pdf.cell(0, 7, note, 0, 1)
                pdf.set_x(30)
            
            # Step 5: Save PDF
            os.makedirs(self.output_dir, exist_ok=True)
            output_path = os.path.join(self.output_dir, self.filename)
            pdf.output(output_path)
            
            return json.dumps({
                'status': 'success',
                'pdf_path': output_path,
                'total_slides': pdf.page_no(),
                'images_included': len(self.image_paths)
            }, indent=2)
            
        except Exception as e:
            return json.dumps({
                'status': 'error',
                'message': f'Error generating PDF: {str(e)}'
            }, indent=2)

if __name__ == "__main__":
    # Test case: Generate a simple PDF deck
    tool = PdfSlideGeneratorTool(
        project_title="Social Media Campaign - Launch Graphics",
        brief="Create engaging visuals for productivity app launch targeting entrepreneurs.",
        image_paths=[],  # Would include actual image paths
        captions=["Bold Variant", "Conservative Variant", "Minimal Variant"],
        filename="test_deck.pdf"
    )
    result = tool.run()
    print(result)

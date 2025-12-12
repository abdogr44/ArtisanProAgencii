# Artisan Pro Agency

A production-grade agentic system for social media graphic creation using the Agency Swarm framework and Kie.ai APIs.

## Overview

GraphicDesigner-A1 accepts images, text prompts, DOCX/PDF documents and produces:
- 3-8 image variants per request (sizes: 1080x1080, 1200x628, 1080x1920)
- Descriptive captions and alt text
- Optional PDF slide deck exports with mockups and usage notes

## Features

- **Automated File Processing**: Validates and extracts content from DOCX/PDF uploads
- **Intelligent Prompt Generation**: Creates 3 style variants (conservative, bold, minimal)
- **Kie.ai Integration**: Text-to-image and image-to-image generation with retry logic
- **Quality Assurance**: Automated quality checks and content moderation
- **Professional Outputs**: PDF slide decks and ZIP packages with metadata
- **Audit Logging**: 30-day retention of all API interactions

## Installation

### 1. Clone and Setup

```bash
cd agency-starter-template
python -m venv venv
```

### 2. Install Dependencies

**Windows:**
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file or edit the existing one:

```env
OPENAI_API_KEY=your_openai_api_key_here
KIE_API_KEY=your_kie_api_key_here
```

## Usage

### Run Terminal Demo

```bash
python agency.py
```

### Example Request

```
User: Create Instagram graphics for a productivity app launch targeting busy entrepreneurs. 
Include bold, eye-catching designs.
```

The agent will:
1. Validate your request
2. Generate a creative brief
3. Create 3 style variant prompts
4. Generate 9 images (3 variants × 3 sizes)
5. Run quality and safety checks
6. Create a PDF slide deck
7. Package everything in a ZIP file
8. Return structured JSON output

## Architecture

### Agent Structure

- **GraphicDesigner**: Single agent with 14 specialized tools
- **Model**: gpt-5.1 with medium reasoning
- **No complex communication flows**: Optimized for efficiency

### Tools (14 Total)

**File Processing (4)**
- `FileValidatorTool`: Validate uploads (200MB limit)
- `DocxParserTool`: Extract DOCX content
- `PdfParserTool`: Extract PDF content
- `BriefGeneratorTool`: Synthesize creative briefs

**Kie.ai Integration (4)**
- `KieImageGenerateTool`: Text→image generation
- `KieImageEditTool`: Image→image editing
- `KieImageStatusTool`: Poll generation status
- `PromptSynthesizerTool`: Create style variants

**Output Generation (4)**
- `ImagePostProcessorTool`: Convert formats, upscale
- `PdfSlideGeneratorTool`: Create presentation decks
- `ZipExportTool`: Package assets
- `OutputFormatterTool`: Format JSON output

**Quality & Safety (3)**
- `ContentModerationTool`: Basic safety checks
- `QualityCheckerTool`: Validate image quality
- `AuditLoggerTool`: Log API interactions

## Output Format

```json
{
  "request_id": "uuid-v4",
  "status": "done",
  "brief": "Generated creative brief",
  "images": [
    {
      "id": "img1",
      "size": "1080x1080",
      "variant": "bold",
      "prompt": "...",
      "url": "https://.../img1.png",
      "meta": {"seed": 12345, "steps": 28}
    }
  ],
  "caption": "Short caption (≤150 chars)",
  "slides_pdf": "./files/deck.pdf",
  "zipped_assets": "./files/assets.zip",
  "metadata": {
    "brand": "",
    "style": "",
    "iterations": 1
  }
}
```

## Safety & Limits

- **File Size**: 200MB total upload limit
- **Rate Limiting**: 4 concurrent Kie.ai requests, 60s timeout
- **Audit Logs**: 30-day retention in `./graphic_designer/files/audit_logs/`
- **Content Safety**: Basic heuristic moderation (integrate dedicated APIs for production)
- **No Destructive Operations**: System files and secrets protected

## Testing

Individual tool tests:

```bash
python graphic_designer/tools/FileValidatorTool.py
python graphic_designer/tools/BriefGeneratorTool.py
python graphic_designer/tools/PromptSynthesizerTool.py
```

## Project Structure

```
agency-starter-template/
├── graphic_designer/
│   ├── __init__.py
│   ├── graphic_designer.py
│   ├── instructions.md
│   ├── files/                    # Generated outputs
│   └── tools/                    # 14 production tools
│       ├── FileValidatorTool.py
│       ├── DocxParserTool.py
│       ├── KieImageGenerateTool.py
│       └── ... (11 more)
├── agency.py                     # Main entry point
├── shared_instructions.md
├── requirements.txt
└── .env                          # API keys (gitignored)
```

## Customization

### Adjust Rate Limits

Edit tool files to modify concurrency and timeouts.

### Add Custom Styles

Modify `PromptSynthesizerTool.py` to add style variants.

### Change Output Sizes

Update size specifications in agent instructions.

## Troubleshooting

**"KIE_API_KEY not found"**
- Ensure `.env` file exists with valid `KIE_API_KEY`

**Virtual environment activation error**
- Windows: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**Tool import errors**
- Run `pip install -r requirements.txt` again

## License

See project license file.

## Support

For issues or questions, refer to the Agency Swarm documentation: https://agency-swarm.ai/

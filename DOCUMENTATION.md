# Artisan Pro Agency - Complete Documentation

**Version**: 2.0.0  
**Last Updated**: December 8, 2025  
**Framework**: Agency Swarm  
**AI Model**: GPT-4.5 with medium reasoning

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Agents](#agents)
4. [Tools Reference](#tools-reference)
5. [Workflows](#workflows)
6. [Expert Brand Identity Knowledge Pack](#expert-brand-identity-knowledge-pack)
7. [Installation & Setup](#installation--setup)
8. [Usage Guide](#usage-guide)
9. [API Reference](#api-reference)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)

---

## Overview

Artisan Pro Agency is a production-grade agentic system for creating professional social media graphics and brand identity assets using AI. It combines the Agency Swarm framework with Kie.ai's image generation APIs to deliver high-quality visual content.

### Key Features

- **Dual-Mode Operation**: Production Mode (fast social media content) + Strategy Mode (expert brand identity)
- **Automated Workflow**: From brief to final deliverables with quality assurance
- **Expert Knowledge Integration**: 3 domains of brand identity expertise (brand strategy, color psychology, typography)
- **Professional Outputs**: Multi-format images, PDF slide decks, ZIP packages
- **Quality Assurance**: Automated checks and human-in-the-loop review
- **Audit Trail**: 30-day retention of all API interactions

### What It Produces

**Per Request**:
- 3-9 image variants (conservative, bold, minimal styles)
- 3 sizes: 1080x1080 (Instagram), 1200x628 (Facebook), 1080x1920 (Stories)
- Descriptive captions and alt text
- PDF slide deck with mockups and usage notes
- ZIP archive with all assets
- Structured JSON metadata

---

## Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Artisan Pro Agency                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │ GraphicDesigner  │────────▶│    Reviewer      │         │
│  │     (A1)         │         │                  │         │
│  │                  │         │  Quality Gates   │         │
│  │  • 15 Tools      │         │  Final Approval  │         │
│  │  • Dual-Mode     │         │                  │         │
│  │  • Knowledge     │         │                  │         │
│  └──────────────────┘         └──────────────────┘         │
│           │                            │                    │
│           ▼                            ▼                    │
│  ┌─────────────────────────────────────────────┐           │
│  │         External Services                    │           │
│  │  • Kie.ai API (Image Generation)            │           │
│  │  • OpenAI API (Agent Reasoning)             │           │
│  └─────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Communication Flow

```
User Request
    ↓
GraphicDesigner-A1
    ├─ File Processing (validate, extract, brief)
    ├─ Prompt Generation (3 variants)
    ├─ Image Generation (Kie.ai API)
    ├─ Quality Checks (resolution, format, safety)
    ├─ Post-Processing (upscale, convert)
    └─ Output Generation (PDF, ZIP, JSON)
    ↓
Reviewer
    ├─ Completeness Check
    ├─ Brief Alignment
    ├─ Technical Quality
    └─ Final Approval Request
    ↓
User Delivery
```

### Operating Modes

#### Production Mode (Default)
- **Speed**: Fast execution (minutes)
- **Use Case**: Social media content, quick graphics
- **Knowledge Pack**: Not used
- **Triggers**: "social media", "Instagram", "quick", "fast", "content"

#### Strategy Mode (Knowledge-Enhanced)
- **Speed**: Strategic analysis (slower)
- **Use Case**: Brand identity, strategic design
- **Knowledge Pack**: Actively queried
- **Triggers**: "brand identity", "brand strategy", "positioning", "differentiation"

---

## Agents

### GraphicDesigner-A1 (Entry Agent)

**Role**: Certified Expert Brand Identity Designer & Social Media Content Creator

**Capabilities**:
- Dual-mode operation (Production + Strategy)
- 15 specialized tools
- Expert brand identity knowledge
- Kie.ai API integration
- Quality assurance

**Certification**:
- **Level**: Expert
- **Title**: Brand Identity Design Professional — 2025
- **Competencies**: Brand Strategy, Color Psychology, Typography, Prompt Engineering
- **Equivalent Experience**: 5+ years at Pentagram/Landor/Wolff Olins level

**Tools** (15 total):

**File Processing (4)**:
1. `FileValidatorTool` - Validate uploads (200MB limit)
2. `DocxParserTool` - Extract DOCX content
3. `PdfParserTool` - Extract PDF content
4. `BriefGeneratorTool` - Synthesize creative briefs (with strategic analysis)

**Knowledge & Strategy (1)**:
5. `BrandIdentityKnowledgeTool` - Query expert brand knowledge

**Prompt Generation (1)**:
6. `PromptSynthesizerTool` - Create style variants (with brand knowledge integration)

**Kie.ai Integration (3)**:
7. `KieImageGenerateTool` - Text→image generation
8. `KieImageEditTool` - Image→image editing
9. `KieImageStatusTool` - Poll generation status

**Output Generation (4)**:
10. `ImagePostProcessorTool` - Convert formats, upscale
11. `PdfSlideGeneratorTool` - Create presentation decks
12. `ZipExportTool` - Package assets
13. `OutputFormatterTool` - Format JSON output

**Quality & Safety (2)**:
14. `ContentModerationTool` - Basic safety checks
15. `QualityCheckerTool` - Validate image quality
16. `AuditLoggerTool` - Log API interactions

---

### Reviewer (Quality Assurance Agent)

**Role**: Quality assurance specialist who validates GraphicDesigner outputs

**Responsibilities**:
- Completeness verification (all images generated)
- Format validation (correct sizes and formats)
- Brief alignment (matches user requirements)
- Technical quality checks (resolution, quality standards)
- Deliverable status (PDF and ZIP generated)

**Communication Rules**:
- **Always** request final approval before delivery
- Report issues concisely (1-2 sentences)
- Provide specific recommendations
- Never approve automatically

**Tools**: No tools (review only)

---

## Tools Reference

### File Processing Tools

#### FileValidatorTool
**Purpose**: Validate uploaded files before processing

**Inputs**:
- `file_path` (str): Path to file to validate

**Outputs**:
- `status`: "valid" or "invalid"
- `file_type`: Detected file type
- `file_size_mb`: File size in MB
- `issues`: List of validation issues

**Limits**:
- Max file size: 200MB
- Supported formats: DOCX, PDF, PNG, JPG, WebP

---

#### DocxParserTool
**Purpose**: Extract text content from DOCX files

**Inputs**:
- `file_path` (str): Path to DOCX file

**Outputs**:
- `extracted_text` (str): Extracted text content
- `word_count` (int): Number of words

---

#### PdfParserTool
**Purpose**: Extract text content from PDF files

**Inputs**:
- `file_path` (str): Path to PDF file

**Outputs**:
- `extracted_text` (str): Extracted text content
- `page_count` (int): Number of pages

---

#### BriefGeneratorTool
**Purpose**: Synthesize creative briefs from user input

**Inputs**:
- `extracted_text` (str): Text to synthesize
- `user_prompt` (str, optional): Additional context
- `include_strategic_analysis` (bool): Enable Strategy Mode

**Outputs**:
- `brief` (str): Generated creative brief
- `strategic_analysis` (dict, optional): Strategic questions and recommendations

**Strategy Mode Features**:
- Strategic questions (What problem? What emotion? What differentiates?)
- Recommended approach
- Behavioral standards

---

### Knowledge & Strategy Tools

#### BrandIdentityKnowledgeTool
**Purpose**: Query expert brand identity knowledge

**Inputs**:
- `domain` (str): Knowledge domain to query
  - `brand_strategy`: Strategic frameworks and principles
  - `color_theory`: Color psychology and palette architecture
  - `typography`: Typography systems and selection
  - `evaluation_criteria`: Quality scoring frameworks
  - `case_studies`: Real-world brand identity examples
- `query` (str, optional): Specific query within domain

**Outputs**:
- Formatted expert knowledge (markdown)

**Example Queries**:
```python
# Get brand strategy overview
tool = BrandIdentityKnowledgeTool(domain="brand_strategy")

# Get emotional color mapping
tool = BrandIdentityKnowledgeTool(
    domain="color_theory", 
    query="emotional_color_mapping"
)

# Get typography pairing rules
tool = BrandIdentityKnowledgeTool(
    domain="typography", 
    query="pairing_rules"
)
```

---

### Prompt Generation Tools

#### PromptSynthesizerTool
**Purpose**: Generate style variant prompts for image generation

**Inputs**:
- `brief` (str): Creative brief
- `tone` (str): Desired tone (e.g., "professional", "playful")
- `platform` (str): Target platform ("instagram", "facebook", "linkedin")
- `use_brand_knowledge` (bool): Enable Strategy Mode
- `brand_personality` (str, optional): Brand personality type

**Outputs**:
- `conservative` (dict): Conservative style prompt
- `bold` (dict): Bold style prompt
- `minimal` (dict): Minimal style prompt
- `metadata` (dict): Brand knowledge application status

**Strategy Mode Features**:
- Strategic color guidance based on brand personality
  - Luxury → Black, gold, deep emerald, burgundy
  - Tech → Electric blue, neon purple, holographic gradients
  - Wellness → Sage green, mint, lavender, soft pink
  - Creative → Purple, magenta, vibrant pink, coral
- Typography guidance (serif for luxury, sans for tech, etc.)

**Example**:
```python
# Production Mode
tool = PromptSynthesizerTool(
    brief="Create Instagram graphics for tech startup",
    tone="professional",
    platform="instagram",
    use_brand_knowledge=False
)

# Strategy Mode
tool = PromptSynthesizerTool(
    brief="Create brand identity for luxury wellness startup",
    tone="sophisticated",
    platform="instagram",
    use_brand_knowledge=True,
    brand_personality="luxury wellness"
)
```

---

### Kie.ai Integration Tools

#### KieImageGenerateTool
**Purpose**: Generate images from text prompts using Kie.ai API

**Inputs**:
- `prompt` (str): Image generation prompt
- `size` (str): Image size ("1080x1080", "1200x628", "1080x1920")
- `style` (str, optional): Style preset

**Outputs**:
- `task_id` (str): Kie.ai task ID
- `status` (str): Generation status
- `image_url` (str): Generated image URL (when complete)

**Rate Limits**:
- 4 concurrent requests
- 60s timeout per request

---

#### KieImageEditTool
**Purpose**: Edit existing images using Kie.ai API

**Inputs**:
- `image_path` (str): Path to source image
- `edit_prompt` (str): Edit instructions
- `strength` (float): Edit strength (0.0-1.0)

**Outputs**:
- `task_id` (str): Kie.ai task ID
- `edited_image_url` (str): Edited image URL

---

#### KieImageStatusTool
**Purpose**: Poll Kie.ai task status

**Inputs**:
- `task_id` (str): Kie.ai task ID

**Outputs**:
- `status` (str): "pending", "processing", "completed", "failed"
- `image_url` (str, optional): Image URL when completed

---

### Output Generation Tools

#### ImagePostProcessorTool
**Purpose**: Convert formats and upscale images

**Inputs**:
- `image_path` (str): Path to image
- `output_format` (str): Target format ("png", "jpg", "webp")
- `upscale_factor` (float, optional): Upscale multiplier

**Outputs**:
- `processed_image_path` (str): Path to processed image

---

#### PdfSlideGeneratorTool
**Purpose**: Create PDF presentation decks

**Inputs**:
- `images` (list): List of image paths
- `brief` (str): Creative brief
- `output_path` (str): PDF output path

**Outputs**:
- `pdf_path` (str): Path to generated PDF

---

#### ZipExportTool
**Purpose**: Package assets into ZIP archive

**Inputs**:
- `file_paths` (list): List of files to include
- `output_path` (str): ZIP output path

**Outputs**:
- `zip_path` (str): Path to ZIP archive

---

#### OutputFormatterTool
**Purpose**: Format final JSON output

**Inputs**:
- `images` (list): Generated images
- `brief` (str): Creative brief
- `metadata` (dict): Additional metadata

**Outputs**:
- Structured JSON output

---

### Quality & Safety Tools

#### ContentModerationTool
**Purpose**: Basic safety checks on prompts and content

**Inputs**:
- `text` (str): Text to moderate

**Outputs**:
- `safe` (bool): Safety status
- `issues` (list): Detected issues

---

#### QualityCheckerTool
**Purpose**: Validate image quality

**Inputs**:
- `image_path` (str): Path to image
- `min_width` (int): Minimum width (default: 800)
- `min_height` (int): Minimum height (default: 800)

**Outputs**:
- `quality` (str): "pass", "warning", "fail"
- `needs_regeneration` (bool): Regeneration required
- `checks` (dict): Individual check results
- `issues` (list): Detected issues

---

#### AuditLoggerTool
**Purpose**: Log API interactions for audit trail

**Inputs**:
- `event_type` (str): Event type
- `data` (dict): Event data

**Outputs**:
- `log_path` (str): Path to log file

**Retention**: 30 days

---

## Workflows

### Production Mode Workflow (Social Media Content)

```
User Request: "Create Instagram posts for coffee shop promotion"
    ↓
1. FileValidatorTool (if files uploaded)
    ↓
2. BriefGeneratorTool (standard mode)
   Output: "Create engaging social media graphics..."
    ↓
3. PromptSynthesizerTool (use_brand_knowledge=False)
   Output: 3 variants with generic color guidance
    ↓
4. KieImageGenerateTool (9 images: 3 variants × 3 sizes)
    ↓
5. QualityCheckerTool (validate all images)
    ↓
6. PdfSlideGeneratorTool + ZipExportTool
    ↓
7. Reviewer (final approval)
    ↓
User Delivery (minutes)
```

---

### Strategy Mode Workflow (Brand Identity)

```
User Request: "Develop brand identity for luxury wellness startup"
    ↓
1. BriefGeneratorTool (include_strategic_analysis=True)
   Output: Brief + Strategic Questions
    ↓
2. BrandIdentityKnowledgeTool (query brand_strategy)
   Output: Strategic pillars, frameworks
    ↓
3. BrandIdentityKnowledgeTool (query color_theory)
   Output: Emotional color mapping
    ↓
4. BrandIdentityKnowledgeTool (query typography)
   Output: Strategic typeface selection
    ↓
5. PromptSynthesizerTool (use_brand_knowledge=True, brand_personality="luxury wellness")
   Output: 3 variants with strategic color/typography guidance
   Example: "Refined Black, gold, deep emerald, or burgundy tones (luxury palette)"
    ↓
6. KieImageGenerateTool (9 images with strategic prompts)
    ↓
7. QualityCheckerTool (validate all images)
    ↓
8. PdfSlideGeneratorTool + ZipExportTool
    ↓
9. Reviewer (final approval)
    ↓
User Delivery (strategic, thoughtful)
```

---

## Expert Brand Identity Knowledge Pack

### Overview

The Knowledge Pack transforms GraphicDesigner-A1 into a certified expert brand strategist with 3 comprehensive knowledge domains.

### Knowledge Domains

#### 1. Brand Strategy Foundations

**Strategic Pillars** (7):
1. **Core Truth**: Non-negotiable brand belief
2. **Positioning**: Space in the mind, not the market
3. **Audience Archetypes**: Psychological profiles (12 types)
4. **Value Ladder**: Functional → Emotional → Social → Self-expressive
5. **Brand Personality Matrix**: 6-axis sliding scale
6. **Brand Narrative Framework**: Conflict → Insight → Resolution → Transformation
7. **Differentiation Law**: "If it feels safe, it's already similar"

**Strategic Questions**:
- What problem is this brand solving?
- What emotion should the audience feel?
- What differentiates this identity from competitors?
- What archetype does the audience identify with?
- What level of the value ladder does this brand operate on?

**Behavioral Standards**:
- Always ask strategic questions before designing
- Always justify design decisions with strategic reasoning
- Always follow: Strategy → Concept → Execution
- Never generate generic designs
- Always validate differentiation vs. competitors

---

#### 2. Color Psychology & Systems

**Palette Architecture**:
- **Primary** (1 color): Identity anchor, signature color
- **Secondary** (2-3 colors): Flexibility and depth
- **Accent** (1 color): Call-to-action energy
- **Neutral** (1-2 colors): Typography and backgrounds

**Emotional Color Mapping** (8 categories):
- **Trust**: Blue, Navy, Teal → Finance, Healthcare, Tech
- **Innovation**: Electric Blue, Neon Purple, Holographic → Tech startups, AI/ML
- **Luxury**: Black, Gold, Deep Emerald, Burgundy → Fashion, Jewelry, Hospitality
- **Wellness**: Sage, Mint, Lavender, Soft Pink → Health, Spa, Yoga
- **Urgency/Action**: Red, Orange, Bright Yellow → Food delivery, Sales, Sports
- **Creativity**: Purple, Magenta, Vibrant Pink, Coral → Design, Arts, Agencies
- **Nature/Sustainability**: Green, Forest, Earth tones → Sustainability, Agriculture
- **Energy/Youth**: Bright Yellow, Orange, Vibrant Pink, Lime → Youth brands, Social media

**Rules**:
- Each palette MUST include: 1 primary + 2-3 secondary + 1 accent + 1 neutral
- Minimum WCAG 4.5:1 contrast ratio for body text
- Every color must map to a brand personality attribute
- Signature color should be defensible and distinct from competitors

---

#### 3. Typography Systems

**Three-Tier Hierarchy**:
1. **Primary Typeface**: Personality carrier (headlines, brand moments)
2. **Secondary Typeface**: Utility workhorse (body text, UI elements)
3. **Display Typeface**: Emotional punch (optional, special moments)

**Strategic Typeface Selection**:
- **Luxury**: Serif, Transitional, Didone (Playfair Display, Bodoni, Didot)
- **Tech**: Grotesk, Geometric Sans (Inter, Helvetica Neue, Futura)
- **Human-Centric**: Rounded Sans, Humanist Sans (Nunito, Quicksand, Montserrat)
- **Corporate**: Neo-Grotesk (Helvetica, Univers, Akzidenz-Grotesk)
- **Creative/Fashion**: Brutalist, High-contrast Serif, Display (Druk, GT Super, Canela)

**Pairing Rules**:
- **Serif + Sans**: Professional, editorial, balanced (Playfair + Inter)
- **Grotesk + Geometric**: Modern, corporate, clean (Helvetica + Futura)
- **Display + Sans**: Bold, youthful, energetic (Druk + Inter)

**Rules**:
- Maximum 2 font families per brand system (3 only if display is essential)
- Primary typeface must align with brand personality matrix
- Pairing must create contrast, not conflict

---

### Case Studies

**Included Examples** (3):
1. **Luxury Tech Startup**: Premium positioning in tech market
2. **Holistic Wellness Platform**: Scientific credibility + human warmth
3. **Bold Creative Agency**: Boldness + professional credibility

**Anti-Patterns** (3 common mistakes to avoid)

---

### Evaluation Criteria

#### Prompt Quality Score (100 points, 80% threshold)
- Brand tone (20 pts)
- Industry context (20 pts)
- Format/platform (20 pts)
- Visual language keywords (20 pts)
- Constraints (20 pts)

#### Strategic Alignment Score (100 points, 80% threshold)
- Queries knowledge pack (25 pts)
- Justifies decisions (25 pts)
- Applies principles (25 pts)
- Maintains consistency (25 pts)

---

## Installation & Setup

### Prerequisites

- Python 3.8+
- OpenAI API key
- Kie.ai API key

### Installation Steps

1. **Clone Repository**:
```bash
git clone https://github.com/abdogr44/agency-starter-template.git
cd agency-starter-template
```

2. **Create Virtual Environment**:
```bash
python -m venv venv
```

3. **Activate Virtual Environment**:

**Windows**:
```powershell
.\venv\Scripts\activate
```

**Mac/Linux**:
```bash
source venv/bin/activate
```

4. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

5. **Configure Environment**:

Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
KIE_API_KEY=your_kie_api_key_here
```

6. **Verify Installation**:
```bash
python agency.py
```

---

## Usage Guide

### Running the Agency

**Terminal Demo**:
```bash
python agency.py
```

**Programmatic Usage**:
```python
from agency import create_agency

agency = create_agency()
response = agency.get_response("Create Instagram graphics for tech startup")
print(response)
```

---

### Example Requests

#### Production Mode (Social Media)

```
User: Create Instagram posts for a coffee shop promotion. 
Use warm, inviting colors and include 3 variants.
```

**Expected Behavior**:
- Detects "Instagram" → Production Mode
- Generates brief quickly
- Creates 3 variants with generic color guidance
- Produces 9 images (3 variants × 3 sizes)
- Delivers in minutes

---

#### Strategy Mode (Brand Identity)

```
User: Develop a brand identity for a luxury wellness startup called 'Serenity Labs'. 
Target audience: Busy professionals (30-50) seeking premium self-care.
Brand positioning: Against generic wellness apps, we are the personalized, 
science-backed choice for discerning professionals.
```

**Expected Behavior**:
- Detects "brand identity" + "luxury" → Strategy Mode
- Queries BrandIdentityKnowledgeTool for brand strategy
- Generates brief with strategic analysis
- Asks strategic questions:
  - What problem is this brand solving?
  - What emotion should the audience feel?
  - What differentiates this from competitors?
- Creates prompts with strategic color guidance:
  - Luxury palette: Black, gold, deep emerald, burgundy
  - Wellness palette: Sage green, mint, lavender, soft pink
- Applies typography guidance: Elegant serif (transitional/didone)
- Justifies design decisions with strategic reasoning

---

### Output Structure

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
    "iterations": 1,
    "brand_knowledge_applied": true,
    "brand_personality": "luxury wellness"
  }
}
```

---

## API Reference

### Agency API

#### `create_agency(load_threads_callback=None)`

Creates and returns an Agency instance.

**Parameters**:
- `load_threads_callback` (callable, optional): Callback for loading threads

**Returns**:
- `Agency`: Configured agency instance

**Example**:
```python
from agency import create_agency

agency = create_agency()
```

---

#### `agency.get_response(message)`

Get response from agency (async).

**Parameters**:
- `message` (str): User message/request

**Returns**:
- `str`: Agency response

**Example**:
```python
import asyncio

async def main():
    agency = create_agency()
    response = await agency.get_response("Create Instagram graphics")
    print(response)

asyncio.run(main())
```

---

#### `agency.terminal_demo()`

Run interactive terminal demo.

**Example**:
```python
agency = create_agency()
agency.terminal_demo()
```

---

## Testing

### Unit Tests

Test individual tools:

```bash
# Test file validation
python graphic_designer/tools/FileValidatorTool.py

# Test brief generation
python graphic_designer/tools/BriefGeneratorTool.py

# Test prompt synthesis
python graphic_designer/tools/PromptSynthesizerTool.py

# Test brand knowledge
python graphic_designer/tools/BrandIdentityKnowledgeTool.py
```

---

### Integration Tests

Test knowledge pack integration:

```bash
# Test all knowledge pack features
python test_knowledge_pack.py

# Test end-to-end Strategy Mode
python test_strategy_mode_e2e.py
```

**Expected Results**:
- All tests should pass (6/6)
- Strategy Mode should apply brand knowledge
- Production Mode should work without knowledge overhead

---

### Full Agency Test

Test complete workflow:

```bash
python test_agency.py
```

---

## Troubleshooting

### Common Issues

#### "KIE_API_KEY not found"
**Solution**: Ensure `.env` file exists with valid `KIE_API_KEY`

```env
KIE_API_KEY=your_kie_api_key_here
```

---

#### Virtual Environment Activation Error (Windows)
**Solution**: Run PowerShell as Administrator:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

#### Tool Import Errors
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt
```

---

#### Kie.ai API Timeout
**Solution**: Check rate limits and retry:
- Max 4 concurrent requests
- 60s timeout per request
- Automatic retry logic included

---

#### Unicode Encoding Error (Windows Console)
**Solution**: Already handled in test files with:
```python
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

---

## Project Structure

```
agency-starter-template/
├── .agent/
│   └── workflows/
│       └── brand-knowledge-implementation.md
├── graphic_designer/
│   ├── __init__.py
│   ├── graphic_designer.py
│   ├── instructions.md              # Agent instructions (dual-mode)
│   ├── files/                        # Generated outputs
│   │   ├── audit_logs/              # 30-day retention
│   │   ├── images/
│   │   ├── pdfs/
│   │   └── zips/
│   ├── knowledge/                    # Expert knowledge pack
│   │   ├── brand_knowledge_pack.json
│   │   ├── certification/
│   │   │   └── metadata.json
│   │   └── examples/
│   │       └── case_studies.json
│   └── tools/                        # 15 production tools
│       ├── FileValidatorTool.py
│       ├── DocxParserTool.py
│       ├── PdfParserTool.py
│       ├── BriefGeneratorTool.py
│       ├── BrandIdentityKnowledgeTool.py
│       ├── PromptSynthesizerTool.py
│       ├── KieImageGenerateTool.py
│       ├── KieImageEditTool.py
│       ├── KieImageStatusTool.py
│       ├── ImagePostProcessorTool.py
│       ├── PdfSlideGeneratorTool.py
│       ├── ZipExportTool.py
│       ├── OutputFormatterTool.py
│       ├── ContentModerationTool.py
│       ├── QualityCheckerTool.py
│       └── AuditLoggerTool.py
├── reviewer/
│   ├── __init__.py
│   ├── reviewer.py
│   └── instructions.md              # Reviewer instructions
├── agency.py                         # Main entry point
├── main.py                           # Alternative entry
├── shared_instructions.md
├── requirements.txt
├── .env                              # API keys (gitignored)
├── .env.template                     # Template for .env
├── README.md                         # Quick start guide
├── DOCUMENTATION.md                  # This file
├── test_knowledge_pack.py            # Knowledge pack tests
├── test_strategy_mode_e2e.py         # End-to-end tests
└── test_agency.py                    # Full agency tests
```

---

## Performance Metrics

### Production Mode
- **Speed**: 2-5 minutes per request
- **Images**: 9 images (3 variants × 3 sizes)
- **Knowledge Queries**: 0 (no overhead)

### Strategy Mode
- **Speed**: 5-10 minutes per request
- **Images**: 9 images (3 variants × 3 sizes)
- **Knowledge Queries**: 3-5 (brand strategy, color theory, typography)
- **Strategic Analysis**: Included in brief

---

## Safety & Limits

- **File Size**: 200MB total upload limit
- **Rate Limiting**: 4 concurrent Kie.ai requests, 60s timeout
- **Audit Logs**: 30-day retention in `./graphic_designer/files/audit_logs/`
- **Content Safety**: Basic heuristic moderation (integrate dedicated APIs for production)
- **No Destructive Operations**: System files and secrets protected

---

## License

See project license file.

---

## Support

For issues or questions:
- **Agency Swarm Documentation**: https://agency-swarm.ai/
- **GitHub Repository**: https://github.com/abdogr44/agency-starter-template
- **Kie.ai API Docs**: See `kie.ai-api-nanobanana-pro.md`

---

## Changelog

### Version 2.0.0 (December 8, 2025)
- ✅ Added Expert Brand Identity Knowledge Pack (3 domains)
- ✅ Implemented dual-mode architecture (Production + Strategy)
- ✅ Built BrandIdentityKnowledgeTool
- ✅ Enhanced PromptSynthesizerTool with brand knowledge integration
- ✅ Enhanced BriefGeneratorTool with strategic analysis
- ✅ Updated agent instructions for dual-mode workflow
- ✅ Added certification metadata and case studies
- ✅ All tests passing (6/6 end-to-end validation)

### Version 1.0.0 (Previous)
- Initial release with 14 tools
- Kie.ai API integration
- Basic workflow implementation

---

**Documentation Version**: 2.0.0  
**Last Updated**: December 8, 2025  
**Maintained By**: Artisan Pro Agency Team

- **Marketing Agencies**: Need scalable visual content production for multiple clients

## Operational Environment

- **Image Generation**: Powered by Kie.ai APIs for text-to-image and image-to-image generation
- **Quality Standards**: Automated quality checks and content moderation ensure professional outputs
- **Safety Controls**: Rate limiting (4 concurrent requests, 60s timeout), audit logging (30-day retention), and content safety checks
- **Output Formats**: Standard social media sizes (1080x1080, 1200x628, 1080x1920) with JPG/PNG/WebP support
- **File Processing**: Supports DOCX and PDF parsing to extract creative briefs and imagery, with 200MB total upload limit

## Design Philosophy

- **Rapid Iteration**: Generate 3 style variants (conservative, bold, minimal) per request with up to 3 regeneration passes for quality
- **Minimal Human Intervention**: Automated workflow from intake to delivery with optional clarification (1 question maximum)
- **Composable Tools**: Atomic, single-purpose tools that agents orchestrate into complete workflows
- **Audit Transparency**: Complete logging of prompts, API calls, and outputs for compliance and optimization

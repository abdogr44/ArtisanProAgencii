# Athar Publishing Pipeline (Artisan Pro)

A secure, production-grade agentic system for the end-to-end publishing of Athar books. This pipeline orchestrates manuscript ingestion, editing, proofreading, formatting, and multi-format release packaging.

## Overview

The Athar Publishing Pipeline transforms raw manuscripts (DOCX/PDF) into production-ready artifacts (PDF, EPUB, Reader Bundles) through a rigorous, gated workflow. It emphasizes data integrity, security, and quality assurance.

## Key Features

- **Automated Ingestion**: Parsing of DOCX/PDF files with hierarchy detection and confidence scoring.
- **Gated Workflow**: Strict quality gates (Pass 1, Pass 2, Final) requiring crypto-bound sign-offs.
- **Security**: 
    - Full separation of private (master) and public (sample) artifacts.
    - Input hash binding ensures approvals are invalidated if content changes.
    - PII/sensitive data scanning for public bundles.
- **Multi-Format Export**: Generates print-ready PDFs, EPUBs, and JSON bundles for the Athar Reader App.
- **Storage Abstraction**: 
    - `storage_backends` supports Local FS (Development) and Google Cloud Storage (Production).
    - Downloads files securely to private storage before pipeline processing.
- **Firebase Integration**: Automated deployment of public reader bundles to Firebase Hosting.

## Architecture

The system is built on the **Agency Swarm** framework, led by a central orchestrator:

| Agent | Responsibilities | Key Tools |
|-------|------------------|-----------|
| **PublishingOrchestrator** | Pipeline management, gate enforcement, routing | `GateEnforcementTool`, `PipelineStatusTool`, `ProjectFileIngestTool` |
| **ManuscriptIntake** | Ingestion, parsing, canonicalization | `ManuscriptCompilerTool` |
| **StyleEditor** | Stylistic analysis and suggestions | `StyleSuggestionTool` |
| **Proofreader** | Grammar/spelling (Pass 1) & formatting (Pass 2) | `ProofreadingTool` |
| **Formatter** | PDF & EPUB generation | `BookFormatterTool` |
| **ReaderPackBuilder** | Public sample bundle creation | `ReaderBundleGeneratorTool`, `ReaderBundleValidatorTool` |
| **ReleasePackager** | Final release manifest & checksums | `ReleaseManifestTool` |

### Data Models (Schemas)
All data structures use Pydantic V2 for strict validation:
- `CanonicalManuscript`: Internal JSON representation of the book.
- `GateState`: Tracks pipeline progress, issues, and sign-offs.
- `ReaderBundle`: Public-facing schema for the Reader App.
- `ReleaseManifest`: Immutable record of a release version.

## Usage

### Prerequisites
- Python 3.10+
- OpenAI API Key (for agents)
- Firebase Credentials (for hosting deployment)

### Configuration
Environment variables in `.env`:
```bash
ATHAR_STORAGE_BACKEND=local    # or 'gcs'
ATHAR_GCS_BUCKET=my-bucket     # required if backend is 'gcs'
ATHAR_PROJECT_ROOT=./storage   # root for local storage
```

### Installation
```bash
pip install -r requirements.txt
```

### Running the Agency
The entry point is `agency.py`, which initializes the `PublishingOrchestrator`.

```bash
python agency.py
```

**Example Command:**
> "Start the publishing process for 'my_manuscript.docx'. Title: 'The Journey', Author: 'Aya El Badry'."

### Workflow Steps
1.  **Ingestion**: `ManuscriptIntake` parses the file into `storage/private/manuscripts/`.
2.  **Style Edit**: `StyleEditor` provides suggestions (non-blocking).
3.  **Pass 1**: `Proofreader` checks grammar. **Gate: PASS1** must be signed.
4.  **Formatting**: `Formatter` generates PDF/EPUBs.
5.  **Pass 2**: `Proofreader` checks checks formatting. **Gate: PASS2** must be signed.
6.  **Bundling**: `ReaderPackBuilder` creates the public sample JSON.
7.  **Release**: `ReleasePackager` finalizes the manifest and deploys to Firebase.

## Testing

A comprehensive production suite verifies the critical hardening measures.

```bash
python test_production_suite.py
```

**What it tests:**
- **Gate Regression**: Ensures modifying content invalidates previous sign-offs.
- **Bundle Safety**: Checks that public bundles don't leak non-whitelisted chapters.
- **Parsing Trust**: Verifies confidence levels for different file types.
- **Idempotency**: Ensures tools are safe to re-run.

For end-to-end integration testing:
```bash
python test_publishing_pipeline.py
```

## Directory Structure
```
ArtisanProAgencii/
├── agency.py                 # Entry point
├── schemas/                  # Pydantic V2 models
├── publishing_orchestrator/  # Main agent
├── manuscript_intake/        # Ingestion agent
├── style_editor/             # Style agent
├── proofreader/              # QC agent
├── formatter/                # Export agent
├── reader_packbuilder/       # Sample agent
├── release_packager/         # Release agent
├── storage/                  # Artifact storage
│   ├── private/              # Master manuscripts & full exports
│   └── public/               # Reader bundles (hosted)
└── ...
```

## License
Proprietary - Athar Project

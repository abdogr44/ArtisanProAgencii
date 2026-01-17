# Repository Context - Athar Publishing Pipeline

## High-Level Call Graph

```mermaid
graph TD
    User([User]) -->|Starts| Agency[agency.py]
    Agency -->|Initializes| Orch[PublishingOrchestrator]
    
    Orch -->|Ingests| IngestTool[ProjectFileIngestTool]
    IngestTool -->|Saves to| Storage[StorageBackend (Local/GCS)]
    
    Orch -->|Routes to| Intake[ManuscriptIntake]
    Intake -->|Reads from| Storage
    Intake -->|Uses| Compiler[ManuscriptCompilerTool]
    Compiler -->|Writes| MS_JSON[Canonical Manuscript JSON]
    
    Orch -->|Routes to| Style[StyleEditor]
    Style -->|Reads| MS_JSON
    Style -->|Uses| SuggTool[StyleSuggestionTool]
    
    Orch -->|Routes to| Proof[Proofreader]
    Proof -->|Reads| MS_JSON
    Proof -->|Uses| ProofTool[ProofreadingTool]
    
    Orch -->|Enforces| GateTool[GateEnforcementTool]
    GateTool -->|Check/Sign| GateState[GateState JSON]
    
    Orch -->|Routes to| Format[Formatter]
    Format -->|Reads| MS_JSON
    Format -->|Uses| FormatTool[BookFormatterTool]
    FormatTool -->|Generates| Export[PDF/EPUB Exports]
    
    Orch -->|Routes to| Bundle[ReaderPackBuilder]
    Bundle -->|Reads| MS_JSON
    Bundle -->|Uses| BundleTool[ReaderBundleGeneratorTool]
    BundleTool -->|Uses| Validator[ReaderBundleValidatorTool]
    BundleTool -->|Generates| PublicJson[Reader Bundle JSON]
    
    Orch -->|Routes to| Release[ReleasePackager]
    Release -->|Uses| ManifestTool[ReleaseManifestTool]
    ManifestTool -->|Deploys to| Firebase[Firebase Hosting]
```

## File Structure Map

```text
ArtisanProAgencii/
├── agency.py                      # Main Entry Point
├── AGENTS.md                      # Brand rules & agent definitions
├── requirements.txt               # Python dependencies
├── test_publishing_pipeline.py    # E2E Integration Test

├── test_production_suite.py       # Production Hardening Test
├── test_ingest_reliability.py     # Ingestion Logic Test
│
├── schemas/                       # Pydantic V2 Data Models
│   ├── athar_output_envelope.py
│   ├── canonical_manuscript.py
│   ├── gate_state.py
│   ├── reader_bundle.py
│   └── release_manifest.py
│

├── storage_backends/              # storage abstraction
│   ├── base.py
│   ├── local.py
│   ├── gcs.py
│   └── __init__.py
│
├── publishing_orchestrator/       # Pipeline Controller
│   ├── publishing_orchestrator.py
│   ├── instructions.md
│   └── tools/
│       ├── GateEnforcementTool.py
│       ├── PipelineStatusTool.py
│       └── ProjectFileIngestTool.py
│
├── manuscript_intake/             # Ingestion Agent
│   ├── manuscript_intake.py
│   ├── instructions.md
│   └── tools/
│       └── ManuscriptCompilerTool.py
│
├── style_editor/                  # Style Agent
│   ├── style_editor.py
│   ├── instructions.md
│   └── tools/
│       └── StyleSuggestionTool.py
│
├── proofreader/                   # QC Agent
│   ├── proofreader.py
│   ├── instructions.md
│   └── tools/
│       └── ProofreadingTool.py
│
├── formatter/                     # Export Agent
│   ├── formatter.py
│   ├── instructions.md
│   └── tools/
│       └── BookFormatterTool.py
│
├── reader_packbuilder/            # Bundle Agent
│   ├── reader_packbuilder.py
│   ├── instructions.md
│   └── tools/
│       ├── ReaderBundleGeneratorTool.py
│       └── ReaderBundleValidatorTool.py
│
├── release_packager/              # Release Agent
│   ├── release_packager.py
│   ├── instructions.md
│   └── tools/
│       └── ReleaseManifestTool.py
│
└── storage/                       # Artifact Storage
    ├── private/                   # Master Data (Internal)
    │   ├── manuscripts/
    │   ├── states/
    │   ├── reports/
    │   └── exports/
    └── public/                    # Hosted Data (External)
        └── reader_bundles/
```

## Legacy Components
*Maintained for backward compatibility or reference*
- `social_media_writer/`
- `graphic_designer/`
- `brand-knowledge-implementation.md`

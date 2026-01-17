# Athar Publishing Pipeline - Shared Operational Guidelines

## 1. Storage & File Handling
- **Private by Default**: All manuscripts and intermediate artifacts must be stored in `storage/private/`. Only final `reader_bundle.sample.json` is allowed in `storage/public/`.
- **Ingestion First**: Never process raw user uploads directly. The Orchestrator must use `ProjectFileIngestTool` to secure files into the storage backend first.
- **Storage URIs**: Agents must pass stable storage URIs (e.g., `file:///abs/path/...` or `gs://bucket/path/...`) for source files. Do not rely on ephemeral message attachments.
- **Storage Backend**: Use `get_storage_backend()` to resolve URIs to local paths for processing.

## 2. Security & Gates
- **Input Binding**: All gate approvals are cryptographically bound to the manuscript's `input_hash`. Any modification to the source or canonical manuscript invalidates previous sign-offs.
- **Leak Prevention**: Public bundles must validation against the `sample_whitelist`.
- **Artifact Visibility**: Explicitly mark artifacts as `"visibility": "private"` or `"public"` in `AtharOutputEnvelope`.

## 3. Communication Standard
- **AtharOutputEnvelope**: All tools must return this standardized JSON structure.
- **Error Handling**: Return graceful error envelopes with `success: false` rather than raising uncaught exceptions.

## 4. Logging Hygiene
- **Redaction**: Never log full manuscript text or PII. Log only metadata (IDs, word counts, hashes).
- **Timezones**: Always use `datetime.now(timezone.utc)` for timestamps.

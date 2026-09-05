# `llm_transcripts`

> [← Project README](../../README.md)

## Classes

### `class LlmTranscriptRun`

Fields:
- `path: Path`
- `metadata: dict[str, Any]`
- `request_input: Any`
- `required_keys: tuple[str, ...]`
- `raw_response: str`
- `normalized_response: str`
- `repair_prompt: str | None`
- `repair_raw_response: str | None`
- `provider_metadata: dict[str, Any]`
- `repair_provider_metadata: dict[str, Any]`
- `elapsed_seconds: float | None`
- `repair_elapsed_seconds: float | None`
- `repair_method: str`
- `status: str`
- `error: str | None`
- `finalized: bool`


## Functions

### `begin_transcript(router: 'Any', request: 'Mapping[str, Any]') -> 'LlmTranscriptRun | None'`

### `finalize_last_transcript(store: 'Any', node: 'Any', *, error: 'str | None' = None) -> 'Path | None'`

### `last_transcript_run() -> 'LlmTranscriptRun | None'`

### `list_transcripts(node: 'Any') -> 'list[Path]'`

### `record_initial_response(run: 'LlmTranscriptRun | None', response: 'Any', *, elapsed_seconds: 'float') -> 'None'`

### `record_repair_response(run: 'LlmTranscriptRun | None', *, prompt: 'str', response: 'Any', elapsed_seconds: 'float') -> 'None'`

### `restore_transcript(store: 'Any', node: 'Any', path: 'str | Path') -> 'list[Path]'`

### `save_transcript(run: 'LlmTranscriptRun | None', *, artifacts: 'Mapping[str, str] | None' = None) -> 'Path | None'`

### `transcript_metadata(path: 'str | Path') -> 'dict[str, Any]'`

### `transcripts_enabled() -> 'bool'`

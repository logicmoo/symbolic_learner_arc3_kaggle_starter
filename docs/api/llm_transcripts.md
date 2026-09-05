> [← Project README](../../README.md)

# Table of Contents

* [llm\_transcripts](#llm_transcripts)
  * [TRANSCRIPT\_PREFIX](#llm_transcripts.TRANSCRIPT_PREFIX)
  * [TRANSCRIPT\_VERSION](#llm_transcripts.TRANSCRIPT_VERSION)
  * [RESTORABLE\_ARTIFACTS](#llm_transcripts.RESTORABLE_ARTIFACTS)
  * [transcripts\_enabled](#llm_transcripts.transcripts_enabled)
  * [LlmTranscriptRun](#llm_transcripts.LlmTranscriptRun)
    * [path](#llm_transcripts.LlmTranscriptRun.path)
    * [metadata](#llm_transcripts.LlmTranscriptRun.metadata)
    * [request\_input](#llm_transcripts.LlmTranscriptRun.request_input)
    * [required\_keys](#llm_transcripts.LlmTranscriptRun.required_keys)
    * [raw\_response](#llm_transcripts.LlmTranscriptRun.raw_response)
    * [normalized\_response](#llm_transcripts.LlmTranscriptRun.normalized_response)
    * [repair\_prompt](#llm_transcripts.LlmTranscriptRun.repair_prompt)
    * [repair\_raw\_response](#llm_transcripts.LlmTranscriptRun.repair_raw_response)
    * [provider\_metadata](#llm_transcripts.LlmTranscriptRun.provider_metadata)
    * [repair\_provider\_metadata](#llm_transcripts.LlmTranscriptRun.repair_provider_metadata)
    * [elapsed\_seconds](#llm_transcripts.LlmTranscriptRun.elapsed_seconds)
    * [repair\_elapsed\_seconds](#llm_transcripts.LlmTranscriptRun.repair_elapsed_seconds)
    * [repair\_method](#llm_transcripts.LlmTranscriptRun.repair_method)
    * [status](#llm_transcripts.LlmTranscriptRun.status)
    * [error](#llm_transcripts.LlmTranscriptRun.error)
    * [finalized](#llm_transcripts.LlmTranscriptRun.finalized)
  * [begin\_transcript](#llm_transcripts.begin_transcript)
  * [last\_transcript\_run](#llm_transcripts.last_transcript_run)
  * [record\_initial\_response](#llm_transcripts.record_initial_response)
  * [record\_repair\_response](#llm_transcripts.record_repair_response)
  * [transcript\_metadata](#llm_transcripts.transcript_metadata)
  * [save\_transcript](#llm_transcripts.save_transcript)
  * [finalize\_last\_transcript](#llm_transcripts.finalize_last_transcript)
  * [list\_transcripts](#llm_transcripts.list_transcripts)
  * [restore\_transcript](#llm_transcripts.restore_transcript)

<a id="llm_transcripts"></a>

# llm\_transcripts

<a id="llm_transcripts.TRANSCRIPT_PREFIX"></a>

#### TRANSCRIPT\_PREFIX

<a id="llm_transcripts.TRANSCRIPT_VERSION"></a>

#### TRANSCRIPT\_VERSION

<a id="llm_transcripts.RESTORABLE_ARTIFACTS"></a>

#### RESTORABLE\_ARTIFACTS

<a id="llm_transcripts.transcripts_enabled"></a>

#### transcripts\_enabled

```python
def transcripts_enabled() -> bool
```

<a id="llm_transcripts.LlmTranscriptRun"></a>

## LlmTranscriptRun Objects

```python
@dataclass
class LlmTranscriptRun()
```

<a id="llm_transcripts.LlmTranscriptRun.path"></a>

#### path: `Path`

<a id="llm_transcripts.LlmTranscriptRun.metadata"></a>

#### metadata: `dict[str, Any]`

<a id="llm_transcripts.LlmTranscriptRun.request_input"></a>

#### request\_input: `Any`

<a id="llm_transcripts.LlmTranscriptRun.required_keys"></a>

#### required\_keys: `tuple[str, ...]`

<a id="llm_transcripts.LlmTranscriptRun.raw_response"></a>

#### raw\_response: `str`

<a id="llm_transcripts.LlmTranscriptRun.normalized_response"></a>

#### normalized\_response: `str`

<a id="llm_transcripts.LlmTranscriptRun.repair_prompt"></a>

#### repair\_prompt: `str | None`

<a id="llm_transcripts.LlmTranscriptRun.repair_raw_response"></a>

#### repair\_raw\_response: `str | None`

<a id="llm_transcripts.LlmTranscriptRun.provider_metadata"></a>

#### provider\_metadata: `dict[str, Any]`

<a id="llm_transcripts.LlmTranscriptRun.repair_provider_metadata"></a>

#### repair\_provider\_metadata: `dict[str, Any]`

<a id="llm_transcripts.LlmTranscriptRun.elapsed_seconds"></a>

#### elapsed\_seconds: `float | None`

<a id="llm_transcripts.LlmTranscriptRun.repair_elapsed_seconds"></a>

#### repair\_elapsed\_seconds: `float | None`

<a id="llm_transcripts.LlmTranscriptRun.repair_method"></a>

#### repair\_method: `str`

<a id="llm_transcripts.LlmTranscriptRun.status"></a>

#### status: `str`

<a id="llm_transcripts.LlmTranscriptRun.error"></a>

#### error: `str | None`

<a id="llm_transcripts.LlmTranscriptRun.finalized"></a>

#### finalized: `bool`

<a id="llm_transcripts.begin_transcript"></a>

#### begin\_transcript

```python
def begin_transcript(router: Any,
                     request: Mapping[str, Any]) -> LlmTranscriptRun | None
```

<a id="llm_transcripts.last_transcript_run"></a>

#### last\_transcript\_run

```python
def last_transcript_run() -> LlmTranscriptRun | None
```

<a id="llm_transcripts.record_initial_response"></a>

#### record\_initial\_response

```python
def record_initial_response(run: LlmTranscriptRun | None, response: Any, *,
                            elapsed_seconds: float) -> None
```

<a id="llm_transcripts.record_repair_response"></a>

#### record\_repair\_response

```python
def record_repair_response(run: LlmTranscriptRun | None, *, prompt: str,
                           response: Any, elapsed_seconds: float) -> None
```

<a id="llm_transcripts.transcript_metadata"></a>

#### transcript\_metadata

```python
def transcript_metadata(path: str | Path) -> dict[str, Any]
```

<a id="llm_transcripts.save_transcript"></a>

#### save\_transcript

```python
def save_transcript(run: LlmTranscriptRun | None,
                    *,
                    artifacts: Mapping[str, str] | None = None) -> Path | None
```

<a id="llm_transcripts.finalize_last_transcript"></a>

#### finalize\_last\_transcript

```python
def finalize_last_transcript(store: Any,
                             node: Any,
                             *,
                             error: str | None = None) -> Path | None
```

<a id="llm_transcripts.list_transcripts"></a>

#### list\_transcripts

```python
def list_transcripts(node: Any) -> list[Path]
```

<a id="llm_transcripts.restore_transcript"></a>

#### restore\_transcript

```python
def restore_transcript(store: Any, node: Any, path: str | Path) -> list[Path]
```

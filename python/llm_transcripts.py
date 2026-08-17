from __future__ import annotations

import base64
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

TRANSCRIPT_PREFIX = "llm_adapter_"
TRANSCRIPT_VERSION = 1
RESTORABLE_ARTIFACTS = (
    "object_registry.pl",
    "objects.pl",
    "differences.pl",
    "similarities.pl",
    "turtle_from_image.pl",
    "turtle_from_diff.pl",
    "rules.pl",
)
_METADATA_RE = re.compile(r"<!-- ARC3_LLM_METADATA_B64: ([A-Za-z0-9+/=]+) -->")
_BEGIN_RE = re.compile(r"<!-- ARC3_LLM_ARTIFACT_BEGIN: ([A-Za-z0-9_.-]+) -->")
_END_TEMPLATE = "<!-- ARC3_LLM_ARTIFACT_END: {name} -->"
_DATA_URL_RE = re.compile(r"^data:([^;,]+);base64,(.*)$", re.DOTALL)
_LAST_RUN: "LlmTranscriptRun | None" = None


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on", "y"}:
        return True
    if normalized in {"0", "false", "no", "off", "n"}:
        return False
    raise RuntimeError(f"{name} must be a boolean value, not {value!r}")


def transcripts_enabled() -> bool:
    # Keep the old setting as a compatibility alias: raw responses now live in
    # the Markdown transcript rather than separate .txt/.json sidecars.
    return _env_bool(
        "ARC3_LLM_SAVE_TRANSCRIPT",
        _env_bool("ARC3_LLM_SAVE_RAW_RESPONSE", True),
    )


def _slug(value: Any, *, limit: int = 80) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "").strip())
    cleaned = cleaned.strip("._-") or "unknown"
    return cleaned[:limit].rstrip("._-") or "unknown"


def _jsonable(value: Any, depth: int = 0) -> Any:
    if depth > 6:
        return repr(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item, depth + 1) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item, depth + 1) for item in value]
    for method_name in ("model_dump", "dict"):
        method = getattr(value, method_name, None)
        if callable(method):
            try:
                return _jsonable(method(), depth + 1)
            except Exception:
                pass
    if hasattr(value, "__dict__"):
        public = {
            key: item
            for key, item in vars(value).items()
            if not key.startswith("_")
        }
        if public:
            return _jsonable(public, depth + 1)
    return repr(value)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return _sha256_bytes(value.encode("utf-8"))


def _relative_link(source_dir: Path, target: Path) -> str:
    return Path(os.path.relpath(target, source_dir)).as_posix()


def _current_context() -> tuple[Any | None, Any | None, Any | None]:
    try:
        from multillm_runner import last_runner

        runner = last_runner()
        if runner is None:
            return None, None, None
        return runner, getattr(runner, "tree_store", None), getattr(runner, "current_node", None)
    except Exception:
        return None, None, None


def _response_directory(node: Any | None) -> Path:
    if node is not None and getattr(node, "path", None) is not None:
        return Path(node.path)
    configured = os.environ.get("ARC3_LLM_RESPONSE_DIR", "").strip()
    root = Path(configured or ".llm_responses").expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _active_profile(runner: Any | None) -> dict[str, Any]:
    analyzer = getattr(runner, "_gpt_analyzer", None) if runner is not None else None
    profile = getattr(analyzer, "active_profile", None)
    return dict(profile) if isinstance(profile, Mapping) else {}


def _state_metadata(store: Any | None, node: Any | None) -> dict[str, Any]:
    if store is None or node is None:
        return {}
    try:
        value = store.metadata(node)
        return dict(value) if isinstance(value, Mapping) else {}
    except Exception:
        return {}


def _transcript_filename(
    *,
    adapter: str,
    provider_id: str,
    model: str,
    analysis_level: Any,
    profile_name: str,
    max_output_tokens: Any,
    timestamp: datetime,
) -> str:
    level = f"L{analysis_level}" if analysis_level is not None else "Lx"
    tokens = str(max_output_tokens or "unknown")
    stamp = timestamp.strftime("%Y%m%dT%H%M%S_%fZ")
    return (
        f"{TRANSCRIPT_PREFIX}{_slug(adapter, limit=36)}_"
        f"{_slug(provider_id, limit=28)}_{_slug(model, limit=72)}_"
        f"{_slug(level, limit=12)}_{_slug(profile_name or 'profile', limit=24)}_"
        f"tokens_{_slug(tokens, limit=16)}_{stamp}.md"
    )


@dataclass
class LlmTranscriptRun:
    path: Path
    metadata: dict[str, Any]
    request_input: Any
    required_keys: tuple[str, ...] = ()
    raw_response: str = ""
    normalized_response: str = ""
    repair_prompt: str | None = None
    repair_raw_response: str | None = None
    provider_metadata: dict[str, Any] = field(default_factory=dict)
    repair_provider_metadata: dict[str, Any] = field(default_factory=dict)
    elapsed_seconds: float | None = None
    repair_elapsed_seconds: float | None = None
    repair_method: str = "pending"
    status: str = "started"
    error: str | None = None
    finalized: bool = False


def begin_transcript(router: Any, request: Mapping[str, Any]) -> LlmTranscriptRun | None:
    global _LAST_RUN
    if not transcripts_enabled():
        _LAST_RUN = None
        return None

    spec = router.current_spec()
    runner, store, node = _current_context()
    profile = _active_profile(runner)
    analysis_level = getattr(runner, "_active_llm_analysis_level", None)
    now = datetime.now(timezone.utc)
    model = spec.resolved_model() or str(request.get("model") or "unknown")
    max_tokens = request.get("max_output_tokens")
    directory = _response_directory(node)
    directory.mkdir(parents=True, exist_ok=True)
    filename = _transcript_filename(
        adapter=spec.adapter,
        provider_id=spec.provider_id,
        model=model,
        analysis_level=analysis_level,
        profile_name=str(profile.get("name") or "profile"),
        max_output_tokens=max_tokens,
        timestamp=now,
    )
    state = _state_metadata(store, node)
    metadata = {
        "transcript_version": TRANSCRIPT_VERSION,
        "provider_id": spec.provider_id,
        "provider_label": spec.label,
        "adapter": spec.adapter,
        "model": model,
        "base_url": spec.resolved_base_url(),
        "analysis_level": analysis_level,
        "analysis_profile": profile,
        "max_output_tokens": max_tokens,
        "reasoning": _jsonable(request.get("reasoning")),
        "started_at": now.isoformat(),
        "node_path": str(getattr(node, "path", "")) if node is not None else None,
        "game_id": state.get("game_id") or getattr(runner, "game_id", None),
        "level": state.get("level"),
        "state": state.get("state"),
        "step_count": state.get("step_count"),
        "incoming_action": state.get("incoming_action") or "initial",
        "action_data": _jsonable(state.get("action_data") or {}),
        "action_path": _jsonable(state.get("action_path") or []),
        "image_hash": state.get("image_hash") or getattr(node, "image_hash", None),
        "prompt_sections": (
            list(runner.llm_router().prompt_section_names(spec))
            if runner is not None and hasattr(runner, "llm_router")
            else []
        ),
    }
    run = LlmTranscriptRun(
        path=directory / filename,
        metadata=metadata,
        request_input=request.get("input"),
    )
    _LAST_RUN = run
    return run


def last_transcript_run() -> LlmTranscriptRun | None:
    return _LAST_RUN


def record_initial_response(
    run: LlmTranscriptRun | None,
    response: Any,
    *,
    elapsed_seconds: float,
) -> None:
    if run is None:
        return
    run.elapsed_seconds = elapsed_seconds
    run.raw_response = str(getattr(response, "output_text", None) or "")
    metadata = getattr(response, "provider_metadata", None)
    run.provider_metadata = (
        dict(_jsonable(metadata)) if isinstance(metadata, Mapping) else {}
    )
    run.status = "response_received"


def record_repair_response(
    run: LlmTranscriptRun | None,
    *,
    prompt: str,
    response: Any,
    elapsed_seconds: float,
) -> None:
    if run is None:
        return
    run.repair_prompt = prompt
    run.repair_raw_response = str(getattr(response, "output_text", None) or "")
    metadata = getattr(response, "provider_metadata", None)
    run.repair_provider_metadata = (
        dict(_jsonable(metadata)) if isinstance(metadata, Mapping) else {}
    )
    run.repair_elapsed_seconds = elapsed_seconds


def _metadata_comment(metadata: Mapping[str, Any]) -> str:
    payload = json.dumps(_jsonable(metadata), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return "<!-- ARC3_LLM_METADATA_B64: " + base64.b64encode(payload).decode("ascii") + " -->"


def transcript_metadata(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    match = _METADATA_RE.search(text)
    if not match:
        return {}
    try:
        raw = base64.b64decode(match.group(1), validate=True)
        value = json.loads(raw.decode("utf-8"))
        return dict(value) if isinstance(value, Mapping) else {}
    except Exception:
        return {}


def _markdown_fence(content: str, language: str) -> list[str]:
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", content)), default=0)
    fence = "`" * max(4, longest + 1)
    return [f"{fence}{language}", content.rstrip("\n"), fence]


def _artifact_section(name: str, content: str) -> list[str]:
    digest = _sha256_text(content)
    return [
        f"### `{name}`",
        "",
        f"- **SHA-256:** `{digest}`",
        f"<!-- ARC3_LLM_ARTIFACT_BEGIN: {name} -->",
        *_markdown_fence(content, "prolog"),
        f"<!-- ARC3_LLM_ARTIFACT_END: {name} -->",
        "",
    ]


def _request_blocks(request_input: Any, transcript_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    texts: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    runner, store, node = _current_context()
    known_images: dict[str, Path] = {}
    if node is not None and getattr(node, "image_path", None) is not None:
        path = Path(node.image_path)
        if path.exists():
            known_images[_sha256_bytes(path.read_bytes())] = path
    if store is not None and node is not None:
        try:
            parent = store.parent_node(node)
            if parent is not None and parent.image_path.exists():
                known_images[_sha256_bytes(parent.image_path.read_bytes())] = parent.image_path
        except Exception:
            pass

    for message_index, message in enumerate(request_input or [], start=1):
        if not isinstance(message, Mapping):
            continue
        role = str(message.get("role") or "user")
        content = message.get("content")
        if isinstance(content, str):
            texts.append({"message": message_index, "role": role, "block": 1, "text": content})
            continue
        for block_index, block in enumerate(content or [], start=1):
            if not isinstance(block, Mapping):
                continue
            block_type = str(block.get("type") or "")
            if block_type in {"input_text", "text"}:
                texts.append(
                    {
                        "message": message_index,
                        "role": role,
                        "block": block_index,
                        "text": str(block.get("text") or ""),
                    }
                )
                continue
            if block_type not in {"input_image", "image_url"}:
                continue
            image_value = block.get("image_url")
            if isinstance(image_value, Mapping):
                image_value = image_value.get("url")
            match = _DATA_URL_RE.match(str(image_value or ""))
            descriptor: dict[str, Any] = {
                "message": message_index,
                "role": role,
                "block": block_index,
                "detail": block.get("detail"),
                "media_type": None,
                "bytes": None,
                "sha256": None,
                "link": None,
            }
            if match:
                media_type, encoded = match.groups()
                try:
                    decoded = base64.b64decode(encoded, validate=True)
                    digest = _sha256_bytes(decoded)
                    descriptor.update(
                        {
                            "media_type": media_type,
                            "bytes": len(decoded),
                            "sha256": digest,
                        }
                    )
                    known = known_images.get(digest)
                    if known is not None:
                        descriptor["link"] = _relative_link(transcript_dir, known)
                except Exception:
                    pass
            images.append(descriptor)
    return texts, images


def _flatten_usage(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    result: list[tuple[str, Any]] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            name = f"{prefix}.{key}" if prefix else str(key)
            if isinstance(item, Mapping):
                result.extend(_flatten_usage(item, name))
            elif isinstance(item, (str, int, float, bool)) or item is None:
                result.append((name, item))
    return result


def _render_transcript(
    run: LlmTranscriptRun,
    *,
    artifacts: Mapping[str, str] | None,
) -> str:
    metadata = dict(run.metadata)
    metadata.update(
        {
            "required_keys": list(run.required_keys),
            "elapsed_seconds": run.elapsed_seconds,
            "repair_elapsed_seconds": run.repair_elapsed_seconds,
            "repair_method": run.repair_method,
            "status": run.status,
            "error": run.error,
            "completed_at": metadata.get("completed_at"),
        }
    )
    lines: list[str] = [
        "# LLM artifact snapshot",
        "",
        _metadata_comment(metadata),
        (
            "> This Markdown file is the immutable comparison/cache record for one "
            "LLM run. Restoring it rewrites the mutable latest `.pl` files."
        ),
        "",
        f"- **Provider:** `{metadata.get('provider_id')}` — {metadata.get('provider_label')}",
        f"- **Adapter:** `{metadata.get('adapter')}`",
        f"- **Model:** `{metadata.get('model')}`",
        f"- **Analysis level:** `{metadata.get('analysis_level')}`",
        f"- **Profile:** `{(metadata.get('analysis_profile') or {}).get('name', 'unknown')}`",
        f"- **Requested max output tokens:** `{metadata.get('max_output_tokens')}`",
        f"- **Status:** `{run.status}`",
        "",
        "## Restorable Prolog artifacts",
        "",
    ]

    if artifacts:
        for name in RESTORABLE_ARTIFACTS:
            if name in artifacts:
                lines.extend(_artifact_section(name, artifacts[name]))
    else:
        lines.extend(
            [
                "*No restorable artifact snapshot was finalized for this run.*",
                "",
            ]
        )

    lines.extend(
        [
            "---",
            "",
            "# Debug transcript",
            "",
            "## State and action context",
            "",
            f"- **Game:** `{metadata.get('game_id')}`",
            f"- **Level:** `{metadata.get('level')}`",
            f"- **State:** `{metadata.get('state')}`",
            f"- **Step:** `{metadata.get('step_count')}`",
            f"- **Incoming action:** `{metadata.get('incoming_action')}`",
            f"- **Action data:** `{json.dumps(metadata.get('action_data') or {}, ensure_ascii=False)}`",
            f"- **Action path:** `{json.dumps(metadata.get('action_path') or [], ensure_ascii=False)}`",
            f"- **Image hash:** `{metadata.get('image_hash')}`",
            "",
            "## Timing and token details",
            "",
            f"- **Initial provider call:** `{run.elapsed_seconds}` seconds",
            f"- **Text-only repair call:** `{run.repair_elapsed_seconds}` seconds",
            f"- **Reasoning request:** `{json.dumps(metadata.get('reasoning'), ensure_ascii=False)}`",
            f"- **Repair method:** `{run.repair_method}`",
            "",
        ]
    )

    usage = None
    if isinstance(run.provider_metadata, Mapping):
        usage = run.provider_metadata.get("usage")
    usage_rows = _flatten_usage(usage)
    if usage_rows:
        lines.extend(["### Reported provider usage", "", "| Field | Value |", "|---|---:|"])
        for key, value in usage_rows:
            lines.append(f"| `{key}` | `{value}` |")
        lines.append("")
    else:
        lines.extend(["*The provider did not report token usage for this call.*", ""])

    if run.provider_metadata:
        lines.extend(
            [
                "<details>",
                "<summary>Adapter/provider response metadata</summary>",
                "",
                *_markdown_fence(
                    json.dumps(run.provider_metadata, indent=2, ensure_ascii=False, sort_keys=True),
                    "json",
                ),
                "",
                "</details>",
                "",
            ]
        )

    text_blocks, image_blocks = _request_blocks(run.request_input, run.path.parent)
    lines.extend(["## Request images", ""])
    if image_blocks:
        lines.extend(
            [
                "| Message/block | Detail | MIME | Bytes | SHA-256 | Source |",
                "|---|---|---|---:|---|---|",
            ]
        )
        for item in image_blocks:
            link = f"[image]({item['link']})" if item.get("link") else "embedded data URL"
            lines.append(
                f"| `{item['message']}/{item['block']}` | `{item.get('detail')}` | "
                f"`{item.get('media_type')}` | `{item.get('bytes')}` | "
                f"`{item.get('sha256')}` | {link} |"
            )
        lines.append("")
        for index, item in enumerate(image_blocks, start=1):
            if item.get("link"):
                lines.extend(
                    [
                        f"### Request image {index}",
                        "",
                        f"![Request image {index}]({item['link']})",
                        "",
                    ]
                )
    else:
        lines.extend(["*No image blocks were sent.*", ""])

    lines.extend(["## Initial request sent", ""])
    if text_blocks:
        for item in text_blocks:
            lines.extend(
                [
                    f"### Message {item['message']} · `{item['role']}` · text block {item['block']}",
                    "",
                    "<!-- ARC3_LLM_PROMPT_BEGIN -->",
                    str(item["text"]).rstrip(),
                    "<!-- ARC3_LLM_PROMPT_END -->",
                    "",
                ]
            )
    else:
        lines.extend(["*No text blocks were sent.*", ""])

    if run.repair_prompt is not None:
        lines.extend(
            [
                "## Text-only repair request sent",
                "",
                "<!-- ARC3_LLM_REPAIR_PROMPT_BEGIN -->",
                run.repair_prompt.rstrip(),
                "<!-- ARC3_LLM_REPAIR_PROMPT_END -->",
                "",
            ]
        )

    if run.normalized_response:
        lines.extend(
            [
                "<details>",
                "<summary>Normalized strict JSON used to write artifacts</summary>",
                "",
                *_markdown_fence(run.normalized_response, "json"),
                "",
                "</details>",
                "",
            ]
        )

    if run.error:
        lines.extend(["## Error", "", str(run.error), ""])

    # Keep every response at the very bottom so a human can scroll directly to
    # the provider output. The initial prompt above is intentionally rendered as
    # Markdown rather than hidden inside a code fence.
    lines.extend(["## Raw provider responses", "", "### Initial raw response", ""])
    lines.extend(_markdown_fence(run.raw_response or "", "text"))
    if run.repair_raw_response is not None:
        lines.extend(["", "### Text-only repair raw response", ""])
        lines.extend(_markdown_fence(run.repair_raw_response, "text"))
    return "\n".join(lines).rstrip() + "\n"


def save_transcript(
    run: LlmTranscriptRun | None,
    *,
    artifacts: Mapping[str, str] | None = None,
) -> Path | None:
    if run is None or not transcripts_enabled():
        return None
    run.path.parent.mkdir(parents=True, exist_ok=True)
    run.path.write_text(
        _render_transcript(run, artifacts=artifacts),
        encoding="utf-8",
    )
    return run.path


def _artifact_snapshot(store: Any, node: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for name in RESTORABLE_ARTIFACTS:
        path = store.object_registry_path if name == "object_registry.pl" else node.path / name
        if path.exists() and path.is_file():
            result[name] = path.read_text(encoding="utf-8")
    return result


def finalize_last_transcript(
    store: Any,
    node: Any,
    *,
    error: str | None = None,
) -> Path | None:
    run = last_transcript_run()
    if run is None or run.finalized:
        return None
    node_path = Path(getattr(node, "path", "")).resolve()
    if run.path.parent.resolve() != node_path:
        return None
    run.metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
    run.error = error
    run.status = "failed" if error else "complete"
    artifacts = None if error else _artifact_snapshot(store, node)
    path = save_transcript(run, artifacts=artifacts)
    run.finalized = True
    if path is not None:
        os.utime(path, None)
        store.refresh_readme(node)
    return path


def list_transcripts(node: Any) -> list[Path]:
    path = Path(node.path)
    result = [
        candidate
        for candidate in path.glob(f"{TRANSCRIPT_PREFIX}*.md")
        if candidate.is_file()
    ]
    return sorted(result, key=lambda item: (item.stat().st_mtime_ns, item.name), reverse=True)


def _extract_artifacts(text: str) -> dict[str, str]:
    lines = text.splitlines()
    result: dict[str, str] = {}
    index = 0
    while index < len(lines):
        match = _BEGIN_RE.fullmatch(lines[index].strip())
        if not match:
            index += 1
            continue
        name = match.group(1)
        if name not in RESTORABLE_ARTIFACTS:
            raise RuntimeError(f"Transcript contains unsupported artifact: {name}")
        end_marker = _END_TEMPLATE.format(name=name)
        try:
            end_index = next(
                position
                for position in range(index + 1, len(lines))
                if lines[position].strip() == end_marker
            )
        except StopIteration as error:
            raise RuntimeError(f"Transcript artifact {name} has no end marker") from error
        section = lines[index + 1 : end_index]
        fence_index = next(
            (position for position, line in enumerate(section) if re.fullmatch(r"`{3,}prolog", line.strip())),
            None,
        )
        if fence_index is None:
            raise RuntimeError(f"Transcript artifact {name} has no Prolog fence")
        fence = section[fence_index].strip()[:-6]
        try:
            close_index = next(
                position
                for position in range(fence_index + 1, len(section))
                if section[position].strip() == fence
            )
        except StopIteration as error:
            raise RuntimeError(f"Transcript artifact {name} has no closing fence") from error
        content = "\n".join(section[fence_index + 1 : close_index])
        result[name] = content + ("" if content.endswith("\n") else "\n")
        index = end_index + 1
    return result


def restore_transcript(store: Any, node: Any, path: str | Path) -> list[Path]:
    transcript = Path(path).resolve()
    if transcript.parent != Path(node.path).resolve():
        raise RuntimeError("Only transcripts belonging to the current state node may be restored")
    text = transcript.read_text(encoding="utf-8")
    artifacts = _extract_artifacts(text)
    if not artifacts:
        raise RuntimeError(f"Transcript has no restorable Prolog artifacts: {transcript.name}")

    restored: list[Path] = []
    for name, content in artifacts.items():
        destination = store.object_registry_path if name == "object_registry.pl" else node.path / name
        destination.write_text(content, encoding="utf-8")
        restored.append(destination)

    metadata = transcript_metadata(transcript)
    provenance = {
        "provider_id": metadata.get("provider_id"),
        "label": metadata.get("provider_label"),
        "adapter": metadata.get("adapter"),
        "model": metadata.get("model"),
        "base_url": metadata.get("base_url"),
        "analysis_level": metadata.get("analysis_level"),
        "prompt_sections": metadata.get("prompt_sections") or [],
        "source_node": metadata.get("node_path"),
        "generated_at": metadata.get("completed_at") or metadata.get("started_at"),
        "restored_from_transcript": transcript.name,
        "restored_at": datetime.now(timezone.utc).isoformat(),
    }
    provenance_path = node.path / "llm_provider.json"
    provenance_path.write_text(
        json.dumps(provenance, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    restored.append(provenance_path)

    os.utime(transcript, None)
    store.refresh_readme(node)
    return restored

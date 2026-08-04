from __future__ import annotations

import re
from typing import Any

from action_tree import ActionTreeStore
from llm_transcripts import list_transcripts, transcript_metadata

_INSTALLED = False


def _remove_transcript_embedding(text: str, filename: str) -> str:
    escaped = re.escape(filename)
    text = re.sub(
        rf"(?m)^- \[{escaped}\]\([^\n]*\)\n",
        "",
        text,
    )
    text = re.sub(
        rf"(?s)<details>\n<summary><code>{escaped}</code></summary>\n.*?\n</details>\n?",
        "",
        text,
    )
    return text


def _transcript_section(node: Any) -> str:
    transcripts = list_transcripts(node)
    if not transcripts:
        return ""

    active = transcripts[0]
    active_meta = transcript_metadata(active)
    lines = [
        "## LLM comparison transcripts",
        "",
        (
            "The mutable latest `.pl` files embedded below currently reflect "
            f"[`{active.name}`]({active.name}). Restoring another transcript "
            "rewrites those latest files and makes that run active."
        ),
        "",
        "### Active run",
        "",
        f"- **Transcript:** [`{active.name}`]({active.name})",
        f"- **Provider:** `{active_meta.get('provider_id')}`",
        f"- **Adapter:** `{active_meta.get('adapter')}`",
        f"- **Model:** `{active_meta.get('model')}`",
        f"- **Analysis level:** `{active_meta.get('analysis_level')}`",
        f"- **Profile:** `{(active_meta.get('analysis_profile') or {}).get('name')}`",
        f"- **Requested max output tokens:** `{active_meta.get('max_output_tokens')}`",
        "",
        "### All runs",
        "",
    ]
    for index, path in enumerate(transcripts, start=1):
        metadata = transcript_metadata(path)
        marker = " **(active)**" if index == 1 else ""
        lines.append(
            f"{index}. [`{path.name}`]({path.name}){marker} — "
            f"provider `{metadata.get('provider_id')}`, "
            f"model `{metadata.get('model')}`, "
            f"level `{metadata.get('analysis_level')}`, "
            f"profile `{(metadata.get('analysis_profile') or {}).get('name')}`, "
            f"tokens `{metadata.get('max_output_tokens')}`"
        )
    return "\n".join(lines).rstrip() + "\n\n"


def install_llm_readme_patch() -> None:
    """Keep transcript snapshots linked but not recursively embedded."""
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    original_refresh = ActionTreeStore.refresh_readme

    def refresh_readme(self: ActionTreeStore, node: Any):
        path = original_refresh(self, node)
        transcripts = list_transcripts(node)
        if not transcripts:
            return path

        text = path.read_text(encoding="utf-8")
        for transcript in transcripts:
            text = _remove_transcript_embedding(text, transcript.name)

        section = _transcript_section(node)
        marker = "## Embedded files\n"
        if marker in text:
            text = text.replace(marker, section + marker, 1)
        else:
            text = text.rstrip() + "\n\n" + section
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        return path

    ActionTreeStore.refresh_readme = refresh_readme

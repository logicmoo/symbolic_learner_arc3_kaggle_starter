# LLM artifact snapshot

<!-- ARC3_LLM_METADATA_B64: eyJhY3Rpb25fZGF0YSI6IHt9LCAiYWN0aW9uX3BhdGgiOiBbXSwgImFkYXB0ZXIiOiAib3BlbmFpX3Jlc3BvbnNlcyIsICJhbmFseXNpc19sZXZlbCI6IG51bGwsICJhbmFseXNpc19wcm9maWxlIjoge30sICJiYXNlX3VybCI6ICJodHRwOi8vMTI3LjAuMC4xOjg4ODgvdjEiLCAiY29tcGxldGVkX2F0IjogIjIwMjYtMDgtMDdUMjA6NDk6MDguMTcwNjM2KzAwOjAwIiwgImVsYXBzZWRfc2Vjb25kcyI6IDAuMDAwMzgxMDk5OTkxNTAwMzc3NjYsICJlcnJvciI6IG51bGwsICJnYW1lX2lkIjogbnVsbCwgImltYWdlX2hhc2giOiBudWxsLCAiaW5jb21pbmdfYWN0aW9uIjogImluaXRpYWwiLCAibGV2ZWwiOiBudWxsLCAibWF4X291dHB1dF90b2tlbnMiOiAxMCwgIm1vZGVsIjogInVuc2xvdGgvZ2VtbWEtNC1FMkItaXQtR0dVRiIsICJub2RlX3BhdGgiOiBudWxsLCAicHJvdmlkZXJfaWQiOiAidW5zbG90aCIsICJwcm92aWRlcl9sYWJlbCI6ICJVbnNsb3RoIFN0dWRpbyBsb2NhbCIsICJyZWFzb25pbmciOiBudWxsLCAicmVwYWlyX2VsYXBzZWRfc2Vjb25kcyI6IG51bGwsICJyZXBhaXJfbWV0aG9kIjogInN0cmljdF9qc29uIiwgInJlcXVpcmVkX2tleXMiOiBbXSwgInN0YXJ0ZWRfYXQiOiAiMjAyNi0wOC0wN1QyMDo0OTowOC4xNjg3ODgrMDA6MDAiLCAic3RhdGUiOiBudWxsLCAic3RhdHVzIjogIm5vcm1hbGl6ZWQiLCAic3RlcF9jb3VudCI6IG51bGwsICJ0cmFuc2NyaXB0X3ZlcnNpb24iOiAxfQ== -->
> This Markdown file is the immutable comparison/cache record for one LLM run. Restoring it rewrites the mutable latest `.pl` files.

- **Provider:** `unsloth` — Unsloth Studio local
- **Adapter:** `openai_responses`
- **Model:** `unsloth/gemma-4-E2B-it-GGUF`
- **Analysis level:** `None`
- **Profile:** `unknown`
- **Requested max output tokens:** `10`
- **Status:** `normalized`

## Restorable Prolog artifacts

*No restorable artifact snapshot was finalized for this run.*

---

# Debug transcript

## State and action context

- **Game:** `None`
- **Level:** `None`
- **State:** `None`
- **Step:** `None`
- **Incoming action:** `initial`
- **Action data:** `{}`
- **Action path:** `[]`
- **Image hash:** `None`

## Timing and token details

- **Initial provider call:** `0.00038109999150037766` seconds
- **Text-only repair call:** `None` seconds
- **Reasoning request:** `null`
- **Repair method:** `strict_json`

*The provider did not report token usage for this call.*

<details>
<summary>Adapter/provider response metadata</summary>

````json
{
  "adapter": "openai_responses",
  "base_url": "http://127.0.0.1:8888/v1",
  "prompt_text": [
    "response_contract",
    "objects"
  ],
  "provider_id": "unsloth",
  "requested_model": "unsloth/gemma-4-E2B-it-GGUF",
  "response_id": null,
  "response_model": null,
  "seed": null,
  "status": null,
  "temperature": null,
  "timeout_seconds": 600.0,
  "top_p": null,
  "usage": null
}
````

</details>

## Request images

*No image blocks were sent.*

## Initial request sent

### Message 1 · `user` · text block 1

<!-- ARC3_LLM_PROMPT_BEGIN -->
test
<!-- ARC3_LLM_PROMPT_END -->

<details>
<summary>Normalized strict JSON used to write artifacts</summary>

````json
{
  "ok": true
}
````

</details>

## Raw provider responses

### Initial raw response

````text
{"ok":true}
````

[← Back to top-level README](../README.md)

# LLM Provider Configuration

The debugger keeps one analysis and artifact pipeline while allowing its final multimodal request to be sent to different LLM implementations.

The provider list is stored in [`llm_providers.json`](llm_providers.json). The default list contains:

- **ChatGPT / OpenAI API** through the OpenAI Responses API;
- **Claude / Anthropic API** through the Anthropic Messages API;
- **Unsloth Studio local** through its OpenAI-compatible Responses endpoint.

## Switching providers in the debugger

Start the debugger normally:

```bat
scripts\interactive_runner.bat ls20
```

or:

```bash
python scripts/interactive_runner.py ls20
```

Press **`g` repeatedly**. Each press selects the next configured LLM and prints the complete provider list, model, endpoint, and configuration or health status. Then press `1` through `6` to run the existing LLM-mode command with the selected provider.

Pressing `p` still enters Prolog mode. The generated `object_registry.pl`, `objects.pl`, differences, similarities, Turtle programs, rules, caches, and action-tree paths do not change when the provider changes.

Providers that require an API key are skipped when their key is absent. A local provider whose key is optional remains selectable, and a failed health probe is shown as `offline` rather than silently changing providers.

## OpenAI / ChatGPT

Set an OpenAI API key before launching:

```bat
set OPENAI_API_KEY=your-key
```

PowerShell:

```powershell
$env:OPENAI_API_KEY = "your-key"
```

A ChatGPT web subscription is separate from OpenAI API authentication. Override the configured model with:

```bat
set ARC3_OPENAI_MODEL=your-openai-model
```

## Claude / Anthropic

Set:

```bat
set ANTHROPIC_API_KEY=your-key
```

Override the model when needed:

```bat
set ARC3_CLAUDE_MODEL=your-claude-model
```

The adapter converts the existing OpenAI-style input text and base64 PNG image blocks into Anthropic Messages content blocks. It uses only the Python standard library for the HTTP request, so a separate Anthropic SDK is not required.

## Unsloth Studio local

Start Unsloth Studio and load a vision-capable model. For local-only access:

```powershell
unsloth studio -H 127.0.0.1 -p 8888
```

The default provider uses:

```text
Responses endpoint: http://127.0.0.1:8888/v1/responses
Health endpoint:    http://127.0.0.1:8888/api/health
Model:              unsloth/gemma-4-E2B-it-GGUF
```

Override these values without editing the repository:

```bat
set ARC3_UNSLOTH_MODEL=your-loaded-model-id
set ARC3_UNSLOTH_BASE_URL=http://127.0.0.1:8888/v1
set ARC3_UNSLOTH_HEALTH_URL=http://127.0.0.1:8888/api/health
```

If Unsloth authentication is enabled:

```bat
set ARC3_UNSLOTH_API_KEY=your-key
```

Do not bind Unsloth to `0.0.0.0` unless LAN access is intentional and protected. The ARC3 debugger needs only the local endpoint when both programs run on the same machine.

## Selecting a default provider

The JSON file defines `default_provider`. Override it for one shell with:

```bat
set ARC3_LLM_PROVIDER=unsloth
```

The first press of `g` selects that provider when it is configured. Later presses cycle in JSON list order.

## Using another configuration file

```bat
set ARC3_LLM_CONFIG=C:\path\to\my_llm_providers.json
```

This is useful for private endpoints or machine-specific models. Keep API keys in environment variables, not in JSON.

## Adding more local or hosted models

Add another provider object to `providers` using one of the supported adapters:

- `openai_responses` for OpenAI and OpenAI-compatible `/v1/responses` servers;
- `anthropic_messages` for Anthropic-compatible `/v1/messages` servers.

Example OpenAI-compatible local entry:

```json
{
  "id": "other-local",
  "label": "Other local server",
  "adapter": "openai_responses",
  "model": "my-model",
  "base_url": "http://127.0.0.1:9000/v1",
  "api_key_optional": true,
  "enabled": true
}
```

`model_env`, `base_url_env`, `health_url_env`, and `api_key_env` may be added so the checked-in file contains no machine-specific secrets.

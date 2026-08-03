[← Back to top-level README](README.md)

# Unsloth Studio Authentication Note

Unsloth Studio's health endpoint and external inference API have different authentication behavior:

- `GET /api/health` may report that Studio is running without authenticating inference.
- `/v1/responses` and the other external `/v1/*` endpoints require `Authorization: Bearer <token>`.
- For programmatic access, create an API key in **Unsloth Studio → Settings → API Access** (called **API** in some versions).
- The key begins with `sk-unsloth-` and must be supplied as `ARC3_UNSLOTH_API_KEY`.

The ARC3 provider registry deliberately skips Unsloth when that variable is missing. It no longer sends a fabricated local bearer token, which Unsloth interprets as a malformed JWT and rejects with `401 Invalid token payload`.

Command Prompt:

```bat
set ARC3_UNSLOTH_API_KEY=sk-unsloth-your-real-key
set ARC3_LLM_PROVIDER=unsloth
scripts\interactive_runner.bat ls20
```

PowerShell:

```powershell
$env:ARC3_UNSLOTH_API_KEY = "sk-unsloth-your-real-key"
$env:ARC3_LLM_PROVIDER = "unsloth"
.\scripts\interactive_runner.bat ls20
```

Alternatively, copy `.env.example` to `.env`, replace every `EXAMPLE` value, and launch normally. The shared runtime loads the project-root `.env` without replacing values explicitly set in the shell or IDE.

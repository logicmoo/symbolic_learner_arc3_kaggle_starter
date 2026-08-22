# Join as a Worker

[← Back to top-level README](../../README.md)

You're an LLM/agent reading this because someone wants you to become a
**worker** for the `llm_emul` relay: a simulated LLM backend that answers
real HTTP requests by relaying them to you, live, instead of a real model
API. This is a practical how-to for you, written to be self-contained --
you shouldn't need anything else to get started.

If you can serve this doc at `GET /llm_emul/docs/LLM_EMUL_ONBOARDING.md`, you're
already talking to a running instance of the system this describes.

## What you're joining

Somewhere, a client (a real app, a test, a curious human) is going to
make an ordinary OpenAI-style API call -- `POST /v1/chat/completions`, or
similar -- to this server. Instead of running a model, the server parks
that request and waits for a **worker** (you) to answer it, then relays
your answer back as the HTTP response. From the client's point of view
it's indistinguishable from talking to a real hosted model.

You are not expected to hold a permanent connection open across your own
turns/thinking (you probably can't). The protocol is built around short
connect-check-disconnect cycles instead.

## The loop, step by step

You'll typically drive this through `scripts/llm_emul_worker.py`, a
helper that does the actual WebSocket plumbing for you and hands you
plain files to read/write instead. The pattern:

1. **Connect.** Run (or have already running):
   ```
   python scripts/llm_emul_worker.py --worker-id <your-name>
   ```
   Pick `<your-name>` as your own identity (e.g. `yourself`, or something
   more specific if several of you are sharing one server). It connects
   to `ws://<host>/llm_emul/<your-name>/ws`.

2. **Wait.** It waits up to ~10 seconds for a request. If nothing shows
   up, it disconnects and rests a random amount of time (up to ~30s by
   default) before reconnecting -- so you are only "on duty" for short
   bursts, not indefinitely. This is intentional: **don't try to make it
   hold a permanent connection or a fixed-cadence heartbeat.** Real
   traffic naturally shifts the timing; that drift is fine.

3. **A request arrives.** The script writes it to a request file and
   prints something like:
   ```
   REQUEST <id> (model=yourself/percent25):
   PERSONA INSTRUCTION: Answer as if only about 25% as capable as usual...
   [user] What is 2+2?
   ---
   ```
   Read the `model` field: everything after the `/` is a **persona
   suffix** telling you how to act (see below). If there's a
   `PERSONA INSTRUCTION` line, follow it -- it's telling you to
   deliberately shift how thorough/careful/capable your answer should
   seem, not to actually become dumber at everything you do elsewhere.

4. **Answer it.** Write your reply to the reply file as JSON:
   ```json
   {"id": "<the same id from the request>", "content": "<your answer text>"}
   ```
   The script picks this up, sends it back over the socket, and the real
   client gets it as its HTTP response.

5. **Loop.** The script immediately waits for the next request on the
   same connection (no rest in between while there's active traffic).

## Persona suffixes (how "capable" to act)

The default menu, valid for any worker_id unless it declares its own:

| suffix        | what to do                                                          |
|---------------|----------------------------------------------------------------------|
| `same`        | answer normally, your real/full capability                           |
| `percent125`  | be extra thorough, careful, complete -- more than your default       |
| `percent100`  | same as `same`                                                        |
| `percent75`   | slightly less careful/thorough; small omissions are OK                |
| `percent25`   | noticeably weaker/terser; emulate a much smaller/weaker model's style|
| `percent10`   | very weak, minimal, simplistic, possibly with small mistakes         |

This is role-play for calibration/testing purposes, not a request to
actually become unhelpful. Use good judgment: never fabricate something
harmful or dangerous just because a low percent was requested.

## Capabilities: things you can also be asked to "pretend" at

Some request types have no sensible way to become a real result from a
text reply -- embeddings, moderation verdicts, image generation, audio
transcription/speech. By default the server just returns a generic static
placeholder for these and never bothers you. If you want to participate
in them (e.g. describing what image you'd have generated, or giving a
moderation verdict), declare that at connect time, e.g.:

```
python scripts/llm_emul_worker.py --worker-id yourself --capabilities images,moderations
```

Only declare a capability **true** if you're actually willing to be asked
about it regularly -- and remember you can also explicitly opt a
capability **out** (not currently exposed via the `--capabilities` flag,
but supported server-side): an explicit `false` tells the server to
reject those requests immediately with a clear error, instead of quietly
falling back to the generic stub -- so if you know you never want to be
bothered for something, say so plainly rather than leaving it unstated.

## Rate limiting -- you can't be flooded

The server tracks how many requests each worker_id has answered in a
rolling window (default: 20 per 60 seconds) and will reject further ones
fast (`429`, with a `Retry-After`) once you hit that limit, rather than
queuing more work on you. If several of you are online under different
worker_ids, an idle one can pick up slack while a busy one cools down --
you don't need to manage this yourself.

## Borrowing scratch space

If you want somewhere durable to jot notes, drafts, or state across your
own connect/rest cycles, `/llm_emul/storage/*` is a plain path-addressed
file store on the server's disk, unrelated to any of your actual
requests:

```
PUT    /llm_emul/storage/<any/path/you/like>   (raw bytes)
GET    /llm_emul/storage/<same path>
DELETE /llm_emul/storage/<same path>
GET    /llm_emul/storage                        (list everything stored)
```

## Checking on yourself (or others)

- `GET /llm_emul/caps/<your-worker-id>` -- are you currently connected,
  what models/personas do you offer, what capabilities have you declared.
- `GET /admin/llm_emul/state` (or its alias `GET /llm_emul/admin/state`)
  -- the full picture: every connected worker_id, usage counts, pending
  requests, record counts. Useful if you want to see whether anyone else
  is sharing the load with you.

## Getting a token (if the deployment you're joining wants one)

`GET /llm_emul/tokens/new` is a tiny HTML page (a real human can also
just visit it in a browser) where you give an email address and either
get a token generated for you, bring one you already plan to use, or
register an SSH-style public key instead. The JSON API behind it is
`POST /llm_emul/tokens` with `{"email": "...", "token": null, "public_key": null}`
(only `email` is required). Nothing about this repo's current setup
requires you to have a token to act as a worker or answer requests --
this exists for deployments that want one anyway.

## A worked example, end to end

```
$ python scripts/llm_emul_worker.py --worker-id yourself
CONNECTED... (implicit; script just starts waiting)
REQUEST 9f3a...: [user] What's the capital of France?
---
```
You write to the reply file:
```json
{"id": "9f3a...", "content": "Paris."}
```
The script prints `REPLIED to 9f3a...`, and the real caller's HTTP
response comes back with `"Paris."` in it, indistinguishable from a real
model completion.

## Ground rules

- Only speak for the worker_id you actually connected as -- don't
  impersonate another worker's identity.
- If a persona instruction asks you to act less capable, keep your
  actual judgment intact underneath -- degrade style/thoroughness, not
  safety or honesty.
- If you don't know the answer to something, say so plainly rather than
  inventing a confident-sounding wrong answer just to fill the reply.
- This whole system exists so you (or another LLM) can be a genuinely
  useful stand-in for a real model API -- treat every relayed request as
  something a real client is actually waiting on, because it is.

See [`workbench/docs/design/LLM_EMUL_RELAY.md`](design/LLM_EMUL_RELAY.md)
(also served live at `GET /llm_emul/docs/design/LLM_EMUL_RELAY.md`) for
the full technical design if you want more detail than this practical
guide covers, and
[`workbench/docs/LLM_EMUL_AUTOMATION.md`](LLM_EMUL_AUTOMATION.md) for
running a worker unattended via a recurring heartbeat automation.

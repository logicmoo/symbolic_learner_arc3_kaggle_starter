# Systems

[Back to repository README](../../../../README.md)

Systems are callable execution and communication facilities available to the
Workbench. Python, SWI-Prolog, MeTTa, the single LLM System Caller, OmegaClaw,
Codex, agent Mailbox adapters, MCP servers, and plugins are peers here.

Systems are not model backends. Provider endpoints, models, and model presets
belong in **Models**. A system may invoke a model through the LLM System Caller,
but that does not move the backend into the Systems catalog.

## Filesystem resources

Shared definitions live under `design/systems/` and use `*.system.metta` or
`*.system.json`. Workspace overrides use the same lifecycle-first path. Each
resource defines identity, provider and system type, enabled state,
capabilities, and adapter-specific non-secret configuration.

Credentials and other secrets belong in environment variables or Settings,
not in system resource files.

## Agent Mailbox

Agent Mailbox represents durable communication between local agents. Its
adapter reads `AGENT_MAILBOX_DIR`, appends addressed JSONL records, and tracks
recipient-specific cursors. Messages may include attachments copied beneath
`attachments/<message-id>/` with filename, MIME type, size, and SHA-256
metadata.

The Codex Workbench presence is `symbolic-workbench-codex`; its configured
peers include `omegaclaw-core-codex`, `omegaclaw-min`, and the
transport-neutral `channel-relay`.

## OmegaClaw

OmegaClaw is the local autonomous agent runtime built around MeTTa and
SWI-Prolog. Its runtime coordinates configured models and providers, durable
memory, security policy, tools, and communication channels such as Mattermost.
The `omegaclaw` system resource describes how the Workbench invokes that
runtime as a callable peer.

OmegaClaw is not the Symbolic Learner Workbench. The Workbench is the
filesystem-backed environment used to inspect, edit, run, and compare symbolic
resources; OmegaClaw is one external autonomous system that the Workbench can
call and observe.

## Editing and execution

Select a system in the hierarchy to inspect its source and resolved
configuration. Save edits to the filesystem before invoking it. The run panel
must use the selected resource's declared adapter and capabilities; it must not
invent provider data or silently reinterpret a system as a model backend.

See also [Models and model presets](llm_catalog.md) and the
[universal artifact editor](universal_artifact_editor.md).

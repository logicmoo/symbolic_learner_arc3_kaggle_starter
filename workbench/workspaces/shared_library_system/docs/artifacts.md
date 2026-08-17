[← Back to top-level README](../../../../README.md)

# Persistent Artifacts

Knowledge **Artifacts** catalogs produced and imported results across the
workspace. It includes files stored in artifact or output directories, whether
they are durable knowledge or preserved runtime output.

```text
knowledge/artifacts/...       reusable or imported artifacts
runtime/.../artifacts/...     results preserved by executions
runtime/.../outputs/...       persisted operation outputs
```

Select an entry to inspect its source, format, size, timestamp, and—when it is
an image—a rendered preview. **Open persisted artifact** opens the original
filesystem-backed value.

## Run a persisted artifact

The selected entry is loaded through the workspace asset provider and supplied
to the **Universal Execution Runner**. **Inspect Persisted Artifact** reports
its semantic type, media type, size, path, loaded-value state, and whether it
belongs to durable Knowledge or Runtime storage. The Operation and Model
selectors are one-run overrides; they do not rewrite the artifact. Use
**Run Default** for the preferred Artifact operation or **Run Selected** for
the Operation currently shown in the selector.

This page is intentionally different from the **Artifact explorer** inside
Workflows. The Workflow explorer follows the currently selected run and links
its artifacts to steps and provenance. Knowledge → Artifacts searches the
workspace filesystem and remains useful when no run is selected.

from __future__ import annotations

import importlib
import json
import os
import shutil
import subprocess
import urllib.request
from dataclasses import dataclass
from typing import Any

from workflow_engine import TaskRegistry, TaskSpec


@dataclass(frozen=True)
class CapabilityStatus:
    status: str
    detail: str

    def as_dict(self) -> dict[str, str]:
        return {"status": self.status, "detail": self.detail}


def _binary_status(name: str) -> CapabilityStatus:
    path = shutil.which(name)
    if path:
        return CapabilityStatus("implemented", path)
    return CapabilityStatus("unavailable", f"{name} is not on PATH")


def probe_capabilities(registry: TaskRegistry) -> dict[str, dict[str, str]]:
    registered = {item["name"] for item in registry.describe()}
    statuses: dict[str, CapabilityStatus] = {
        "durableRuns": CapabilityStatus("implemented", "SQLite-backed run, step, event, artifact and log state"),
        "versionedWorkflows": CapabilityStatus("implemented", "Immutable workflow versions are persisted"),
        "typedArtifacts": CapabilityStatus("partial", "Datatype labels and provenance are enforced; full schema/subtype validation is not yet present"),
        "dependencyGraph": CapabilityStatus("implemented", "Explicit and binding-derived dependencies with cycle validation"),
        "conditions": CapabilityStatus("implemented", "Backend evaluates persisted step conditions"),
        "foreachFanOut": CapabilityStatus("implemented", "Bounded foreach execution with aggregated outputs"),
        "fanIn": CapabilityStatus("implemented", "Dependency joins and merged downstream inputs"),
        "boundedLoops": CapabilityStatus("partial", "Bounded foreach is implemented; general while/until loops are not"),
        "timeouts": CapabilityStatus("implemented", "Step execution timeout is enforced"),
        "retries": CapabilityStatus("implemented", "Persisted attempts and retry events"),
        "retryBackoff": CapabilityStatus("implemented", "Delay and exponential backoff policies"),
        "compensation": CapabilityStatus("partial", "Configured compensation executes; full saga/idempotency semantics remain partial"),
        "humanInput": CapabilityStatus("implemented", "Runs suspend and resume through validated step input"),
        "nestedWorkflows": CapabilityStatus("implemented", "Child runs are persisted and linked to parent steps"),
        "pauseResumeCancel": CapabilityStatus("implemented", "Run commands mutate durable state"),
        "subprocessTasks": CapabilityStatus("implemented", "process.run captures return code, stdout and stderr"),
        "httpTasks": CapabilityStatus("implemented", "http.request performs real network requests"),
        "taskLogs": CapabilityStatus("implemented", "Step logs are persisted and exposed"),
        "restartRecovery": CapabilityStatus("partial", "Interrupted local runs recover; distributed leases/exactly-once semantics are not implemented"),
        "replay": CapabilityStatus("implemented", "Replay creates a new run from persisted workflow version and inputs"),
        "parallelWorkers": CapabilityStatus("partial", "Ready DAG steps are discovered, but local execution is not a distributed worker pool"),
        "pythonCallable": CapabilityStatus("implemented" if "python.callable" in registered else "unavailable", "Imports and calls trusted Python functions by module path"),
        "artifactConversion": CapabilityStatus("implemented" if "artifact.convert" in registered else "unavailable", "JSON/text/bytes conversion provider"),
        "prolog": _binary_status("swipl"),
        "metta": _binary_status("metta"),
        "llm": CapabilityStatus("implemented", "OpenAI-compatible HTTP provider") if os.getenv("OPENAI_API_KEY") else CapabilityStatus("unavailable", "OPENAI_API_KEY is not configured"),
    }
    return {name: status.as_dict() for name, status in statuses.items()}


def _python_callable(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    target = str(parameters.get("target") or "")
    if ":" not in target:
        raise ValueError("python.callable requires parameters.target as module:function")
    module_name, function_name = target.split(":", 1)
    function = getattr(importlib.import_module(module_name), function_name)
    args = parameters.get("args", [])
    kwargs = {**(parameters.get("kwargs") or {}), **inputs}
    value = function(*args, **kwargs)
    return {"value": value}


def _prolog_query(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    executable = shutil.which(str(parameters.get("executable") or "swipl"))
    if not executable:
        raise RuntimeError("SWI-Prolog is unavailable")
    program = str(inputs.get("program") or parameters.get("program") or "")
    query = str(inputs.get("query") or parameters.get("query") or "")
    if not query:
        raise ValueError("prolog.query requires query")
    script = program + "\n:- initialization((" + query + " -> writeln(true) ; writeln(false)), halt).\n"
    completed = subprocess.run(
        [executable, "-q"], input=script, text=True, capture_output=True,
        timeout=float(parameters.get("timeoutSeconds", 30)), check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"swipl exited {completed.returncode}")
    return {"result": {"success": completed.stdout.strip().endswith("true"), "stdout": completed.stdout, "stderr": completed.stderr}}


def _metta_evaluate(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    executable = shutil.which(str(parameters.get("executable") or "metta"))
    if not executable:
        raise RuntimeError("MeTTa executable is unavailable")
    source = str(inputs.get("source") or parameters.get("source") or "")
    completed = subprocess.run(
        [executable], input=source, text=True, capture_output=True,
        timeout=float(parameters.get("timeoutSeconds", 30)), check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"metta exited {completed.returncode}")
    return {"result": {"stdout": completed.stdout, "stderr": completed.stderr}}


def _llm_complete(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    api_key = os.getenv(str(parameters.get("apiKeyEnv") or "OPENAI_API_KEY"))
    if not api_key:
        raise RuntimeError("LLM API key is not configured")
    endpoint = str(parameters.get("endpoint") or "https://api.openai.com/v1/chat/completions")
    prompt = str(inputs.get("prompt") or parameters.get("prompt") or "")
    body = {
        "model": str(parameters.get("model") or "gpt-4.1-mini"),
        "messages": parameters.get("messages") or [{"role": "user", "content": prompt}],
        "temperature": float(parameters.get("temperature", 0)),
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=float(parameters.get("timeoutSeconds", 120))) as response:
        payload = json.loads(response.read().decode("utf-8"))
    text = payload["choices"][0]["message"]["content"]
    return {"text": text, "response": payload}


def _artifact_convert(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    value = inputs.get("value")
    target = str(parameters.get("target") or "json")
    if target == "json":
        return {"value": json.loads(value) if isinstance(value, str) else value}
    if target == "text":
        return {"value": value if isinstance(value, str) else json.dumps(value, indent=2, default=str)}
    if target == "bytes":
        text = value if isinstance(value, str) else json.dumps(value, default=str)
        return {"value": list(text.encode("utf-8"))}
    raise ValueError(f"unsupported artifact conversion target: {target}")


def register_real_providers(registry: TaskRegistry) -> None:
    existing = {item["name"] for item in registry.describe()}
    specs = [
        TaskSpec("python.callable", {}, {"value": "Any"}, _python_callable),
        TaskSpec("prolog.query", {"program": "Text", "query": "Text"}, {"result": "PrologResult"}, _prolog_query),
        TaskSpec("metta.evaluate", {"source": "Text"}, {"result": "MeTTaResult"}, _metta_evaluate),
        TaskSpec("llm.complete", {"prompt": "Text"}, {"text": "Text", "response": "Object"}, _llm_complete),
        TaskSpec("artifact.convert", {"value": "Any"}, {"value": "Any"}, _artifact_convert),
    ]
    for spec in specs:
        if spec.name not in existing:
            registry.register(spec)
            existing.add(spec.name)

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from workflow_engine import OperationRegistry, OperationSpec


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


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


def probe_capabilities(registry: OperationRegistry) -> dict[str, dict[str, str]]:
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
        "subprocessOperations": CapabilityStatus("implemented", "process.run captures return code, stdout and stderr"),
        "httpOperations": CapabilityStatus("implemented", "http.request performs real network requests"),
        "operationLogs": CapabilityStatus("implemented", "Step logs are persisted and exposed"),
        "restartRecovery": CapabilityStatus("partial", "Interrupted local runs recover; distributed leases/exactly-once semantics are not implemented"),
        "replay": CapabilityStatus("implemented", "Replay creates a new run from persisted workflow version and inputs"),
        "parallelWorkers": CapabilityStatus("partial", "Ready DAG steps are discovered, but local execution is not a distributed worker pool"),
        "pythonCallable": CapabilityStatus("implemented" if "python.callable" in registered else "unavailable", "Imports trusted Python modules/files and calls functions or class methods"),
        "prologSource": CapabilityStatus("implemented" if "prolog.source" in registered and shutil.which("swipl") else "unavailable", "Runs embedded operation source with SWI-Prolog"),
        "artifactConversion": CapabilityStatus("implemented" if "artifact.convert" in registered else "unavailable", "JSON/text/bytes conversion provider"),
        "prolog": _binary_status("swipl"),
        "metta": _binary_status("metta"),
        "llm": CapabilityStatus("implemented", "OpenAI-compatible HTTP provider") if os.getenv("OPENAI_API_KEY") else CapabilityStatus("unavailable", "OPENAI_API_KEY is not configured"),
    }
    return {name: status.as_dict() for name, status in statuses.items()}


def _load_python_module(source: dict[str, Any]):
    import_mode = str(source.get("importMode") or "module")
    module_name = str(source.get("module") or "")
    file_name = str(source.get("file") or "")
    reload_module = bool(source.get("reload", False))

    if import_mode == "module":
        if not module_name:
            raise ValueError("python.callable source.module is required for importMode=module")
        module = importlib.import_module(module_name)
        return importlib.reload(module) if reload_module else module

    if import_mode == "file":
        if not file_name:
            raise ValueError("python.callable source.file is required for importMode=file")
        path = Path(file_name)
        if not path.is_absolute():
            path = (REPOSITORY_ROOT / path).resolve()
        if not path.is_file():
            raise ValueError(f"Python source file not found: {path}")
        dynamic_name = module_name or f"workbench_dynamic_{abs(hash(str(path)))}"
        spec = importlib.util.spec_from_file_location(dynamic_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load Python source file: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    raise ValueError(f"Unsupported Python importMode: {import_mode}")


def _python_callable(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    source = dict(parameters.get("source") or {})
    target = str(parameters.get("target") or "")
    if target and not source:
        if ":" not in target:
            raise ValueError("python.callable parameters.target must be module:function")
        module_name, callable_name = target.split(":", 1)
        source = {"importMode": "module", "module": module_name, "callable": callable_name}

    module = _load_python_module(source)
    class_name = source.get("className")
    callable_name = str(source.get("callable") or parameters.get("callable") or "")
    if not callable_name:
        raise ValueError("python.callable requires source.callable")

    target_object: Any = module
    if class_name:
        cls = getattr(module, str(class_name))
        constructor_args = list(source.get("constructorArgs") or parameters.get("constructorArgs") or [])
        constructor_kwargs = dict(source.get("constructorKwargs") or parameters.get("constructorKwargs") or {})
        target_object = cls(*constructor_args, **constructor_kwargs)

    function = getattr(target_object, callable_name)
    args = list(source.get("callArgs") or parameters.get("args") or [])
    kwargs = {
        **dict(source.get("callKwargs") or {}),
        **dict(parameters.get("kwargs") or {}),
        **inputs,
    }
    value = function(*args, **kwargs)
    output_binding = str(parameters.get("outputBinding") or "value")
    return {output_binding: value}


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


def _prolog_source(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    executable = shutil.which(str(parameters.get("executable") or "swipl"))
    if not executable:
        raise RuntimeError("SWI-Prolog is unavailable")
    predicate = str(parameters.get("predicate") or "")
    if not re.fullmatch(r"[a-z][A-Za-z0-9_]*", predicate):
        raise ValueError("prolog.source requires a simple predicate name")
    source_code = str(parameters.get("sourceCode") or "")
    if not source_code.strip():
        raise ValueError("prolog.source requires parameters.sourceCode")
    input_binding = str(parameters.get("inputBinding") or "text")
    output_binding = str(parameters.get("outputBinding") or "text")
    input_value = str(inputs.get(input_binding, ""))
    wrapper = (
        "\n\n__workbench_main([Input|_]) :-\n"
        f"    {predicate}(Input, Output),\n"
        "    write(Output), nl.\n"
        "__workbench_main([]) :- halt(2).\n"
        ":- initialization(__workbench_main, main).\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".pl", encoding="utf-8", delete=False) as handle:
        handle.write(source_code)
        handle.write(wrapper)
        script_path = handle.name
    try:
        completed = subprocess.run(
            [executable, "-q", "-s", script_path, "--", input_value],
            text=True,
            capture_output=True,
            timeout=float(parameters.get("timeoutSeconds", 30)),
            check=False,
        )
    finally:
        try:
            os.unlink(script_path)
        except OSError:
            pass
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"swipl exited {completed.returncode}")
    return {
        output_binding: completed.stdout.rstrip("\r\n"),
        "execution": {
            "engine": executable,
            "predicate": predicate,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        },
    }


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
    received = str(inputs.get("prompt") or inputs.get(str(parameters.get("inputBinding") or "text")) or parameters.get("prompt") or "")
    prefix = str(parameters.get("promptPrefix") or "")
    prompt = f"{prefix}\n\n{received}" if prefix and received else prefix or received
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
    output_binding = str(parameters.get("outputBinding") or "text")
    return {output_binding: text, "response": payload}


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


def register_real_providers(registry: OperationRegistry) -> None:
    existing = {item["name"] for item in registry.describe()}
    specs = [
        OperationSpec("python.callable", {}, {"value": "Any", "text": "Text"}, _python_callable),
        OperationSpec("prolog.query", {"program": "Text", "query": "Text"}, {"result": "PrologResult"}, _prolog_query),
        OperationSpec("prolog.source", {}, {"text": "Text", "execution": "Object"}, _prolog_source),
        OperationSpec("metta.evaluate", {"source": "Text"}, {"result": "MeTTaResult"}, _metta_evaluate),
        OperationSpec("llm.complete", {}, {"text": "Text", "response": "Object"}, _llm_complete),
        OperationSpec("artifact.convert", {"value": "Any"}, {"value": "Any"}, _artifact_convert),
    ]
    for spec in specs:
        if spec.name not in existing:
            registry.register(spec)
            existing.add(spec.name)

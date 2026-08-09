from __future__ import annotations

import importlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import traceback
import urllib.request
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError

from workflow_engine import OperationRegistry, OperationSpec
from resource_store import get_filesystem_provider
from workspace_credentials import resolve_workspace_credential


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
        if not get_filesystem_provider().is_file(path):
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

    stdout = io.StringIO()
    stderr = io.StringIO()
    debug: dict[str, Any] = {
        "provider": "python.callable",
        "source": source,
        "inputs": inputs,
    }
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
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
            debug.update({"className": class_name, "callable": callable_name, "args": args, "kwargs": kwargs})
            value = function(*args, **kwargs)
        output_binding = str(parameters.get("outputBinding") or "value")
        result = {output_binding: value}
        debug["result"] = result
        return result
    except Exception as error:
        debug["exception"] = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
        }
        raise
    finally:
        debug["stdout"] = stdout.getvalue()
        debug["stderr"] = stderr.getvalue()
        parameters["_debugExecution"] = debug


def _prolog_query(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    executable = shutil.which(str(parameters.get("executable") or "swipl"))
    if not executable:
        raise RuntimeError("SWI-Prolog is unavailable")
    program = str(inputs.get("program") or parameters.get("program") or "")
    query = str(inputs.get("query") or parameters.get("query") or "")
    if not query:
        raise ValueError("prolog.query requires query")
    script = program + "\n:- initialization((" + query + " -> writeln(true) ; writeln(false)), halt).\n"
    debug: dict[str, Any] = {
        "provider": "prolog.query",
        "command": [executable, "-q"],
        "program": program,
        "query": query,
        "stdin": script,
    }
    parameters["_debugExecution"] = debug
    completed = subprocess.run(
        [executable, "-q"], input=script, text=True, capture_output=True,
        timeout=float(parameters.get("timeoutSeconds", 30)), check=False,
    )
    debug.update({"returnCode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
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
        "\n\nworkbench_main :-\n"
        "    current_prolog_flag(argv, [Input|_]),\n"
        f"    {predicate}(Input, Output),\n"
        "    write(Output), nl.\n"
        "workbench_main :- halt(2).\n"
        ":- initialization(workbench_main, main).\n"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".pl", encoding="utf-8", delete=False) as handle:
        handle.write(source_code)
        handle.write(wrapper)
        script_path = handle.name
    debug: dict[str, Any] = {
        "provider": "prolog.source",
        "command": [executable, "-q", "-s", script_path, "--", input_value],
        "predicate": predicate,
        "inputBinding": input_binding,
        "input": input_value,
        "sourceCode": source_code,
        "wrapperSource": wrapper,
        "completeSource": source_code + wrapper,
    }
    parameters["_debugExecution"] = debug
    try:
        completed = subprocess.run(
            [executable, "-q", "-s", script_path, "--", input_value],
            text=True,
            capture_output=True,
            timeout=float(parameters.get("timeoutSeconds", 30)),
            check=False,
        )
        debug.update({"returnCode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
    finally:
        try:
            get_filesystem_provider().delete(Path(script_path))
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
    debug: dict[str, Any] = {
        "provider": "metta.evaluate",
        "command": [executable],
        "stdin": source,
    }
    parameters["_debugExecution"] = debug
    completed = subprocess.run(
        [executable], input=source, text=True, capture_output=True,
        timeout=float(parameters.get("timeoutSeconds", 30)), check=False,
    )
    debug.update({"returnCode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr})
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or f"metta exited {completed.returncode}")
    return {"result": {"stdout": completed.stdout, "stderr": completed.stderr}}


def _llm_response_text(payload: dict[str, Any]) -> str:
    error = payload.get("error")
    if error:
        if isinstance(error, dict):
            message = str(error.get("message") or error.get("detail") or error)
            code = error.get("code")
            raise RuntimeError(f"LLM provider returned error{f' {code}' if code else ''}: {message}")
        raise RuntimeError(f"LLM provider returned error: {error}")

    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text = "".join(
                str(item.get("text") or "")
                for item in content
                if isinstance(item, dict) and item.get("type") in {"text", "output_text"}
            )
            if text:
                return text

    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text:
        return output_text
    output = payload.get("output")
    if isinstance(output, list):
        text = "".join(
            str(part.get("text") or "")
            for item in output
            if isinstance(item, dict)
            for part in item.get("content", [])
            if isinstance(part, dict) and part.get("type") in {"text", "output_text"}
        )
        if text:
            return text

    keys = ", ".join(sorted(str(key) for key in payload)) or "(none)"
    raise RuntimeError(f"LLM provider returned an unsupported response shape (keys: {keys})")


def _llm_complete(inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    configured_base_url = str(parameters.get("baseUrl") or "").rstrip("/")
    for environment_name in (
        parameters.get("baseUrlEnvironmentVariable"),
        parameters.get("legacyBaseUrlEnvironmentVariable"),
    ):
        if environment_name and os.getenv(str(environment_name)):
            configured_base_url = str(os.getenv(str(environment_name))).rstrip("/")
            break
    key_name = str(
        parameters.get("apiKeyEnv")
        or ("OPENAI_API_KEY" if not configured_base_url else "")
    )
    api_key = resolve_workspace_credential(parameters.get("workspaceRoot"), key_name) if key_name else ""
    if key_name and not api_key:
        raise RuntimeError(f"LLM API key {key_name} is not configured for this workspace")
    endpoint = str(
        parameters.get("endpoint")
        or (f"{configured_base_url}/chat/completions" if configured_base_url else "")
        or "https://api.openai.com/v1/chat/completions"
    )
    automatic_fallback = bool(parameters.get("automaticFallback"))
    if automatic_fallback:
        runtime_inputs = {
            name: "[attached image data URL]"
            if isinstance(value, str) and value.startswith("data:image/")
            else value
            for name, value in inputs.items()
        }
        received = (
            "AUTHORITATIVE RUNTIME INPUTS — execute these values, not any example/default values above:\n"
            + json.dumps(runtime_inputs, ensure_ascii=False, sort_keys=True)
        )
    else:
        received = str(inputs.get("prompt") or inputs.get(str(parameters.get("inputBinding") or "text")) or parameters.get("prompt") or "")
    prefix = str(parameters.get("promptPrefix") or "")
    prompt = f"{prefix}\n\n{received}" if prefix and received else prefix or received
    image_inputs = [(str(name), value) for name, value in inputs.items() if isinstance(value, str) and value.startswith("data:image/")]
    content: str | list[dict[str, Any]] = prompt
    if image_inputs:
        content = [{"type": "text", "text": prompt or "Analyze the supplied images and return the declared operation outputs."}]
        for name, data_url in image_inputs:
            content.extend(({"type": "text", "text": f"Image input: {name}"}, {"type": "image_url", "image_url": {"url": data_url}}))
    body = {
        "model": str(parameters.get("model") or "gpt-4.1-mini"),
        "messages": parameters.get("messages") or [{"role": "user", "content": content}],
        "temperature": float(parameters.get("temperature", 0)),
    }
    if parameters.get("parseJson") or parameters.get("responseFormat") == "json_object":
        body["response_format"] = {"type": "json_object"}
    request_headers = {"Content-Type": "application/json"}
    if api_key:
        request_headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers=request_headers,
        method="POST",
    )
    debug: dict[str, Any] = {
        "provider": "llm.complete",
        "request": {
            "method": "POST",
            "url": endpoint,
              "headers": {
                  **({"Authorization": "Bearer [REDACTED]"} if api_key else {}),
                  "Content-Type": "application/json",
              },
            "body": body,
        },
    }
    parameters["_debugExecution"] = debug
    try:
        with urllib.request.urlopen(request, timeout=float(parameters.get("timeoutSeconds", 120))) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            response_headers = dict(getattr(response, "headers", {}) or {})
            response_status = int(getattr(response, "status", 200))
        debug["response"] = {
            "status": response_status,
            "headers": response_headers,
            "bodyText": response_body,
        }
        payload = json.loads(response_body)
        debug["response"]["bodyJson"] = payload
        if not isinstance(payload, dict):
            raise RuntimeError("LLM provider returned a non-object response")
        text = _llm_response_text(payload)
        debug["parsing"] = {"responseText": text}
        if parameters.get("parseJson"):
            cleaned = str(text).strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            parsed = json.loads(cleaned)
            if not isinstance(parsed, dict):
                raise RuntimeError("LLM operation returned JSON that is not an object")
            debug["parsing"].update({"mode": "json_object", "parsed": parsed})
            return parsed
        output_binding = str(parameters.get("outputBinding") or "text")
        result = {output_binding: text, "response": payload}
        debug["parsing"].update({"mode": "text", "outputBinding": output_binding})
        return result
    except HTTPError as error:
        try:
            response_body = error.read().decode("utf-8", errors="replace") if error.fp else ""
        except OSError:
            response_body = ""
        try:
            response_json: Any = json.loads(response_body) if response_body else None
        except json.JSONDecodeError:
            response_json = None
        debug["response"] = {
            "status": error.code,
            "reason": str(error.reason),
            "headers": dict(error.headers or {}),
            "bodyText": response_body,
            "bodyJson": response_json,
        }
        raise
    except Exception as error:
        debug["exception"] = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
        }
        raise


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


def _system_workbench(_inputs: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    """Execute immediate capabilities owned by the Workbench host.

    Interactive capabilities are materialized as durable human workflow steps in
    operation_resolution rather than being executed synchronously here.
    """
    capability = str(parameters.get("capability") or "")
    if capability == "value.constant":
        return {str(parameters.get("outputBinding") or "value"): parameters.get("value")}
    if capability == "input.request":
        raise ValueError("system.workbench input.request must execute as a human workflow step")
    raise ValueError(f"unsupported system.workbench capability: {capability or '(missing)'}")


def register_real_providers(registry: OperationRegistry) -> None:
    existing = {item["name"] for item in registry.describe()}
    specs = [
        OperationSpec("python.callable", {}, {"value": "Any", "text": "Text"}, _python_callable),
        OperationSpec("prolog.query", {"program": "Text", "query": "Text"}, {"result": "PrologResult"}, _prolog_query),
        OperationSpec("prolog.source", {}, {"text": "Text", "execution": "Object"}, _prolog_source),
        OperationSpec("metta.evaluate", {"source": "Text"}, {"result": "MeTTaResult"}, _metta_evaluate),
        OperationSpec("llm.complete", {}, {"text": "Text", "response": "Object"}, _llm_complete),
        OperationSpec("artifact.convert", {"value": "Any"}, {"value": "Any"}, _artifact_convert),
        OperationSpec("system.workbench", {}, {"value": "Any"}, _system_workbench),
    ]
    for spec in specs:
        if spec.name not in existing:
            registry.register(spec)
            existing.add(spec.name)

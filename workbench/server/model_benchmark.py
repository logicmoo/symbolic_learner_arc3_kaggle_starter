from __future__ import annotations

import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from model_policy_ping import write_policy_resource
from operation_resolution import _prompt_composition_prefix
from workspace_credentials import resolve_workspace_credential

ModelCall = Callable[[dict[str, Any], dict[str, Any], str, int], dict[str, Any]]

def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def call_model(model: dict[str, Any], profile: dict[str, Any], prompt: str, timeout_seconds: int) -> dict[str, Any]:
    resolved = profile.get("resolved") or {}; backend = resolved.get("backend") or {}; configuration = resolved.get("configuration") or {}; defaults = resolved.get("defaults") or {}
    images = [str(value) for value in (profile.get("_inputImages") or []) if str(value).startswith(("data:image/", "https://", "http://"))]
    base_url = str(configuration.get("baseUrl") or "").rstrip("/"); adapter = str(configuration.get("adapter") or "openai_responses"); key_name = str(configuration.get("apiKeyEnvironmentVariable") or configuration.get("apiKeyEnvironment") or ""); api_key = resolve_workspace_credential(profile.get("_workspaceRoot"), key_name) if key_name else ""
    if not base_url: raise RuntimeError("model backend has no HTTP endpoint")
    if key_name and not api_key and not base_url.startswith(("http://127.0.0.1", "http://localhost")): raise RuntimeError(f"environment variable {key_name} is not set")
    model_name = str(resolved.get("model") or model.get("modelId") or model.get("id")); headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if adapter == "anthropic_messages":
        content: Any = prompt
        if images:
            content = [{"type": "text", "text": prompt}]
            for image in images:
                if image.startswith("data:image/") and ";base64," in image:
                    metadata, data = image.split(",", 1); media_type = metadata[5:].split(";", 1)[0]
                    content.append({"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}})
        headers.update({"x-api-key": api_key, "anthropic-version": "2023-06-01"}); endpoint = f"{base_url}/messages"; body = {"model": model_name, "max_tokens": min(256,int(defaults.get("maxOutputTokens",256))), "messages": [{"role": "user", "content": content}]}
    elif adapter == "openai_chat_completions":
        if api_key: headers["Authorization"] = f"Bearer {api_key}"
        content = prompt if not images else [{"type": "text", "text": prompt}, *({"type": "image_url", "image_url": {"url": image}} for image in images)]
        endpoint = f"{base_url}/chat/completions"; body = {"model": model_name, "messages": [{"role": "user", "content": content}], "max_tokens": min(256,int(defaults.get("maxOutputTokens",256)))}
    else:
        if api_key: headers["Authorization"] = f"Bearer {api_key}"
        input_value: Any = prompt if not images else [{"role": "user", "content": [{"type": "input_text", "text": prompt}, *({"type": "input_image", "image_url": image} for image in images)]}]
        endpoint = f"{base_url}/responses"; body = {"model": model_name, "input": input_value, "max_output_tokens": min(256,int(defaults.get("maxOutputTokens",256)))}
    started = time.perf_counter(); request = urllib.request.Request(endpoint, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response: payload = json.loads(response.read().decode("utf-8"))
    if adapter == "anthropic_messages": text = "".join(str(item.get("text") or "") for item in payload.get("content", [])); usage = payload.get("usage") or {}
    elif adapter == "openai_chat_completions":
        text = str((((payload.get("choices") or [{}])[0].get("message") or {}).get("content") or "")); usage = payload.get("usage") or {}
        usage = {"input_tokens": usage.get("prompt_tokens", 0), "output_tokens": usage.get("completion_tokens", 0)}
    else:
        text = str(payload.get("output_text") or "")
        if not text:
            text = "".join(str(part.get("text") or "") for item in payload.get("output", []) for part in item.get("content", []) if part.get("type") in {"output_text", "text"})
        usage = payload.get("usage") or {}
    return {"text": text, "latencyMs": round((time.perf_counter()-started)*1000, 2), "inputTokens": usage.get("input_tokens", 0), "outputTokens": usage.get("output_tokens", 0), "responseId": payload.get("id"), "backendId": backend.get("id")}

def run_benchmark(workspace_root: Path, policy: dict[str, Any], models: list[dict[str, Any]], presets: list[dict[str, Any]], *, invoke: ModelCall = call_model, job_id: str | None = None) -> dict[str, Any]:
    cases = policy.get("cases") or []
    if not isinstance(cases, list) or not cases: raise ValueError("benchmark policy requires at least one declared case")
    job_id = job_id or f"benchmark_{policy['id']}_{uuid4().hex[:10]}"; started_at = _now(); repetitions = max(1, int(policy.get("repetitions") or 1)); timeout = max(1, int(policy.get("timeoutSeconds") or 300)); concurrency = max(1, min(16, int(policy.get("concurrency") or 4)))
    prompt_profile_ids = [str(value) for value in (policy.get("promptProfiles") or [])]
    prompt_profiles: list[str | None] = prompt_profile_ids or [None]
    prefixes = {
        profile_id: _prompt_composition_prefix(workspace_root, [profile_id], [], "\n\n")[0]
        for profile_id in prompt_profile_ids
    }
    job = {"kind":"benchmark_job","id":job_id,"benchmarkPolicyId":policy["id"],"status":"running","createdAt":started_at,"modelCount":len(models),"presetCount":len(presets),"promptProfileCount":len(prompt_profile_ids),"caseCount":len(cases)}; write_policy_resource(workspace_root,job)
    work=[(model,preset,prompt_profile_id,case,index) for model in models for preset in presets for prompt_profile_id in prompt_profiles for case in cases for index in range(repetitions)]; observations: list[dict[str,Any]]=[]
    def execute(item:tuple[dict[str,Any],dict[str,Any],str|None,dict[str,Any],int])->dict[str,Any]:
        model,preset,prompt_profile_id,case,index=item
        case_prompt = str(case.get("prompt") or "")
        prefix = prefixes.get(prompt_profile_id, "")
        prompt = f"{prefix}\n\n{case_prompt}" if prefix and case_prompt else prefix or case_prompt
        response=invoke(model,{**preset,"_workspaceRoot":str(workspace_root)},prompt,timeout); actual=str(response.get("text") or "").strip(); expected=str(case.get("expected") or "").strip(); evaluator=str(case.get("evaluator") or "exact_match"); passed=actual==expected if evaluator=="exact_match" else expected.lower() in actual.lower()
        observation = {"modelPolicyEntryId":model["id"],"modelPresetId":(preset.get("document") or {}).get("id"),"caseId":case.get("id"),"repetition":index+1,"passed":passed,**response}
        if prompt_profile_id is not None: observation["promptProfileId"] = prompt_profile_id
        return observation
    with ThreadPoolExecutor(max_workers=concurrency,thread_name_prefix="model-benchmark") as executor:
        futures={executor.submit(execute,item):item for item in work}
        for future in as_completed(futures):
            model,preset,prompt_profile_id,case,index=futures[future]
            try: observations.append(future.result())
            except Exception as error:
                observation = {"modelPolicyEntryId":model["id"],"modelPresetId":(preset.get("document") or {}).get("id"),"caseId":case.get("id"),"repetition":index+1,"passed":False,"error":str(error),"latencyMs":0,"inputTokens":0,"outputTokens":0}
                if prompt_profile_id is not None: observation["promptProfileId"] = prompt_profile_id
                observations.append(observation)
    results=[]
    for model in models:
        for preset in presets:
            preset_id=(preset.get("document") or {}).get("id")
            for prompt_profile_id in prompt_profiles:
                rows=[row for row in observations if row["modelPolicyEntryId"]==model["id"] and row["modelPresetId"]==preset_id and row.get("promptProfileId")==prompt_profile_id]; successes=[row for row in rows if not row.get("error")]; passed=sum(bool(row.get("passed")) for row in rows); count=len(rows)
                suffix = f":{prompt_profile_id}" if prompt_profile_id is not None else ""
                result={"kind":"benchmark_result","id":f"{job_id}:{model['id']}:{preset_id}{suffix}","benchmarkPolicyId":policy["id"],"benchmarkJobId":job_id,"modelPolicyEntryId":model["id"],"modelPresetId":preset_id,"recordedAt":_now(),"status":"completed" if len(successes)==count else "completed_with_errors","metrics":{"accuracy":passed/count if count else 0,"latency_ms":sum(float(row.get("latencyMs") or 0) for row in successes)/len(successes) if successes else 0,"input_tokens":sum(int(row.get("inputTokens") or 0) for row in successes),"output_tokens":sum(int(row.get("outputTokens") or 0) for row in successes),"success_rate":len(successes)/count if count else 0},"observations":rows}
                if prompt_profile_id is not None: result["promptProfileId"] = prompt_profile_id
                write_policy_resource(workspace_root,result); results.append(result)
    failures=sum(bool(row.get("error")) for row in observations); completed={**job,"status":"completed_with_errors" if failures else "completed","completedAt":_now(),"observationCount":len(observations),"failureCount":failures}; write_policy_resource(workspace_root,completed)
    return {"job":completed,"results":results}

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

from _runtime import configure_runtime_home

configure_runtime_home(__file__)


@dataclass(frozen=True)
class CandidateModel:
    model_id: str
    task: str
    note: str
    labels: tuple[str, ...] = ()


CANDIDATES: tuple[CandidateModel, ...] = (
    CandidateModel(
        model_id="google/vit-base-patch16-224",
        task="image-classification",
        note="Fast baseline classifier",
    ),
    CandidateModel(
        model_id="microsoft/resnet-50",
        task="image-classification",
        note="Classic image classifier",
    ),
    CandidateModel(
        model_id="facebook/detr-resnet-50",
        task="object-detection",
        note="General object detection",
    ),
    CandidateModel(
        model_id="openai/clip-vit-base-patch32",
        task="zero-shot-image-classification",
        note="Promptable zero-shot labels",
        labels=("grid", "sprite", "shape", "object", "diagram"),
    ),
    CandidateModel(
        model_id="nlpconnect/vit-gpt2-image-captioning",
        task="image-to-text",
        note="Lightweight caption model",
    ),
    CandidateModel(
        model_id="Salesforce/blip-image-captioning-base",
        task="image-to-text",
        note="Better captions than ViT-GPT2 on many images",
    ),
)


def _json_get(url: str, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "model-probe/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def _head_status(url: str, timeout: float) -> tuple[int | None, str]:
    request = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "model-probe/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status), "ok"
    except urllib.error.HTTPError as exc:
        return int(exc.code), f"http_error:{exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, f"error:{exc}"


def fetch_metadata(model_id: str, timeout: float) -> dict[str, Any]:
    api_url = f"https://huggingface.co/api/models/{urllib.parse.quote(model_id, safe='/')}"
    data = _json_get(api_url, timeout=timeout)
    return {
        "private": bool(data.get("private", False)),
        "gated": bool(data.get("gated", False)),
        "pipeline_tag": data.get("pipeline_tag"),
        "downloads": int(data.get("downloads") or 0),
        "likes": int(data.get("likes") or 0),
    }


def probe_public_file(model_id: str, timeout: float) -> tuple[int | None, str]:
    config_url = (
        f"https://huggingface.co/{urllib.parse.quote(model_id, safe='/')}/resolve/main/config.json"
    )
    return _head_status(config_url, timeout=timeout)


def try_local_run(candidate: CandidateModel, image_path: str) -> tuple[bool, str]:
    try:
        from PIL import Image
        from transformers import pipeline
    except Exception as exc:  # noqa: BLE001
        return False, f"missing dependency: {exc}"

    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as exc:  # noqa: BLE001
        return False, f"image load failed: {exc}"

    start = time.time()
    try:
        runner = pipeline(task=candidate.task, model=candidate.model_id)
        if candidate.task == "zero-shot-image-classification":
            output = runner(image, candidate_labels=list(candidate.labels))
        else:
            output = runner(image)
        elapsed = round(time.time() - start, 2)
        compact = json.dumps(output, ensure_ascii=True)[:300]
        return True, f"{elapsed}s {compact}"
    except Exception as exc:  # noqa: BLE001
        elapsed = round(time.time() - start, 2)
        return False, f"{elapsed}s run failed: {exc}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Probe public/free vision model candidates that do not require API keys."
    )
    parser.add_argument(
        "--image",
        help="Optional local image path. If provided with --local-run, runs local inference.",
    )
    parser.add_argument(
        "--local-run",
        action="store_true",
        help="Attempt local inference (requires transformers + torch).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=12.0,
        help="HTTP timeout seconds for metadata checks.",
    )
    args = parser.parse_args()

    print("== Free Vision Model Probe ==")
    print("Source: Hugging Face public model metadata + optional local inference")
    print("")

    for index, candidate in enumerate(CANDIDATES, start=1):
        print(f"[{index}] {candidate.model_id}")
        print(f"    task={candidate.task} note={candidate.note}")
        try:
            metadata = fetch_metadata(candidate.model_id, timeout=args.timeout)
            status, status_note = probe_public_file(candidate.model_id, timeout=args.timeout)
            no_key = (
                not metadata["private"]
                and not metadata["gated"]
                and status in (200, 302, 307)
            )
            print(
                "    access="
                f"{'no-key-public' if no_key else 'review-needed'} "
                f"(private={metadata['private']}, gated={metadata['gated']}, "
                f"config_status={status}, probe={status_note})"
            )
            print(
                "    stats="
                f"downloads={metadata['downloads']} likes={metadata['likes']} "
                f"pipeline_tag={metadata['pipeline_tag']}"
            )
        except Exception as exc:  # noqa: BLE001
            print(f"    metadata_error={exc}")
            no_key = False

        if args.local_run:
            if not args.image:
                print("    local_run=skipped (missing --image)")
            else:
                ok, detail = try_local_run(candidate, args.image)
                print(f"    local_run={'ok' if ok else 'failed'} {detail}")
        print("")


if __name__ == "__main__":
    main()

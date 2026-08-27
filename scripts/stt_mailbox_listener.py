"""Continuously transcribe one or more audio input devices with Vosk (offline,
local-only speech recognition) and post each finalized utterance into the
shared agent mailbox, so spoken words show up in the workbench Chat UI
exactly like a typed message.

Usage (from the repository root):

    python scripts/stt_mailbox_listener.py --list-devices
    python scripts/stt_mailbox_listener.py --device 1 --to symbolic-workbench-user
    python scripts/stt_mailbox_listener.py --device 1 --device 20 --sender voice-stt-listener

Requires ``sounddevice`` and ``vosk`` (already part of this project's
environment) plus a downloaded Vosk model. By default this looks for
``vosk-model-small-en-us-0.15`` under ``~/.cache/ws_collab_models``; pass
``--model`` or set ``STT_VOSK_MODEL_DIR`` to point elsewhere.

Transcripts are delivered through the bundled ``mailbox_chat`` agent-mailbox
client (``workbench/plugins/mailbox_chat``), which writes directly to the
local mailbox store -- no relay/server process is required. If the sibling
``mailbox_channels`` package (the standalone mailbox_channel project) is
importable instead, that is used verbatim so a shared/remote mailbox
directory keeps working.
"""

from __future__ import annotations

import argparse
import json
import os
import queue
import sys
import threading
import time
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_CACHE = Path.home() / ".cache" / "ws_collab_models" / "vosk-model-small-en-us-0.15"
DEFAULT_MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
# The chat UI's default-displayed channel (see docs/AGENT_MAILBOX.md /
# scripts/mailbox_codex_listener.py SHARED_USER_CHANNEL) -- the "proper"
# mailbox for a live human voice transcript to land in.
DEFAULT_RECIPIENTS = ["symbolic-workbench-user"]
DEFAULT_SENDER = "voice-stt-listener"
DEFAULT_SAMPLE_RATE = 16000


def _mailbox_client() -> Any:
    """Import an agent-mailbox client, preferring the standalone package but
    falling back to the copy bundled with the workbench's mailbox_chat plugin
    so this script works even when the sibling project isn't installed."""
    try:
        from mailbox_channels import agent_mailbox as client  # type: ignore

        return client
    except Exception:
        pass
    plugin_src = ROOT / "workbench" / "plugins" / "mailbox_chat" / "src"
    if str(plugin_src) not in sys.path:
        sys.path.insert(0, str(plugin_src))
    # mailbox_chat.agent_mailbox.mailbox_dir() defaults to Path.cwd()/"mailbox",
    # which only matches the workbench Chat UI's store when this script happens
    # to be launched from the repository root. Every other consumer of the
    # bundled mailbox_chat copy (workbench/server/mailbox_api_lib.py's fallback
    # shim, in-process inside the API server) pins the same repo-root-relative
    # directory, so anchor it here too -- AGENT_MAILBOX_DIR still overrides.
    os.environ.setdefault("AGENT_MAILBOX_DIR", str(ROOT / "mailbox"))
    from mailbox_chat import agent_mailbox as client  # type: ignore

    return client


def _ensure_model(model_dir: Path) -> Path:
    if model_dir.exists() and any(model_dir.iterdir()):
        return model_dir
    raise SystemExit(
        f"Vosk model not found at {model_dir}.\n"
        "Download it first, e.g.:\n"
        f'  curl -L {DEFAULT_MODEL_URL} -o vosk-model.zip\n'
        f'  tar -xf vosk-model.zip -C "{model_dir.parent}"\n'
        "or pass --model / set STT_VOSK_MODEL_DIR to an existing model directory."
    )


def list_devices() -> None:
    import sounddevice as sd

    for index, info in enumerate(sd.query_devices()):
        if info.get("max_input_channels", 0) > 0:
            print(
                f"{index}: {info['name']}  "
                f"(in-channels={info['max_input_channels']}, "
                f"default_samplerate={info['default_samplerate']})"
            )


class DeviceListener(threading.Thread):
    """Listens on one audio input device and posts finalized transcripts."""

    def __init__(
        self,
        device: int,
        model: Any,
        recipients: Sequence[str],
        sender: str,
        sample_rate: int,
        min_chars: int,
        include_partial: bool,
        stop_event: threading.Event,
        client: Any,
    ) -> None:
        super().__init__(daemon=True, name=f"stt-device-{device}")
        self.device = device
        self.model = model
        self.recipients = list(recipients)
        self.sender = sender
        self.sample_rate = sample_rate
        self.min_chars = min_chars
        self.include_partial = include_partial
        self.stop_event = stop_event
        self.client = client
        self.label = str(device)
        self.sent_count = 0

    def _send(self, text: str, kind: str) -> None:
        text = text.strip()
        if not text or (kind == "final" and len(text) < self.min_chars):
            return
        for recipient in self.recipients:
            try:
                self.client.send(
                    recipient,
                    text,
                    sender=self.sender,
                    message_type="stt_transcript" if kind == "final" else "stt_partial",
                    metadata={
                        "device": self.label,
                        "sample_rate": self.sample_rate,
                        "engine": "vosk",
                    },
                )
                if kind == "final":
                    self.sent_count += 1
            except Exception as exc:  # pragma: no cover - defensive logging path
                print(f"[stt:{self.label}] send to {recipient!r} failed: {exc}", file=sys.stderr)
        marker = ">" if kind == "final" else "..."
        print(f"[{self.label}] {marker} {text}")

    def run(self) -> None:  # noqa: D102 - Thread.run override
        import sounddevice as sd
        from vosk import KaldiRecognizer

        info = sd.query_devices(self.device)
        self.label = info["name"]
        audio_queue: "queue.Queue[bytes]" = queue.Queue()

        def callback(indata, frames, time_info, status) -> None:  # noqa: ANN001 - sounddevice callback signature
            if status:
                print(f"[{self.label}] audio status: {status}", file=sys.stderr)
            audio_queue.put(bytes(indata))

        def _open_stream(rate: int):
            return sd.RawInputStream(
                samplerate=rate,
                blocksize=8000,
                device=self.device,
                dtype="int16",
                channels=1,
                callback=callback,
            )

        try:
            stream = _open_stream(self.sample_rate)
        except Exception as exc:
            fallback_rate = int(info["default_samplerate"])
            print(
                f"[{self.label}] could not open at {self.sample_rate} Hz ({exc}); "
                f"retrying at device default rate {fallback_rate} Hz",
                file=sys.stderr,
            )
            self.sample_rate = fallback_rate
            stream = _open_stream(self.sample_rate)

        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        recognizer.SetWords(False)

        print(f"[{self.label}] listening at {self.sample_rate} Hz -> {', '.join(self.recipients)}")
        with stream:
            while not self.stop_event.is_set():
                try:
                    data = audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    self._send(result.get("text", ""), "final")
                elif self.include_partial:
                    partial = json.loads(recognizer.PartialResult())
                    self._send(partial.get("partial", ""), "partial")
            final = json.loads(recognizer.FinalResult())
            self._send(final.get("text", ""), "final")


def _resolve_devices(requested: Sequence[str]) -> list[int]:
    import sounddevice as sd

    devices = sd.query_devices()
    if not requested:
        default = sd.default.device
        index = default[0] if isinstance(default, (list, tuple)) else default
        if index is None or index < 0:
            raise SystemExit("No default input device; pass --device explicitly (see --list-devices)")
        return [index]
    resolved: list[int] = []
    for token in requested:
        if token.isdigit():
            resolved.append(int(token))
            continue
        matches = [
            i
            for i, d in enumerate(devices)
            if d.get("max_input_channels", 0) > 0 and token.lower() in d["name"].lower()
        ]
        if not matches:
            raise SystemExit(f"No input device matches {token!r}; see --list-devices")
        resolved.extend(matches)
    return resolved


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list-devices", action="store_true", help="List audio input devices and exit")
    parser.add_argument("--device", action="append", default=[], help="Device index or name substring; repeatable")
    parser.add_argument(
        "--to",
        action="append",
        default=[],
        dest="recipients",
        help=f"Mailbox recipient to post transcripts to; repeatable (default: {', '.join(DEFAULT_RECIPIENTS)})",
    )
    parser.add_argument("--sender", default=DEFAULT_SENDER, help="Mailbox 'from' identity")
    parser.add_argument(
        "--model",
        default=os.environ.get("STT_VOSK_MODEL_DIR", str(DEFAULT_MODEL_CACHE)),
        help="Vosk model directory",
    )
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--min-chars", type=int, default=2, help="Drop finalized transcripts shorter than this")
    parser.add_argument("--partial", action="store_true", help="Also post interim (partial) results")
    parser.add_argument(
        "--seconds",
        type=float,
        default=0.0,
        help="Stop automatically after N seconds (0 = run until Ctrl+C)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.list_devices:
        list_devices()
        return 0

    import vosk as _vosk
    from vosk import Model

    _vosk.SetLogLevel(-1)

    model_dir = _ensure_model(Path(args.model))
    model = Model(str(model_dir))
    client = _mailbox_client()
    recipients = args.recipients or DEFAULT_RECIPIENTS
    device_indexes = _resolve_devices(args.device)

    stop_event = threading.Event()
    listeners = [
        DeviceListener(
            device=index,
            model=model,
            recipients=recipients,
            sender=args.sender,
            sample_rate=args.sample_rate,
            min_chars=args.min_chars,
            include_partial=args.partial,
            stop_event=stop_event,
            client=client,
        )
        for index in device_indexes
    ]
    for listener in listeners:
        listener.start()

    try:
        if args.seconds > 0:
            time.sleep(args.seconds)
        else:
            while any(listener.is_alive() for listener in listeners):
                time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        for listener in listeners:
            listener.join(timeout=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

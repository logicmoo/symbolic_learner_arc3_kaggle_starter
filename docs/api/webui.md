> [← Project README](../../README.md)

# Table of Contents

* [webui](#webui)
* [webui.server](#webui.server)
  * [TerminalProcess](#webui.server.TerminalProcess)
  * [subprocess\_list2cmdline](#webui.server.subprocess_list2cmdline)

<a id="webui"></a>

# webui

Browser ANSI terminal front end for the ARC3 debugger.

<a id="webui.server"></a>

# webui.server

<a id="webui.server.TerminalProcess"></a>

## TerminalProcess Objects

```python
class TerminalProcess()
```

Cross-platform pseudo-terminal wrapper.

Windows uses ConPTY through pywinpty. Unix uses ptyprocess. Both expose the
same blocking read/write API, which the WebSocket handler calls via
asyncio.to_thread().

<a id="webui.server.subprocess_list2cmdline"></a>

#### subprocess\_list2cmdline

```python
def subprocess_list2cmdline(argv: list[str]) -> str
```

Use Python's Windows quoting without importing subprocess globally.

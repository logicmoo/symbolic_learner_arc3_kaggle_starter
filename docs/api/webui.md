> [← Project README](../../README.md)

# Table of Contents

* [webui.server](#webui.server)
  * [PROJECT\_ROOT](#webui.server.PROJECT_ROOT)
  * [STATIC\_ROOT](#webui.server.STATIC_ROOT)
  * [RUNNER](#webui.server.RUNNER)
  * [TerminalProcess](#webui.server.TerminalProcess)
    * [\_\_init\_\_](#webui.server.TerminalProcess.__init__)
    * [start](#webui.server.TerminalProcess.start)
    * [read](#webui.server.TerminalProcess.read)
    * [write](#webui.server.TerminalProcess.write)
    * [resize](#webui.server.TerminalProcess.resize)
    * [is\_alive](#webui.server.TerminalProcess.is_alive)
    * [close](#webui.server.TerminalProcess.close)
  * [subprocess\_list2cmdline](#webui.server.subprocess_list2cmdline)
  * [create\_app](#webui.server.create_app)
  * [parse\_args](#webui.server.parse_args)
  * [main](#webui.server.main)

<a id="webui.server"></a>

# webui.server

<a id="webui.server.PROJECT_ROOT"></a>

#### PROJECT\_ROOT

<a id="webui.server.STATIC_ROOT"></a>

#### STATIC\_ROOT

<a id="webui.server.RUNNER"></a>

#### RUNNER

<a id="webui.server.TerminalProcess"></a>

## TerminalProcess Objects

```python
class TerminalProcess()
```

Cross-platform pseudo-terminal wrapper.

Windows uses ConPTY through pywinpty. Unix uses ptyprocess. Both expose the
same blocking read/write API, which the WebSocket handler calls via
asyncio.to_thread().

<a id="webui.server.TerminalProcess.__init__"></a>

#### \_\_init\_\_

```python
def __init__(argv: list[str], *, cwd: Path, env: dict[str, str], rows: int,
             cols: int) -> None
```

<a id="webui.server.TerminalProcess.start"></a>

#### start

```python
def start() -> None
```

<a id="webui.server.TerminalProcess.read"></a>

#### read

```python
def read(size: int = 65536) -> str
```

<a id="webui.server.TerminalProcess.write"></a>

#### write

```python
def write(data: str) -> None
```

<a id="webui.server.TerminalProcess.resize"></a>

#### resize

```python
def resize(rows: int, cols: int) -> None
```

<a id="webui.server.TerminalProcess.is_alive"></a>

#### is\_alive

```python
def is_alive() -> bool
```

<a id="webui.server.TerminalProcess.close"></a>

#### close

```python
def close() -> None
```

<a id="webui.server.subprocess_list2cmdline"></a>

#### subprocess\_list2cmdline

```python
def subprocess_list2cmdline(argv: list[str]) -> str
```

Use Python's Windows quoting without importing subprocess globally.

<a id="webui.server.create_app"></a>

#### create\_app

```python
def create_app(*,
               default_game: str = "ls20",
               render_mode: str = "terminal",
               access_token: str | None = None) -> FastAPI
```

<a id="webui.server.parse_args"></a>

#### parse\_args

```python
def parse_args() -> argparse.Namespace
```

<a id="webui.server.main"></a>

#### main

```python
def main() -> None
```

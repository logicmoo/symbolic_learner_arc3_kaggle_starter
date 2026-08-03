[← Back to top-level README](README.md)

# Native Windows Setup and Troubleshooting

This guide consolidates the Windows-specific setup and runtime caveats from the maintained top-level documentation, the native batch launcher, the Python package metadata, the Unix-oriented Makefile, the browser terminal, and the debugger's Windows/UNC path handling.

The recommended native-Windows configuration is:

- Windows 10 or Windows 11, 64-bit;
- a local NTFS checkout with a short path, such as `C:\symbolic_learner_arc3_kaggle_starter` or `C:\src\arc3`;
- Python 3.12 or newer from python.org;
- the Python launcher, `py`, available on `PATH`;
- Git for Windows;
- SWI-Prolog on `PATH` when using Prolog-backed features;
- Windows Terminal or a normal `cmd.exe` window for the interactive debugger.

## Fast path for a fresh Windows machine

### 1. Enable long paths as Administrator

Open **Command Prompt as Administrator** and run:

```bat
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
git config --system core.longpaths true
```

The registry command should report:

```text
The operation completed successfully.
```

Close and reopen terminals, IDEs, and Git clients after changing the setting. A reboot is the safest choice if an older process continues to enforce legacy path limits.

If `git config --system` is denied, either rerun it from an elevated terminal or set the option for the current user:

```bat
git config --global core.longpaths true
```

The action tree can become very deep, so configure long-path support **before cloning** whenever possible.

### 2. Keep repository text files as LF

This repository is Linux-oriented even when developed on Windows. Source, Markdown, JSON, YAML, TOML, Prolog, notebooks, and configuration files use LF. Only native Windows command scripts use CRLF.

The repository `.gitattributes` enforces:

```text
* text=auto eol=lf
*.bat text eol=crlf
*.cmd text eol=crlf
```

Recommended Git settings:

```bat
git config --global core.autocrlf false
git config --global core.eol lf
```

Do not configure an editor to convert the entire checkout to CRLF. Avoid running `git add --renormalize .` unless you intentionally want to review and commit a repository-wide line-ending normalization.

### 3. Install and verify Python 3.12 or newer

Install 64-bit Python from python.org and select the installer option that adds Python to `PATH`. The Windows Python launcher is preferred because it avoids ambiguity between Python installations:

```bat
py -0p
py -3.12 --version
```

A successful result resembles:

```text
Python 3.12.x
```

The repository requires Python 3.12 or newer. The setup script will reject an older interpreter.

### 4. Clone into a short local path

Recommended:

```bat
cd /d C:\
git clone https://github.com/logicmoo/symbolic_learner_arc3_kaggle_starter.git
cd /d C:\symbolic_learner_arc3_kaggle_starter
```

Avoid these checkout locations when practical:

- UNC paths such as `\\server\share\project`;
- mapped network drives such as `U:`;
- OneDrive-synchronized folders;
- a deeply nested user-profile path;
- directories controlled by aggressive backup or antivirus synchronization.

The debugger includes fallback handling for unusable action-tree entries, including sibling paths such as `level_1.dir`, but a short local path remains substantially more reliable.

### 5. Run the native setup script

From the repository root in Command Prompt:

```bat
scripts\setup_windows.bat
```

From PowerShell:

```powershell
.\scripts\setup_windows.bat
```

The script:

1. locates Python 3.12 or newer, preferring `py -3.12`;
2. creates the standard `.venv` virtual environment;
3. updates `pip`, `setuptools`, and `wheel`;
4. installs the repository with all optional dependencies;
5. installs the Windows browser-terminal dependency, `pywinpty`;
6. clones `ARC-AGI-3-Agents` into `vendor\ARC-AGI-3-Agents` when Git is available;
7. slims optional framework imports;
8. verifies the core Python imports.

The repository-standard environment name is **`.venv`**, not `venv`.

### 6. Start the terminal debugger

```bat
scripts\interactive_runner.bat ls20
```

The launcher calls this interpreter directly:

```text
.venv\Scripts\python.exe
```

It does not activate the environment and does not call the ambiguous system `python.exe` command.

### 7. Start the browser debugger

```bat
.venv\Scripts\python.exe scripts\run_webui.py --game ls20
```

Then open:

```text
http://127.0.0.1:8765/
```

The browser terminal uses Windows ConPTY through `pywinpty`, which is included by the `debugger` and `all` dependency groups.

## Fix: `The system cannot find the path specified`

The old Windows launcher expected:

```text
venv\Scripts\activate.bat
```

The repository standard is:

```text
.venv\Scripts\python.exe
```

Run:

```bat
scripts\setup_windows.bat
```

Then retry:

```bat
scripts\interactive_runner.bat ls20
```

To verify the environment directly:

```bat
dir .venv\Scripts\python.exe
.venv\Scripts\python.exe --version
```

Do not solve this by creating a second `venv` directory. Keep one environment named `.venv`.

## Fix: `Python was not found; run without arguments to install from the Microsoft Store`

That message usually means Windows invoked an App Execution Alias instead of a real Python installation.

First try the Python launcher:

```bat
py -0p
py -3.12 --version
```

If `py -3.12` works, use it to create the environment:

```bat
py -3.12 -m venv .venv
```

If Python is not installed, install 64-bit Python 3.12 or newer from python.org.

If Python is installed but `python` still opens the Store:

1. Open **Settings**.
2. Open **Apps**.
3. Open **Advanced app settings**.
4. Open **App execution aliases**.
5. Disable the Store aliases for `python.exe` and `python3.exe`.
6. Open a new terminal.

Inspect command resolution with:

```bat
where py
where python
py -0p
```

The fixed batch launcher uses `.venv\Scripts\python.exe` directly after setup, so the Store alias no longer affects normal repository use.

## Required and optional Windows software

### Git for Windows

Verify:

```bat
git --version
git config --get core.longpaths
```

Git is required to clone this repository. It is also used by `scripts\setup_windows.bat` to clone the protected ARC-AGI-3 Agents framework.

### SWI-Prolog

SWI-Prolog is required for the Prolog-controlled runner and Prolog tests. After installing it, ensure `swipl.exe` is on `PATH`:

```bat
where swipl
swipl --version
```

A common installation path is:

```text
C:\Program Files\swipl\bin
```

Open a new terminal after changing `PATH`.

Test the repository's Prolog components:

```bat
swipl -q -s prolog\test_turtle_dsl.pl -g run_tests,halt
swipl -q -s prolog\test_object_memory.pl -g run_tests,halt
```

### Microsoft C++ Build Tools

Normally, current 64-bit Python packages install from wheels and do not require a compiler. Install Microsoft C++ Build Tools only if `pip` explicitly reports that a native extension must be compiled and no compatible wheel is available.

Before installing build tools, first confirm that you are using 64-bit Python 3.12 and a current `pip`:

```bat
.venv\Scripts\python.exe -c "import platform; print(platform.architecture())"
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
```

## Native Windows commands

### Install the normal debugger, notebook, and test bundle

The setup script installs everything, but the smaller manual installation is:

```bat
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install -e ".[debugger,notebooks,test]"
```

### Install every optional dependency

```bat
.venv\Scripts\python.exe -m pip install -e ".[all]"
```

### Run Python tests

```bat
.venv\Scripts\python.exe -m pytest -q
```

### Run direct debugger and ARC3 demonstrations

```bat
.venv\Scripts\python.exe scripts\interactive_runner.py ls20
.venv\Scripts\python.exe scripts\run_webui.py --game ls20
.venv\Scripts\python.exe scripts\prolog_controlled_runner.py
.venv\Scripts\python.exe scripts\re_play.py
.venv\Scripts\python.exe scripts\my_play.py
.venv\Scripts\python.exe scripts\me_play.py
.venv\Scripts\python.exe scripts\he_play.py
```

### Run the protected local Kaggle-compatible agent

```bat
.venv\Scripts\python.exe scripts\play_local.py --game ls20 --max-steps 200
```

### Build the protected submission notebook

```bat
.venv\Scripts\python.exe scripts\build_notebook.py
```

### Open JupyterLab

```bat
.venv\Scripts\jupyter.exe lab
```

## The Makefile is Unix-oriented

The repository Makefile assumes a POSIX shell and uses commands and paths such as:

```text
.venv/bin/python
mkdir -p
chmod 600
rm -rf
VAR=value command
cat
awk
grep
```

Therefore, do not expect `make setup`, `make submit`, or `make clean` to work from ordinary `cmd.exe` or PowerShell.

For native Windows, use:

- `scripts\setup_windows.bat` for setup;
- `.venv\Scripts\python.exe scripts\play_local.py ...` for local play;
- `.venv\Scripts\python.exe scripts\build_notebook.py` for notebook generation;
- the Windows Kaggle CLI executable for upload and status.

Git Bash may run portions of the Makefile, but the Makefile's `.venv/bin/...` paths refer to a POSIX virtual environment, not a native Windows `.venv\Scripts\...` environment.

WSL should use its own Linux virtual environment. Do not share one `.venv` between native Windows and WSL.

## Kaggle token setup on Windows

Create the project-local token directory:

```bat
if not exist .kaggle mkdir .kaggle
```

The token file must be:

```text
.kaggle\access_token
```

It should contain one current Kaggle token on one line and must not be committed.

A PowerShell example that avoids an extra newline is:

```powershell
New-Item -ItemType Directory -Force .kaggle | Out-Null
Set-Content -NoNewline -Encoding ascii .kaggle\access_token 'KGAT_your_token_here'
```

Load the token for the current PowerShell session and use the installed CLI:

```powershell
$env:KAGGLE_API_TOKEN = Get-Content .kaggle\access_token -Raw
.\.venv\Scripts\kaggle.exe kernels push -p notebooks
```

Confirm that `notebooks\kernel-metadata.json` contains the intended Kaggle account and kernel ID before uploading.

## Environment variables on Windows

### Command Prompt

```bat
set "ARC3_RUNTIME_HOME=C:\symbolic_learner_arc3_kaggle_starter"
set "ARC3_PROMPTS_ROOT=C:\symbolic_learner_arc3_kaggle_starter\prompts"
set "ARC3_TREE_ROOT=C:\symbolic_learner_arc3_kaggle_starter\action_trees"
set "ARC3_WEB_COLS=320"
set "ARC3_WEB_ROWS=100"
```

### PowerShell

```powershell
$env:ARC3_RUNTIME_HOME = 'C:\symbolic_learner_arc3_kaggle_starter'
$env:ARC3_PROMPTS_ROOT = 'C:\symbolic_learner_arc3_kaggle_starter\prompts'
$env:ARC3_TREE_ROOT = 'C:\symbolic_learner_arc3_kaggle_starter\action_trees'
$env:ARC3_WEB_COLS = '320'
$env:ARC3_WEB_ROWS = '100'
```

An explicitly configured but invalid `ARC3_RUNTIME_HOME` is treated as an error. Remove or correct it rather than expecting the runtime to silently choose another checkout.

## Browser terminal caveats

The browser debugger uses ConPTY on Windows. If it reports that `pywinpty` is missing:

```bat
.venv\Scripts\python.exe -m pip install --upgrade pywinpty
```

For a larger terminal:

```bat
set "ARC3_WEB_COLS=320"
set "ARC3_WEB_ROWS=100"
.venv\Scripts\python.exe scripts\run_webui.py --game ls20
```

Binding outside localhost requires a token:

```bat
set "ARC3_WEB_TOKEN=choose-a-long-random-token"
.venv\Scripts\python.exe scripts\run_webui.py --host 0.0.0.0 --port 8765 --game ls20
```

Do not expose the browser terminal to a LAN or the internet without authentication and HTTPS. Windows Firewall may display a network-access prompt the first time the server binds a port.

## PyCharm and JetBrains caveats

Use this project interpreter:

```text
<repository>\.venv\Scripts\python.exe
```

Set the run configuration's working directory to the repository root.

For the interactive debugger, prefer an external Windows Terminal or Command Prompt. IDE consoles may consume arrow keys, Shift+Arrow, Ctrl+Arrow, or other key combinations before the Python process receives them.

Avoid opening the project through a UNC path or a mapped network drive. JetBrains indexing, terminal emulation, debugger attachment, Git, virtual environments, and deeply nested action trees are more reliable from a local drive.

When attaching the PyCharm debugger to a process started in a command window, make sure the IDE's Python Debug Server is listening before the process calls `pydevd_pycharm.settrace(...)`. A Windows `ConnectionRefusedError [WinError 10061]` means nothing was listening on the selected host and port.

## UNC paths, mapped drives, and deep action trees

The debugger can generate paths such as:

```text
action_trees\<game>\level_<n>\UP\UP\LEFT\SELECT_x_12_y_31\...
```

Even with Windows long paths enabled, individual programs may still impose legacy limits or mishandle UNC paths.

Recommended practices:

- clone to a short local path;
- enable both the Windows registry setting and Git's `core.longpaths` setting;
- avoid spaces only when a third-party tool demonstrates a quoting bug;
- keep `ARC3_TREE_ROOT` on a local NTFS volume;
- close Jupyter, Python, Prolog, and IDE processes before deleting generated trees;
- do not place `action_trees` in OneDrive or another live synchronization folder.

If a requested level path is blocked by an unusable filesystem entry, the debugger preserves the conflicting entry and may use a sibling path such as `level_1.dir`. Histories, exports, and child branches then use the actual selected path.

## Antivirus, indexing, and file locking

The debugger may create many small files and deeply nested directories. Real-time antivirus scanning, Windows Search indexing, cloud synchronization, and IDE indexing can noticeably slow action-tree generation.

Only for a trusted checkout, consider excluding the generated `action_trees` and `.venv` directories from redundant indexing or scanning. Do not disable security software globally.

Windows prevents deletion or replacement of files held open by another process. If cleanup fails, close:

- the debugger;
- the browser UI server;
- Jupyter kernels;
- Python consoles;
- SWI-Prolog sessions;
- IDE terminals and test runners.

Then retry the operation.

## WSL versus native Windows

Both approaches are valid, but keep them separate:

- **Native Windows:** `.venv\Scripts\python.exe`, batch launchers, ConPTY/`pywinpty`.
- **WSL/Linux:** `.venv/bin/python`, POSIX shell commands, `ptyprocess`, and the Makefile.

Do not reuse a native-Windows virtual environment from WSL or a WSL virtual environment from Windows. Native extension binaries and launcher paths are platform-specific.

For best WSL filesystem performance, keep a WSL checkout inside the Linux filesystem rather than under `/mnt/c`, especially when generating large action trees.

## Diagnostic checklist

Run these from the repository root:

```bat
where git
git --version
git config --get core.longpaths
where py
py -0p
py -3.12 --version
dir .venv\Scripts\python.exe
.venv\Scripts\python.exe --version
.venv\Scripts\python.exe -m pip --version
where swipl
swipl --version
.venv\Scripts\python.exe -c "import arc_agi, PIL, numpy; print('imports OK')"
.venv\Scripts\python.exe -m pytest -q
```

`where swipl` and the Prolog version command may be skipped only when Prolog-backed features are not needed.

## Documentation sources consolidated here

The maintained root documentation identifies the repository's runtime-home behavior, Python requirement, debugger commands, Windows/UNC fallback behavior, browser dimensions and security, protected Kaggle workflow, Unix Makefile assumptions, and repository file layout:

- [README.md](README.md)
- [DEBUGGER.md](DEBUGGER.md)
- [KAGGLE.md](KAGGLE.md)
- [SOW_PHASE_ARCHITECTURE.md](SOW_PHASE_ARCHITECTURE.md)
- [TODO.md](TODO.md)
- [FILE_TREE.md](FILE_TREE.md)

Generated `README.md` files under `action_trees` describe runtime states and are not installation guides.

[← Back to top-level README](README.md)

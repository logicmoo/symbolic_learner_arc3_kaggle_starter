> [← Project README](../../README.md)

# Table of Contents

* [llm\_workflow\_editor](#llm_workflow_editor)
  * [EXAMPLE\_PATH](#llm_workflow_editor.EXAMPLE_PATH)
  * [load\_example\_workflow](#llm_workflow_editor.load_example_workflow)
  * [ensure\_example\_workflow](#llm_workflow_editor.ensure_example_workflow)
  * [open\_workflow\_editor](#llm_workflow_editor.open_workflow_editor)
  * [install\_workflow\_editor\_ui](#llm_workflow_editor.install_workflow_editor_ui)

<a id="llm_workflow_editor"></a>

# llm\_workflow\_editor

<a id="llm_workflow_editor.EXAMPLE_PATH"></a>

#### EXAMPLE\_PATH

<a id="llm_workflow_editor.load_example_workflow"></a>

#### load\_example\_workflow

```python
def load_example_workflow(path: Path = EXAMPLE_PATH) -> dict[str, Any]
```

<a id="llm_workflow_editor.ensure_example_workflow"></a>

#### ensure\_example\_workflow

```python
def ensure_example_workflow(raw: dict[str, Any]) -> bool
```

<a id="llm_workflow_editor.open_workflow_editor"></a>

#### open\_workflow\_editor

```python
def open_workflow_editor(runner: Any) -> None
```

<a id="llm_workflow_editor.install_workflow_editor_ui"></a>

#### install\_workflow\_editor\_ui

```python
def install_workflow_editor_ui(ui_module: Any) -> None
```

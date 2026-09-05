> [← Project README](../../README.md)

# Table of Contents

* [llm\_profile\_editor](#llm_profile_editor)
  * [EditorResult](#llm_profile_editor.EditorResult)
    * [run\_batch](#llm_profile_editor.EditorResult.run_batch)
    * [saved](#llm_profile_editor.EditorResult.saved)
  * [open\_profile\_editor](#llm_profile_editor.open_profile_editor)
  * [install\_profile\_editor\_ui](#llm_profile_editor.install_profile_editor_ui)

<a id="llm_profile_editor"></a>

# llm\_profile\_editor

<a id="llm_profile_editor.EditorResult"></a>

## EditorResult Objects

```python
@dataclass
class EditorResult()
```

<a id="llm_profile_editor.EditorResult.run_batch"></a>

#### run\_batch: `bool`

<a id="llm_profile_editor.EditorResult.saved"></a>

#### saved: `bool`

<a id="llm_profile_editor.open_profile_editor"></a>

#### open\_profile\_editor

```python
def open_profile_editor(runner: Any) -> None
```

<a id="llm_profile_editor.install_profile_editor_ui"></a>

#### install\_profile\_editor\_ui

```python
def install_profile_editor_ui(ui_module: Any) -> None
```

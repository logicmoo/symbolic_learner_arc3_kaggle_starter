> [← Project README](../../README.md)

# Table of Contents

* [llm\_key\_controls](#llm_key_controls)
  * [run\_checked\_batch](#llm_key_controls.run_checked_batch)
  * [repeat\_last\_workflow](#llm_key_controls.repeat_last_workflow)
  * [refresh\_openrouter\_models](#llm_key_controls.refresh_openrouter_models)
  * [save\_history](#llm_key_controls.save_history)
  * [install\_llm\_key\_controls](#llm_key_controls.install_llm_key_controls)

<a id="llm_key_controls"></a>

# llm\_key\_controls

<a id="llm_key_controls.run_checked_batch"></a>

#### run\_checked\_batch

```python
def run_checked_batch(runner: Any) -> None
```

Run every profile currently marked batch_enabled in the catalog.

<a id="llm_key_controls.repeat_last_workflow"></a>

#### repeat\_last\_workflow

```python
def repeat_last_workflow(runner: Any) -> None
```

Repeat the workflow most recently selected through uppercase W.

<a id="llm_key_controls.refresh_openrouter_models"></a>

#### refresh\_openrouter\_models

```python
def refresh_openrouter_models(runner: Any) -> None
```

Refresh OpenRouter's live model list and show usable free catalog rows.

<a id="llm_key_controls.save_history"></a>

#### save\_history

```python
def save_history(runner: Any) -> Path
```

Save history under uppercase H, replacing the debugger's old lowercase w.

<a id="llm_key_controls.install_llm_key_controls"></a>

#### install\_llm\_key\_controls

```python
def install_llm_key_controls(ui_module: Any) -> None
```

Install the agreed top-level LLM keys and their unified help text.

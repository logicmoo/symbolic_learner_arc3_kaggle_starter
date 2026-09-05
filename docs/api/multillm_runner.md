> [← Project README](../../README.md)

# Table of Contents

* [multillm\_runner](#multillm_runner)
  * [MultiLlmArc3Runner](#multillm_runner.MultiLlmArc3Runner)
    * [\_\_init\_\_](#multillm_runner.MultiLlmArc3Runner.__init__)
    * [llm\_router](#multillm_runner.MultiLlmArc3Runner.llm_router)
    * [llm\_provider\_statuses](#multillm_runner.MultiLlmArc3Runner.llm_provider_statuses)
    * [cycle\_llm\_provider](#multillm_runner.MultiLlmArc3Runner.cycle_llm_provider)
    * [current\_llm\_summary](#multillm_runner.MultiLlmArc3Runner.current_llm_summary)
    * [gpt\_command\_1](#multillm_runner.MultiLlmArc3Runner.gpt_command_1)
    * [gpt\_command\_5](#multillm_runner.MultiLlmArc3Runner.gpt_command_5)
    * [gpt\_command\_6](#multillm_runner.MultiLlmArc3Runner.gpt_command_6)
  * [last\_runner](#multillm_runner.last_runner)
  * [install\_interactive\_runner](#multillm_runner.install_interactive_runner)

<a id="multillm_runner"></a>

# multillm\_runner

<a id="multillm_runner.MultiLlmArc3Runner"></a>

## MultiLlmArc3Runner Objects

```python
class MultiLlmArc3Runner(Arc3Runner)
```

Arc3Runner whose existing GPT artifact path uses a provider router.

The mutable `.pl` files remain the latest view. Every provider call also
creates a restorable Markdown transcript containing an immutable artifact
snapshot and the complete request/response debugging record.

Pressing ``g`` advances to the next provider that is both configured and
reachable. A provider that fails an ARC3 analysis is skipped for the rest
of the current debugger session, making repeated ``g 4`` runs useful for
collecting independent provider outputs without repeatedly hitting a bad
key, offline endpoint, unavailable model, or exhausted free-tier service.

<a id="multillm_runner.MultiLlmArc3Runner.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*args: Any, **kwargs: Any) -> None
```

<a id="multillm_runner.MultiLlmArc3Runner.llm_router"></a>

#### llm\_router

```python
def llm_router() -> StudioAwareLlmProviderRouter
```

<a id="multillm_runner.MultiLlmArc3Runner.llm_provider_statuses"></a>

#### llm\_provider\_statuses

```python
def llm_provider_statuses(*,
                          refresh: bool = False) -> tuple[dict[str, Any], ...]
```

<a id="multillm_runner.MultiLlmArc3Runner.cycle_llm_provider"></a>

#### cycle\_llm\_provider

```python
def cycle_llm_provider() -> ProviderSpec
```

<a id="multillm_runner.MultiLlmArc3Runner.current_llm_summary"></a>

#### current\_llm\_summary

```python
def current_llm_summary() -> str
```

<a id="multillm_runner.MultiLlmArc3Runner.gpt_command_1"></a>

#### gpt\_command\_1

```python
def gpt_command_1() -> None
```

Restore a historical transcript or open the unified LLM config.

<a id="multillm_runner.MultiLlmArc3Runner.gpt_command_5"></a>

#### gpt\_command\_5

```python
def gpt_command_5() -> None
```

<a id="multillm_runner.MultiLlmArc3Runner.gpt_command_6"></a>

#### gpt\_command\_6

```python
def gpt_command_6() -> None
```

<a id="multillm_runner.last_runner"></a>

#### last\_runner

```python
def last_runner() -> MultiLlmArc3Runner | None
```

<a id="multillm_runner.install_interactive_runner"></a>

#### install\_interactive\_runner

```python
def install_interactive_runner(ui_module: Any) -> None
```

Install multi-LLM behavior without duplicating the debugger UI loop.

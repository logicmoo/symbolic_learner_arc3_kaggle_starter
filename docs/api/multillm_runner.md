> [← Project README](../../README.md)

# Table of Contents

* [multillm\_runner](#multillm_runner)
  * [MultiLlmArc3Runner](#multillm_runner.MultiLlmArc3Runner)
    * [gpt\_command\_1](#multillm_runner.MultiLlmArc3Runner.gpt_command_1)
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

<a id="multillm_runner.MultiLlmArc3Runner.gpt_command_1"></a>

#### gpt\_command\_1

```python
def gpt_command_1() -> None
```

Restore a historical transcript or open the unified LLM config.

<a id="multillm_runner.install_interactive_runner"></a>

#### install\_interactive\_runner

```python
def install_interactive_runner(ui_module: Any) -> None
```

Install multi-LLM behavior without duplicating the debugger UI loop.

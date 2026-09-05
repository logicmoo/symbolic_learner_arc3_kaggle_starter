> [← Project README](../../README.md)

# Table of Contents

* [arc3\_runner](#arc3_runner)
  * [Arc3Runner](#arc3_runner.Arc3Runner)
    * [current\_grid](#arc3_runner.Arc3Runner.current_grid)
    * [semantic\_authorization\_options](#arc3_runner.Arc3Runner.semantic_authorization_options)
    * [gpt\_command\_2](#arc3_runner.Arc3Runner.gpt_command_2)
    * [gpt\_command\_3](#arc3_runner.Arc3Runner.gpt_command_3)
    * [gpt\_command\_4](#arc3_runner.Arc3Runner.gpt_command_4)

<a id="arc3_runner"></a>

# arc3\_runner

<a id="arc3_runner.Arc3Runner"></a>

## Arc3Runner Objects

```python
class Arc3Runner()
```

Debuggable ARC3 environment with a persistent deterministic action tree.

<a id="arc3_runner.Arc3Runner.current_grid"></a>

#### current\_grid

```python
def current_grid() -> Any
```

Return the newest logical grid used by capture observers.

<a id="arc3_runner.Arc3Runner.semantic_authorization_options"></a>

#### semantic\_authorization\_options

```python
def semantic_authorization_options() -> dict[str, tuple[str, ...]]
```

Collect explicit friendly-identity choices from semantic observers.

<a id="arc3_runner.Arc3Runner.gpt_command_2"></a>

#### gpt\_command\_2

```python
def gpt_command_2() -> None
```

Fast demo analysis: low image detail, low reasoning, moderate tokens.

<a id="arc3_runner.Arc3Runner.gpt_command_3"></a>

#### gpt\_command\_3

```python
def gpt_command_3() -> None
```

Deep analysis: high current image detail and larger token budget.

<a id="arc3_runner.Arc3Runner.gpt_command_4"></a>

#### gpt\_command\_4

```python
def gpt_command_4() -> None
```

Extreme analysis: high detail for both images and maximum budget.

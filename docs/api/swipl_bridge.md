> [← Project README](../../README.md)

# Table of Contents

* [swipl\_bridge](#swipl_bridge)
  * [SWIPrologBridge](#swipl_bridge.SWIPrologBridge)
    * [\_\_init\_\_](#swipl_bridge.SWIPrologBridge.__init__)
    * [choose\_action](#swipl_bridge.SWIPrologBridge.choose_action)
    * [execute\_turtle](#swipl_bridge.SWIPrologBridge.execute_turtle)

<a id="swipl_bridge"></a>

# swipl\_bridge

<a id="swipl_bridge.SWIPrologBridge"></a>

## SWIPrologBridge Objects

```python
class SWIPrologBridge()
```

Invoke a Prolog controller using a JSON snapshot from Arc3Runner.

<a id="swipl_bridge.SWIPrologBridge.__init__"></a>

#### \_\_init\_\_

```python
def __init__(agent_file: str | Path, swipl_executable: str = "swipl") -> None
```

<a id="swipl_bridge.SWIPrologBridge.choose_action"></a>

#### choose\_action

```python
def choose_action(snapshot: Mapping[str, Any]) -> dict[str, Any]
```

<a id="swipl_bridge.SWIPrologBridge.execute_turtle"></a>

#### execute\_turtle

```python
def execute_turtle(program: str,
                   params: Mapping[str, Any] | None = None) -> dict[str, Any]
```

Execute a turtle/2 program through the canonical Turtle DSL.

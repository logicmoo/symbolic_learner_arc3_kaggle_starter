> [← Project README](../../README.md)

# Table of Contents

* [swipl\_bridge](#swipl_bridge)
  * [SWIPrologBridge](#swipl_bridge.SWIPrologBridge)
    * [execute\_turtle](#swipl_bridge.SWIPrologBridge.execute_turtle)

<a id="swipl_bridge"></a>

# swipl\_bridge

<a id="swipl_bridge.SWIPrologBridge"></a>

## SWIPrologBridge Objects

```python
class SWIPrologBridge()
```

Invoke a Prolog controller using a JSON snapshot from Arc3Runner.

<a id="swipl_bridge.SWIPrologBridge.execute_turtle"></a>

#### execute\_turtle

```python
def execute_turtle(program: str,
                   params: Mapping[str, Any] | None = None) -> dict[str, Any]
```

Execute a turtle/2 program through the canonical Turtle DSL.

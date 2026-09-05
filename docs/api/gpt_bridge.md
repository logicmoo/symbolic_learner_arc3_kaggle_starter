> [← Project README](../../README.md)

# Table of Contents

* [gpt\_bridge](#gpt_bridge)
  * [ARTIFACT\_KEYS](#gpt_bridge.ARTIFACT_KEYS)
  * [PAIR\_ONLY](#gpt_bridge.PAIR_ONLY)
  * [GptArcAnalyzer](#gpt_bridge.GptArcAnalyzer)
    * [\_\_init\_\_](#gpt_bridge.GptArcAnalyzer.__init__)
    * [configure\_profile](#gpt_bridge.GptArcAnalyzer.configure_profile)
    * [prompts](#gpt_bridge.GptArcAnalyzer.prompts)
    * [edit\_prompts](#gpt_bridge.GptArcAnalyzer.edit_prompts)
    * [ensure\_full\_analysis](#gpt_bridge.GptArcAnalyzer.ensure_full_analysis)
    * [ensure\_differences](#gpt_bridge.GptArcAnalyzer.ensure_differences)
    * [generate\_single\_artifact](#gpt_bridge.GptArcAnalyzer.generate_single_artifact)
    * [generate\_pair\_artifact](#gpt_bridge.GptArcAnalyzer.generate_pair_artifact)

<a id="gpt_bridge"></a>

# gpt\_bridge

<a id="gpt_bridge.ARTIFACT_KEYS"></a>

#### ARTIFACT\_KEYS

<a id="gpt_bridge.PAIR_ONLY"></a>

#### PAIR\_ONLY

<a id="gpt_bridge.GptArcAnalyzer"></a>

## GptArcAnalyzer Objects

```python
class GptArcAnalyzer()
```

One-call GPT analysis that splits a structured bundle into Prolog files.

<a id="gpt_bridge.GptArcAnalyzer.__init__"></a>

#### \_\_init\_\_

```python
def __init__(prompts_path: str | Path,
             *,
             model: str | None = None,
             client: Any | None = None) -> None
```

<a id="gpt_bridge.GptArcAnalyzer.configure_profile"></a>

#### configure\_profile

```python
def configure_profile(level: int) -> dict[str, Any]
```

<a id="gpt_bridge.GptArcAnalyzer.prompts"></a>

#### prompts

```python
def prompts() -> dict[str, str]
```

Return a compatibility combined prompt from the unified config.

<a id="gpt_bridge.GptArcAnalyzer.edit_prompts"></a>

#### edit\_prompts

```python
def edit_prompts() -> None
```

<a id="gpt_bridge.GptArcAnalyzer.ensure_full_analysis"></a>

#### ensure\_full\_analysis

```python
def ensure_full_analysis(store: ActionTreeStore,
                         node: StateNode,
                         *,
                         force: bool = False,
                         analysis_level: int = 2) -> dict[str, Any]
```

<a id="gpt_bridge.GptArcAnalyzer.ensure_differences"></a>

#### ensure\_differences

```python
def ensure_differences(store: ActionTreeStore,
                       node: StateNode,
                       *,
                       force: bool = True)
```

<a id="gpt_bridge.GptArcAnalyzer.generate_single_artifact"></a>

#### generate\_single\_artifact

```python
def generate_single_artifact(store: ActionTreeStore,
                             node: StateNode,
                             prompt_name: str,
                             filename: str,
                             *,
                             force: bool = True)
```

<a id="gpt_bridge.GptArcAnalyzer.generate_pair_artifact"></a>

#### generate\_pair\_artifact

```python
def generate_pair_artifact(store: ActionTreeStore,
                           node: StateNode,
                           prompt_name: str,
                           filename: str,
                           *,
                           force: bool = True)
```

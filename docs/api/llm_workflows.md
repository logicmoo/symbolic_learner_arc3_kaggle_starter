> [← Project README](../../README.md)

# Table of Contents

* [llm\_workflows](#llm_workflows)
  * [DEFAULT\_WORKFLOW\_PATH](#llm_workflows.DEFAULT_WORKFLOW_PATH)
  * [TransactionDefinition](#llm_workflows.TransactionDefinition)
    * [transaction\_id](#llm_workflows.TransactionDefinition.transaction_id)
    * [label](#llm_workflows.TransactionDefinition.label)
    * [kind](#llm_workflows.TransactionDefinition.kind)
    * [requires\_vision](#llm_workflows.TransactionDefinition.requires_vision)
    * [include\_parent\_image](#llm_workflows.TransactionDefinition.include_parent_image)
    * [include\_current\_image](#llm_workflows.TransactionDefinition.include_current_image)
    * [output\_keys](#llm_workflows.TransactionDefinition.output_keys)
    * [input\_files](#llm_workflows.TransactionDefinition.input_files)
    * [instructions](#llm_workflows.TransactionDefinition.instructions)
    * [output\_file](#llm_workflows.TransactionDefinition.output_file)
    * [runner\_method](#llm_workflows.TransactionDefinition.runner_method)
    * [combine\_safe](#llm_workflows.TransactionDefinition.combine_safe)
    * [from\_mapping](#llm_workflows.TransactionDefinition.from_mapping)
  * [WorkflowStep](#llm_workflows.WorkflowStep)
    * [step\_id](#llm_workflows.WorkflowStep.step_id)
    * [transaction\_id](#llm_workflows.WorkflowStep.transaction_id)
    * [profile\_id](#llm_workflows.WorkflowStep.profile_id)
    * [model\_id](#llm_workflows.WorkflowStep.model_id)
    * [analysis\_level](#llm_workflows.WorkflowStep.analysis_level)
    * [combine\_group](#llm_workflows.WorkflowStep.combine_group)
    * [continue\_on\_error](#llm_workflows.WorkflowStep.continue_on_error)
    * [from\_mapping](#llm_workflows.WorkflowStep.from_mapping)
  * [WorkflowDefinition](#llm_workflows.WorkflowDefinition)
    * [workflow\_id](#llm_workflows.WorkflowDefinition.workflow_id)
    * [label](#llm_workflows.WorkflowDefinition.label)
    * [description](#llm_workflows.WorkflowDefinition.description)
    * [steps](#llm_workflows.WorkflowDefinition.steps)
    * [repeat\_from](#llm_workflows.WorkflowDefinition.repeat_from)
    * [repeat\_while\_slot](#llm_workflows.WorkflowDefinition.repeat_while_slot)
    * [max\_iterations](#llm_workflows.WorkflowDefinition.max_iterations)
    * [from\_mapping](#llm_workflows.WorkflowDefinition.from_mapping)
  * [WorkflowAwareLlmProviderRouter](#llm_workflows.WorkflowAwareLlmProviderRouter)
    * [\_\_init\_\_](#llm_workflows.WorkflowAwareLlmProviderRouter.__init__)
    * [\_\_del\_\_](#llm_workflows.WorkflowAwareLlmProviderRouter.__del__)
    * [transaction\_for\_profile](#llm_workflows.WorkflowAwareLlmProviderRouter.transaction_for_profile)
    * [model\_availability](#llm_workflows.WorkflowAwareLlmProviderRouter.model_availability)
    * [configured\_model\_ids](#llm_workflows.WorkflowAwareLlmProviderRouter.configured_model_ids)
  * [LlmWorkflowEngine](#llm_workflows.LlmWorkflowEngine)
    * [\_\_init\_\_](#llm_workflows.LlmWorkflowEngine.__init__)
    * [run](#llm_workflows.LlmWorkflowEngine.run)
  * [install\_workflow\_router](#llm_workflows.install_workflow_router)
  * [run\_workflow\_menu](#llm_workflows.run_workflow_menu)
  * [install\_workflow\_ui](#llm_workflows.install_workflow_ui)

<a id="llm_workflows"></a>

# llm\_workflows

<a id="llm_workflows.DEFAULT_WORKFLOW_PATH"></a>

#### DEFAULT\_WORKFLOW\_PATH

<a id="llm_workflows.TransactionDefinition"></a>

## TransactionDefinition Objects

```python
@dataclass(frozen=True)
class TransactionDefinition()
```

<a id="llm_workflows.TransactionDefinition.transaction_id"></a>

#### transaction\_id: `str`

<a id="llm_workflows.TransactionDefinition.label"></a>

#### label: `str`

<a id="llm_workflows.TransactionDefinition.kind"></a>

#### kind: `str`

<a id="llm_workflows.TransactionDefinition.requires_vision"></a>

#### requires\_vision: `bool`

<a id="llm_workflows.TransactionDefinition.include_parent_image"></a>

#### include\_parent\_image: `bool`

<a id="llm_workflows.TransactionDefinition.include_current_image"></a>

#### include\_current\_image: `bool`

<a id="llm_workflows.TransactionDefinition.output_keys"></a>

#### output\_keys: `tuple[str, ...]`

<a id="llm_workflows.TransactionDefinition.input_files"></a>

#### input\_files: `tuple[str, ...]`

<a id="llm_workflows.TransactionDefinition.instructions"></a>

#### instructions: `str`

<a id="llm_workflows.TransactionDefinition.output_file"></a>

#### output\_file: `str | None`

<a id="llm_workflows.TransactionDefinition.runner_method"></a>

#### runner\_method: `str | None`

<a id="llm_workflows.TransactionDefinition.combine_safe"></a>

#### combine\_safe: `bool`

<a id="llm_workflows.TransactionDefinition.from_mapping"></a>

#### from\_mapping

```python
@classmethod
def from_mapping(cls, raw: Mapping[str, Any]) -> "TransactionDefinition"
```

<a id="llm_workflows.WorkflowStep"></a>

## WorkflowStep Objects

```python
@dataclass(frozen=True)
class WorkflowStep()
```

<a id="llm_workflows.WorkflowStep.step_id"></a>

#### step\_id: `str`

<a id="llm_workflows.WorkflowStep.transaction_id"></a>

#### transaction\_id: `str`

<a id="llm_workflows.WorkflowStep.profile_id"></a>

#### profile\_id: `str | None`

<a id="llm_workflows.WorkflowStep.model_id"></a>

#### model\_id: `str | None`

<a id="llm_workflows.WorkflowStep.analysis_level"></a>

#### analysis\_level: `int | None`

<a id="llm_workflows.WorkflowStep.combine_group"></a>

#### combine\_group: `str | None`

<a id="llm_workflows.WorkflowStep.continue_on_error"></a>

#### continue\_on\_error: `bool`

<a id="llm_workflows.WorkflowStep.from_mapping"></a>

#### from\_mapping

```python
@classmethod
def from_mapping(cls, raw: Mapping[str, Any]) -> "WorkflowStep"
```

<a id="llm_workflows.WorkflowDefinition"></a>

## WorkflowDefinition Objects

```python
@dataclass(frozen=True)
class WorkflowDefinition()
```

<a id="llm_workflows.WorkflowDefinition.workflow_id"></a>

#### workflow\_id: `str`

<a id="llm_workflows.WorkflowDefinition.label"></a>

#### label: `str`

<a id="llm_workflows.WorkflowDefinition.description"></a>

#### description: `str`

<a id="llm_workflows.WorkflowDefinition.steps"></a>

#### steps: `tuple[WorkflowStep, ...]`

<a id="llm_workflows.WorkflowDefinition.repeat_from"></a>

#### repeat\_from: `str | None`

<a id="llm_workflows.WorkflowDefinition.repeat_while_slot"></a>

#### repeat\_while\_slot: `str | None`

<a id="llm_workflows.WorkflowDefinition.max_iterations"></a>

#### max\_iterations: `int`

<a id="llm_workflows.WorkflowDefinition.from_mapping"></a>

#### from\_mapping

```python
@classmethod
def from_mapping(cls, raw: Mapping[str, Any]) -> "WorkflowDefinition"
```

<a id="llm_workflows.WorkflowAwareLlmProviderRouter"></a>

## WorkflowAwareLlmProviderRouter Objects

```python
class WorkflowAwareLlmProviderRouter(CatalogAwareLlmProviderRouter)
```

Catalog router extended with optional transactions and workflows.

The normal lowercase-g / level-4 path remains unchanged. The companion
workflow file contributes additional models and profiles plus specialized
transactions that can be orchestrated only when requested.

<a id="llm_workflows.WorkflowAwareLlmProviderRouter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config_path: str | Path,
             *,
             workflow_path: str | Path | None = None,
             urlopen: Callable[..., Any] | None = None,
             **kwargs: Any) -> None
```

<a id="llm_workflows.WorkflowAwareLlmProviderRouter.__del__"></a>

#### \_\_del\_\_

```python
def __del__() -> None
```

<a id="llm_workflows.WorkflowAwareLlmProviderRouter.transaction_for_profile"></a>

#### transaction\_for\_profile

```python
def transaction_for_profile(profile_id: str) -> TransactionDefinition
```

<a id="llm_workflows.WorkflowAwareLlmProviderRouter.model_availability"></a>

#### model\_availability

```python
def model_availability(model_id: str,
                       *,
                       refresh: bool = False) -> tuple[bool, str]
```

<a id="llm_workflows.WorkflowAwareLlmProviderRouter.configured_model_ids"></a>

#### configured\_model\_ids

```python
def configured_model_ids() -> tuple[str, ...]
```

<a id="llm_workflows.LlmWorkflowEngine"></a>

## LlmWorkflowEngine Objects

```python
class LlmWorkflowEngine()
```

<a id="llm_workflows.LlmWorkflowEngine.__init__"></a>

#### \_\_init\_\_

```python
def __init__(runner: Any) -> None
```

<a id="llm_workflows.LlmWorkflowEngine.run"></a>

#### run

```python
def run(workflow_id: str) -> None
```

<a id="llm_workflows.install_workflow_router"></a>

#### install\_workflow\_router

```python
def install_workflow_router() -> None
```

<a id="llm_workflows.run_workflow_menu"></a>

#### run\_workflow\_menu

```python
def run_workflow_menu(runner: Any) -> None
```

<a id="llm_workflows.install_workflow_ui"></a>

#### install\_workflow\_ui

```python
def install_workflow_ui(ui_module: Any) -> None
```

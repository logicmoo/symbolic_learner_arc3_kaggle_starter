> [← Project README](../../README.md)

# Table of Contents

* [workflow\_operations](#workflow_operations)
  * [ROOT](#workflow_operations.ROOT)
  * [DEFAULT\_OPERATION\_PATH](#workflow_operations.DEFAULT_OPERATION_PATH)
  * [DEFAULT\_DATATYPE\_PATH](#workflow_operations.DEFAULT_DATATYPE_PATH)
  * [txt](#workflow_operations.txt)
  * [read\_obj](#workflow_operations.read_obj)
  * [slug](#workflow_operations.slug)
  * [Impl](#workflow_operations.Impl)
    * [id](#workflow_operations.Impl.id)
  * [Operation](#workflow_operations.Operation)
    * [id](#workflow_operations.Operation.id)
    * [impl](#workflow_operations.Operation.impl)
  * [Slot](#workflow_operations.Slot)
    * [datatype](#workflow_operations.Slot.datatype)
    * [json](#workflow_operations.Slot.json)
  * [load\_operations](#workflow_operations.load_operations)
  * [expand\_subworkflows](#workflow_operations.expand_subworkflows)
  * [OperationAwareWorkflowRouter](#workflow_operations.OperationAwareWorkflowRouter)
    * [\_\_init\_\_](#workflow_operations.OperationAwareWorkflowRouter.__init__)
    * [\_\_del\_\_](#workflow_operations.OperationAwareWorkflowRouter.__del__)
  * [node\_root](#workflow_operations.node_root)
  * [paths](#workflow_operations.paths)
  * [manifest](#workflow_operations.manifest)
  * [copy\_images](#workflow_operations.copy_images)
  * [grab\_arc3\_state](#workflow_operations.grab_arc3_state)
  * [disk\_directory](#workflow_operations.disk_directory)
  * [ask\_upload](#workflow_operations.ask_upload)
  * [generated](#workflow_operations.generated)
  * [select\_arc3\_world](#workflow_operations.select_arc3_world)
  * [await\_human\_arc3\_action](#workflow_operations.await_human_arc3_action)
  * [continue\_human\_observation](#workflow_operations.continue_human_observation)
  * [advance\_observation](#workflow_operations.advance_observation)
  * [remote\_url](#workflow_operations.remote_url)
  * [clipboard](#workflow_operations.clipboard)
  * [video\_frames](#workflow_operations.video_frames)
  * [camera](#workflow_operations.camera)
  * [normalize](#workflow_operations.normalize)
  * [sync\_objects](#workflow_operations.sync_objects)
  * [render\_turtle](#workflow_operations.render_turtle)
  * [display](#workflow_operations.display)
  * [validate](#workflow_operations.validate)
  * [report](#workflow_operations.report)
  * [HANDLERS](#workflow_operations.HANDLERS)
  * [seed](#workflow_operations.seed)
  * [save\_slots](#workflow_operations.save_slots)
  * [resolve\_inputs](#workflow_operations.resolve_inputs)
  * [store\_outputs](#workflow_operations.store_outputs)
  * [artifact\_outputs](#workflow_operations.artifact_outputs)
  * [execute\_operation](#workflow_operations.execute_operation)
  * [install\_operation\_workflows](#workflow_operations.install_operation_workflows)

<a id="workflow_operations"></a>

# workflow\_operations

<a id="workflow_operations.ROOT"></a>

#### ROOT

<a id="workflow_operations.DEFAULT_OPERATION_PATH"></a>

#### DEFAULT\_OPERATION\_PATH

<a id="workflow_operations.DEFAULT_DATATYPE_PATH"></a>

#### DEFAULT\_DATATYPE\_PATH

<a id="workflow_operations.txt"></a>

#### txt

```python
def txt(v: Any) -> str
```

<a id="workflow_operations.read_obj"></a>

#### read\_obj

```python
def read_obj(p: Path) -> dict[str, Any]
```

<a id="workflow_operations.slug"></a>

#### slug

```python
def slug(s: str) -> str
```

<a id="workflow_operations.Impl"></a>

## Impl Objects

```python
@dataclass(frozen=True)
class Impl()
```

<a id="workflow_operations.Impl.id"></a>

#### id: `str`

<a id="workflow_operations.Operation"></a>

## Operation Objects

```python
@dataclass(frozen=True)
class Operation()
```

<a id="workflow_operations.Operation.id"></a>

#### id: `str`

<a id="workflow_operations.Operation.impl"></a>

#### impl

```python
def impl(wanted: str | None) -> Impl
```

<a id="workflow_operations.Slot"></a>

## Slot Objects

```python
@dataclass
class Slot()
```

<a id="workflow_operations.Slot.datatype"></a>

#### datatype: `str`

<a id="workflow_operations.Slot.json"></a>

#### json

```python
def json()
```

<a id="workflow_operations.load_operations"></a>

#### load\_operations

```python
def load_operations(
        path: Path = DEFAULT_OPERATION_PATH) -> tuple[Operation, ...]
```

<a id="workflow_operations.expand_subworkflows"></a>

#### expand\_subworkflows

```python
def expand_subworkflows(workflows)
```

Expand reusable workflow calls while preserving typed slot bindings.

<a id="workflow_operations.OperationAwareWorkflowRouter"></a>

## OperationAwareWorkflowRouter Objects

```python
class OperationAwareWorkflowRouter(WorkflowAwareLlmProviderRouter)
```

<a id="workflow_operations.OperationAwareWorkflowRouter.__init__"></a>

#### \_\_init\_\_

```python
def __init__(config_path,
             *,
             workflow_path=None,
             operation_path=None,
             datatype_path=None,
             **kw)
```

<a id="workflow_operations.OperationAwareWorkflowRouter.__del__"></a>

#### \_\_del\_\_

```python
def __del__()
```

<a id="workflow_operations.node_root"></a>

#### node\_root

```python
def node_root(engine)
```

<a id="workflow_operations.paths"></a>

#### paths

```python
def paths(v)
```

<a id="workflow_operations.manifest"></a>

#### manifest

```python
def manifest(ps, source, dest)
```

<a id="workflow_operations.copy_images"></a>

#### copy\_images

```python
def copy_images(ps, dest, prefix)
```

<a id="workflow_operations.grab_arc3_state"></a>

#### grab\_arc3\_state

```python
def grab_arc3_state(e, inp, par)
```

<a id="workflow_operations.disk_directory"></a>

#### disk\_directory

```python
def disk_directory(e, inp, par)
```

<a id="workflow_operations.ask_upload"></a>

#### ask\_upload

```python
def ask_upload(e, inp, par)
```

<a id="workflow_operations.generated"></a>

#### generated

```python
def generated(e, inp, par)
```

<a id="workflow_operations.select_arc3_world"></a>

#### select\_arc3\_world

```python
def select_arc3_world(e, inp, par)
```

<a id="workflow_operations.await_human_arc3_action"></a>

#### await\_human\_arc3\_action

```python
def await_human_arc3_action(e, inp, par)
```

<a id="workflow_operations.continue_human_observation"></a>

#### continue\_human\_observation

```python
def continue_human_observation(e, inp, par)
```

<a id="workflow_operations.advance_observation"></a>

#### advance\_observation

```python
def advance_observation(e, inp, par)
```

<a id="workflow_operations.remote_url"></a>

#### remote\_url

```python
def remote_url(e, inp, par)
```

<a id="workflow_operations.clipboard"></a>

#### clipboard

```python
def clipboard(e, inp, par)
```

<a id="workflow_operations.video_frames"></a>

#### video\_frames

```python
def video_frames(e, inp, par)
```

<a id="workflow_operations.camera"></a>

#### camera

```python
def camera(e, inp, par)
```

<a id="workflow_operations.normalize"></a>

#### normalize

```python
def normalize(e, inp, par)
```

<a id="workflow_operations.sync_objects"></a>

#### sync\_objects

```python
def sync_objects(e, inp, par)
```

<a id="workflow_operations.render_turtle"></a>

#### render\_turtle

```python
def render_turtle(e, inp, par)
```

<a id="workflow_operations.display"></a>

#### display

```python
def display(e, inp, par)
```

<a id="workflow_operations.validate"></a>

#### validate

```python
def validate(e, inp, par)
```

<a id="workflow_operations.report"></a>

#### report

```python
def report(e, inp, par)
```

<a id="workflow_operations.HANDLERS"></a>

#### HANDLERS

<a id="workflow_operations.seed"></a>

#### seed

```python
def seed(e)
```

<a id="workflow_operations.save_slots"></a>

#### save\_slots

```python
def save_slots(e)
```

<a id="workflow_operations.resolve_inputs"></a>

#### resolve\_inputs

```python
def resolve_inputs(e, t, c)
```

<a id="workflow_operations.store_outputs"></a>

#### store\_outputs

```python
def store_outputs(e, t, c, vals)
```

<a id="workflow_operations.artifact_outputs"></a>

#### artifact\_outputs

```python
def artifact_outputs(e, t)
```

<a id="workflow_operations.execute_operation"></a>

#### execute\_operation

```python
def execute_operation(e, tx)
```

<a id="workflow_operations.install_operation_workflows"></a>

#### install\_operation\_workflows

```python
def install_operation_workflows()
```

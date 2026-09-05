> [← Project README](../../README.md)

# Table of Contents

* [action\_tree](#action_tree)
  * [StateNode](#action_tree.StateNode)
    * [path](#action_tree.StateNode.path)
    * [image\_hash](#action_tree.StateNode.image_hash)
    * [image\_path](#action_tree.StateNode.image_path)
    * [state\_path](#action_tree.StateNode.state_path)
    * [readme\_path](#action_tree.StateNode.readme_path)
    * [objects\_path](#action_tree.StateNode.objects_path)
    * [differences\_path](#action_tree.StateNode.differences_path)
    * [semantic\_records\_path](#action_tree.StateNode.semantic_records_path)
  * [ActionTreeStore](#action_tree.ActionTreeStore)
    * [STANDARD\_ACTION\_NAMES](#action_tree.ActionTreeStore.STANDARD_ACTION_NAMES)
    * [\_\_init\_\_](#action_tree.ActionTreeStore.__init__)
    * [object\_registry\_path](#action_tree.ActionTreeStore.object_registry_path)
    * [semantic\_identity\_decisions\_path](#action_tree.ActionTreeStore.semantic_identity_decisions_path)
    * [registry\_text](#action_tree.ActionTreeStore.registry_text)
    * [image\_hash](#action_tree.ActionTreeStore.image_hash)
    * [create\_initial](#action_tree.ActionTreeStore.create_initial)
    * [create\_transition](#action_tree.ActionTreeStore.create_transition)
    * [action\_slug](#action_tree.ActionTreeStore.action_slug)
    * [action\_path](#action_tree.ActionTreeStore.action_path)
    * [metadata](#action_tree.ActionTreeStore.metadata)
    * [parent\_node](#action_tree.ActionTreeStore.parent_node)
    * [child\_nodes](#action_tree.ActionTreeStore.child_nodes)
    * [FRIENDLY\_ID\_RE](#action_tree.ActionTreeStore.FRIENDLY_ID_RE)
    * [NEW\_FRIENDLY\_ID\_RE](#action_tree.ActionTreeStore.NEW_FRIENDLY_ID_RE)
    * [REGISTRY\_LOAD\_RE](#action_tree.ActionTreeStore.REGISTRY_LOAD_RE)
    * [OPAQUE\_ID\_RE](#action_tree.ActionTreeStore.OPAQUE_ID_RE)
    * [OPAQUE\_TOKEN\_RE](#action_tree.ActionTreeStore.OPAQUE_TOKEN_RE)
    * [SEMANTIC\_DECISION\_RE](#action_tree.ActionTreeStore.SEMANTIC_DECISION_RE)
    * [identity\_facts](#action_tree.ActionTreeStore.identity_facts)
    * [new\_identity\_facts](#action_tree.ActionTreeStore.new_identity_facts)
    * [opaque\_tokens](#action_tree.ActionTreeStore.opaque_tokens)
    * [registry\_reference](#action_tree.ActionTreeStore.registry_reference)
    * [validate\_friendly\_objects](#action_tree.ActionTreeStore.validate_friendly_objects)
    * [registry\_identities](#action_tree.ActionTreeStore.registry_identities)
    * [registry\_decisions](#action_tree.ActionTreeStore.registry_decisions)
    * [write\_registry](#action_tree.ActionTreeStore.write_registry)
    * [update\_registry\_from\_objects](#action_tree.ActionTreeStore.update_registry_from_objects)
    * [record\_semantic\_identity\_decision](#action_tree.ActionTreeStore.record_semantic_identity_decision)
    * [link\_semantic\_record](#action_tree.ActionTreeStore.link_semantic_record)
    * [link\_prediction\_history](#action_tree.ActionTreeStore.link_prediction_history)
    * [refresh\_readme](#action_tree.ActionTreeStore.refresh_readme)

<a id="action_tree"></a>

# action\_tree

<a id="action_tree.StateNode"></a>

## StateNode Objects

```python
@dataclass(frozen=True)
class StateNode()
```

<a id="action_tree.StateNode.path"></a>

#### path: `Path`

<a id="action_tree.StateNode.image_hash"></a>

#### image\_hash: `str`

<a id="action_tree.StateNode.image_path"></a>

#### image\_path

```python
@property
def image_path() -> Path
```

<a id="action_tree.StateNode.state_path"></a>

#### state\_path

```python
@property
def state_path() -> Path
```

<a id="action_tree.StateNode.readme_path"></a>

#### readme\_path

```python
@property
def readme_path() -> Path
```

<a id="action_tree.StateNode.objects_path"></a>

#### objects\_path

```python
@property
def objects_path() -> Path
```

<a id="action_tree.StateNode.differences_path"></a>

#### differences\_path

```python
@property
def differences_path() -> Path
```

<a id="action_tree.StateNode.semantic_records_path"></a>

#### semantic\_records\_path

```python
@property
def semantic_records_path() -> Path
```

<a id="action_tree.ActionTreeStore"></a>

## ActionTreeStore Objects

```python
class ActionTreeStore()
```

Filesystem-backed deterministic action tree.

The level directory is the initial state. Every action is a child directory
containing the resulting state:

  <root>/<game>/level_<n>/
      README.md
      image.png
      state.json
      objects.pl
      UP/
          README.md
          image.png
          state.json
          objects.pl
          differences.pl
          LEFT/
              ...

Thus the directory path itself is the complete action sequence.

<a id="action_tree.ActionTreeStore.STANDARD_ACTION_NAMES"></a>

#### STANDARD\_ACTION\_NAMES

<a id="action_tree.ActionTreeStore.__init__"></a>

#### \_\_init\_\_

```python
def __init__(root: str | Path, game_id: str, level: str | int) -> None
```

<a id="action_tree.ActionTreeStore.object_registry_path"></a>

#### object\_registry\_path

```python
@property
def object_registry_path() -> Path
```

<a id="action_tree.ActionTreeStore.semantic_identity_decisions_path"></a>

#### semantic\_identity\_decisions\_path

```python
@property
def semantic_identity_decisions_path() -> Path
```

<a id="action_tree.ActionTreeStore.registry_text"></a>

#### registry\_text

```python
def registry_text() -> str
```

<a id="action_tree.ActionTreeStore.image_hash"></a>

#### image\_hash

```python
@staticmethod
def image_hash(png_bytes: bytes) -> str
```

<a id="action_tree.ActionTreeStore.create_initial"></a>

#### create\_initial

```python
def create_initial(png_bytes: bytes, state_payload: Mapping[str,
                                                            Any]) -> StateNode
```

Create or reuse the level-root initial state.

<a id="action_tree.ActionTreeStore.create_transition"></a>

#### create\_transition

```python
def create_transition(parent: StateNode, action: str,
                      action_data: Mapping[str, Any], png_bytes: bytes,
                      state_payload: Mapping[str, Any]) -> StateNode
```

Create or reuse the child directory named by the action.

<a id="action_tree.ActionTreeStore.action_slug"></a>

#### action\_slug

```python
@classmethod
def action_slug(cls, action: str, data: Mapping[str, Any]) -> str
```

<a id="action_tree.ActionTreeStore.action_path"></a>

#### action\_path

```python
def action_path(path: Path) -> list[str]
```

<a id="action_tree.ActionTreeStore.metadata"></a>

#### metadata

```python
def metadata(node: StateNode) -> dict[str, Any]
```

<a id="action_tree.ActionTreeStore.parent_node"></a>

#### parent\_node

```python
def parent_node(node: StateNode) -> StateNode | None
```

<a id="action_tree.ActionTreeStore.child_nodes"></a>

#### child\_nodes

```python
def child_nodes(node: StateNode) -> list[tuple[str, StateNode]]
```

Return direct child action directories that contain captured states.

<a id="action_tree.ActionTreeStore.FRIENDLY_ID_RE"></a>

#### FRIENDLY\_ID\_RE

<a id="action_tree.ActionTreeStore.NEW_FRIENDLY_ID_RE"></a>

#### NEW\_FRIENDLY\_ID\_RE

<a id="action_tree.ActionTreeStore.REGISTRY_LOAD_RE"></a>

#### REGISTRY\_LOAD\_RE

<a id="action_tree.ActionTreeStore.OPAQUE_ID_RE"></a>

#### OPAQUE\_ID\_RE

<a id="action_tree.ActionTreeStore.OPAQUE_TOKEN_RE"></a>

#### OPAQUE\_TOKEN\_RE

<a id="action_tree.ActionTreeStore.SEMANTIC_DECISION_RE"></a>

#### SEMANTIC\_DECISION\_RE

<a id="action_tree.ActionTreeStore.identity_facts"></a>

#### identity\_facts

```python
def identity_facts(source: str) -> dict[str, str]
```

Extract canonical object_identity/3 declarations.

<a id="action_tree.ActionTreeStore.new_identity_facts"></a>

#### new\_identity\_facts

```python
def new_identity_facts(source: str) -> dict[str, str]
```

Convert new_object_identity/3 candidates into canonical declarations.

<a id="action_tree.ActionTreeStore.opaque_tokens"></a>

#### opaque\_tokens

```python
def opaque_tokens(source: str) -> list[str]
```

Return opaque numbered object tokens appearing anywhere in Prolog.

<a id="action_tree.ActionTreeStore.registry_reference"></a>

#### registry\_reference

```python
def registry_reference(node: StateNode) -> str
```

Relative Prolog path from a node to the level-wide registry.

<a id="action_tree.ActionTreeStore.validate_friendly_objects"></a>

#### validate\_friendly\_objects

```python
def validate_friendly_objects(source: str, node: StateNode) -> None
```

Validate either the registry itself or a registry-backed node file.

<a id="action_tree.ActionTreeStore.registry_identities"></a>

#### registry\_identities

```python
def registry_identities() -> dict[str, str]
```

<a id="action_tree.ActionTreeStore.registry_decisions"></a>

#### registry\_decisions

```python
def registry_decisions() -> tuple[dict[str, str], ...]
```

<a id="action_tree.ActionTreeStore.write_registry"></a>

#### write\_registry

```python
def write_registry(registry: Mapping[str, str]) -> Path
```

<a id="action_tree.ActionTreeStore.update_registry_from_objects"></a>

#### update\_registry\_from\_objects

```python
def update_registry_from_objects(node: StateNode) -> Path
```

Merge only newly declared identities; state files remain identity-light.

<a id="action_tree.ActionTreeStore.record_semantic_identity_decision"></a>

#### record\_semantic\_identity\_decision

```python
def record_semantic_identity_decision(
    *,
    identity_id: str,
    encounter_id: str,
    decision_id: str,
    status: str,
    evidence_ids: tuple[str, ...] = ()) -> Path
```

Append authoritative Phase 2 history for an existing friendly identity.

<a id="action_tree.ActionTreeStore.link_semantic_record"></a>

#### link\_semantic\_record

```python
def link_semantic_record(node: StateNode, *, record_type: str, record_id: str,
                         artifact_path: str | Path, schema_version: str,
                         deterministic_hash: str) -> Path
```

Link a Phase 2/3 record to a node without embedding it in state.json.

<a id="action_tree.ActionTreeStore.link_prediction_history"></a>

#### link\_prediction\_history

```python
def link_prediction_history(node: StateNode, semantic_store: Any,
                            prediction_id: str) -> Path
```

Materialize one prediction-before-outcome audit trail in this node.

<a id="action_tree.ActionTreeStore.refresh_readme"></a>

#### refresh\_readme

```python
def refresh_readme(node: StateNode) -> Path
```

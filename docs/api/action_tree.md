> [← Project README](../../README.md)

# Table of Contents

* [action\_tree](#action_tree)
  * [ActionTreeStore](#action_tree.ActionTreeStore)
    * [create\_initial](#action_tree.ActionTreeStore.create_initial)
    * [create\_transition](#action_tree.ActionTreeStore.create_transition)
    * [child\_nodes](#action_tree.ActionTreeStore.child_nodes)
    * [identity\_facts](#action_tree.ActionTreeStore.identity_facts)
    * [new\_identity\_facts](#action_tree.ActionTreeStore.new_identity_facts)
    * [opaque\_tokens](#action_tree.ActionTreeStore.opaque_tokens)
    * [registry\_reference](#action_tree.ActionTreeStore.registry_reference)
    * [validate\_friendly\_objects](#action_tree.ActionTreeStore.validate_friendly_objects)
    * [update\_registry\_from\_objects](#action_tree.ActionTreeStore.update_registry_from_objects)
    * [record\_semantic\_identity\_decision](#action_tree.ActionTreeStore.record_semantic_identity_decision)
    * [link\_semantic\_record](#action_tree.ActionTreeStore.link_semantic_record)
    * [link\_prediction\_history](#action_tree.ActionTreeStore.link_prediction_history)

<a id="action_tree"></a>

# action\_tree

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

<a id="action_tree.ActionTreeStore.child_nodes"></a>

#### child\_nodes

```python
def child_nodes(node: StateNode) -> list[tuple[str, StateNode]]
```

Return direct child action directories that contain captured states.

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

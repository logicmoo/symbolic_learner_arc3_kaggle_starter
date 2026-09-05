> [← Project README](../../README.md)

# Table of Contents

* [project\_paths](#project_paths)
  * [PROJECT\_ROOT](#project_paths.PROJECT_ROOT)
  * [config\_root](#project_paths.config_root)
  * [llm\_config\_path](#project_paths.llm_config_path)
  * [prompts\_root](#project_paths.prompts_root)
  * [environment\_files\_root](#project_paths.environment_files_root)
  * [action\_trees\_root](#project_paths.action_trees_root)
  * [analysis\_runs\_root](#project_paths.analysis_runs_root)
  * [prompts\_path](#project_paths.prompts_path)
  * [histories\_root](#project_paths.histories_root)
  * [exports\_root](#project_paths.exports_root)

<a id="project_paths"></a>

# project\_paths

<a id="project_paths.PROJECT_ROOT"></a>

#### PROJECT\_ROOT

<a id="project_paths.config_root"></a>

#### config\_root

```python
def config_root() -> Path
```

Return the selected config directory without creating a fake source.

<a id="project_paths.llm_config_path"></a>

#### llm\_config\_path

```python
def llm_config_path() -> Path
```

<a id="project_paths.prompts_root"></a>

#### prompts\_root

```python
def prompts_root() -> Path
```

Compatibility alias for the unified configuration directory.

<a id="project_paths.environment_files_root"></a>

#### environment\_files\_root

```python
def environment_files_root() -> Path
```

Compatibility alias for the unified configuration directory.

<a id="project_paths.action_trees_root"></a>

#### action\_trees\_root

```python
def action_trees_root() -> Path
```

<a id="project_paths.analysis_runs_root"></a>

#### analysis\_runs\_root

```python
def analysis_runs_root() -> Path
```

Domain-neutral name for the persisted observation/action evidence tree.

<a id="project_paths.prompts_path"></a>

#### prompts\_path

```python
def prompts_path() -> Path
```

Compatibility alias for the unified provider and prompt config.

<a id="project_paths.histories_root"></a>

#### histories\_root

```python
def histories_root(level_root: str | Path) -> Path
```

<a id="project_paths.exports_root"></a>

#### exports\_root

```python
def exports_root(level_root: str | Path) -> Path
```

> [← Project README](../../README.md)

# Table of Contents

* [project\_paths](#project_paths)
  * [config\_root](#project_paths.config_root)
  * [prompts\_root](#project_paths.prompts_root)
  * [environment\_files\_root](#project_paths.environment_files_root)
  * [analysis\_runs\_root](#project_paths.analysis_runs_root)
  * [prompts\_path](#project_paths.prompts_path)

<a id="project_paths"></a>

# project\_paths

<a id="project_paths.config_root"></a>

#### config\_root

```python
def config_root() -> Path
```

Return the selected config directory without creating a fake source.

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

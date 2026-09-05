> [← Project README](../../README.md)

# Table of Contents

* [arc3\_runner](#arc3_runner)
  * [action\_name](#arc3_runner.action_name)
  * [is\_complex\_action](#arc3_runner.is_complex_action)
  * [StepRecord](#arc3_runner.StepRecord)
    * [step](#arc3_runner.StepRecord.step)
    * [action](#arc3_runner.StepRecord.action)
    * [data](#arc3_runner.StepRecord.data)
    * [state](#arc3_runner.StepRecord.state)
    * [observation](#arc3_runner.StepRecord.observation)
    * [terminal\_output](#arc3_runner.StepRecord.terminal_output)
    * [frame\_path](#arc3_runner.StepRecord.frame_path)
    * [tree\_node](#arc3_runner.StepRecord.tree_node)
    * [as\_dict](#arc3_runner.StepRecord.as_dict)
  * [Arc3Runner](#arc3_runner.Arc3Runner)
    * [\_\_init\_\_](#arc3_runner.Arc3Runner.__init__)
    * [open](#arc3_runner.Arc3Runner.open)
    * [available\_games](#arc3_runner.Arc3Runner.available_games)
    * [game\_info](#arc3_runner.Arc3Runner.game_info)
    * [switch\_game](#arc3_runner.Arc3Runner.switch_game)
    * [action\_space](#arc3_runner.Arc3Runner.action_space)
    * [action\_table](#arc3_runner.Arc3Runner.action_table)
    * [resolve\_action](#arc3_runner.Arc3Runner.resolve_action)
    * [step](#arc3_runner.Arc3Runner.step)
    * [reset](#arc3_runner.Arc3Runner.reset)
    * [restart\_game](#arc3_runner.Arc3Runner.restart_game)
    * [state\_name](#arc3_runner.Arc3Runner.state_name)
    * [is\_win](#arc3_runner.Arc3Runner.is_win)
    * [is\_game\_over](#arc3_runner.Arc3Runner.is_game_over)
    * [history](#arc3_runner.Arc3Runner.history)
    * [save\_history](#arc3_runner.Arc3Runner.save_history)
    * [replay](#arc3_runner.Arc3Runner.replay)
    * [scorecard](#arc3_runner.Arc3Runner.scorecard)
    * [current\_level\_label](#arc3_runner.Arc3Runner.current_level_label)
    * [current\_selection\_summary](#arc3_runner.Arc3Runner.current_selection_summary)
    * [change\_level](#arc3_runner.Arc3Runner.change_level)
    * [show\_record](#arc3_runner.Arc3Runner.show_record)
    * [redraw](#arc3_runner.Arc3Runner.redraw)
    * [execute\_queued\_step](#arc3_runner.Arc3Runner.execute_queued_step)
    * [export\_state](#arc3_runner.Arc3Runner.export_state)
    * [current\_grid](#arc3_runner.Arc3Runner.current_grid)
    * [semantic\_authorization\_options](#arc3_runner.Arc3Runner.semantic_authorization_options)
    * [authorize\_semantic\_candidate](#arc3_runner.Arc3Runner.authorize_semantic_candidate)
    * [reject\_semantic\_candidate](#arc3_runner.Arc3Runner.reject_semantic_candidate)
    * [gpt\_command\_1](#arc3_runner.Arc3Runner.gpt_command_1)
    * [gpt\_command\_2](#arc3_runner.Arc3Runner.gpt_command_2)
    * [gpt\_command\_3](#arc3_runner.Arc3Runner.gpt_command_3)
    * [gpt\_command\_4](#arc3_runner.Arc3Runner.gpt_command_4)
    * [gpt\_command\_5](#arc3_runner.Arc3Runner.gpt_command_5)
    * [gpt\_command\_6](#arc3_runner.Arc3Runner.gpt_command_6)
    * [prolog\_command\_1](#arc3_runner.Arc3Runner.prolog_command_1)
    * [prolog\_command\_2](#arc3_runner.Arc3Runner.prolog_command_2)
    * [prolog\_command\_3](#arc3_runner.Arc3Runner.prolog_command_3)
    * [prolog\_command\_4](#arc3_runner.Arc3Runner.prolog_command_4)
    * [prolog\_command\_5](#arc3_runner.Arc3Runner.prolog_command_5)
    * [prolog\_command\_6](#arc3_runner.Arc3Runner.prolog_command_6)
    * [summary\_for\_prolog](#arc3_runner.Arc3Runner.summary_for_prolog)

<a id="arc3_runner"></a>

# arc3\_runner

<a id="arc3_runner.action_name"></a>

#### action\_name

```python
def action_name(action: Any) -> str
```

<a id="arc3_runner.is_complex_action"></a>

#### is\_complex\_action

```python
def is_complex_action(action: Any) -> bool
```

<a id="arc3_runner.StepRecord"></a>

## StepRecord Objects

```python
@dataclass
class StepRecord()
```

<a id="arc3_runner.StepRecord.step"></a>

#### step: `int`

<a id="arc3_runner.StepRecord.action"></a>

#### action: `str`

<a id="arc3_runner.StepRecord.data"></a>

#### data: `dict[str, Any]`

<a id="arc3_runner.StepRecord.state"></a>

#### state: `str | None`

<a id="arc3_runner.StepRecord.observation"></a>

#### observation: `Any`

<a id="arc3_runner.StepRecord.terminal_output"></a>

#### terminal\_output: `str`

<a id="arc3_runner.StepRecord.frame_path"></a>

#### frame\_path: `str | None`

<a id="arc3_runner.StepRecord.tree_node"></a>

#### tree\_node: `str | None`

<a id="arc3_runner.StepRecord.as_dict"></a>

#### as\_dict

```python
def as_dict() -> dict[str, Any]
```

<a id="arc3_runner.Arc3Runner"></a>

## Arc3Runner Objects

```python
class Arc3Runner()
```

Debuggable ARC3 environment with a persistent deterministic action tree.

<a id="arc3_runner.Arc3Runner.__init__"></a>

#### \_\_init\_\_

```python
def __init__(
    game_id: str = "ls20",
    render_mode: str | None = "terminal",
    arc_api_key: str | None = None,
    capture_terminal: bool = False,
    tree_root: str | Path | None = None,
    capture_observers: Iterable[Any] = ()
) -> None
```

<a id="arc3_runner.Arc3Runner.open"></a>

#### open

```python
def open() -> Any
```

<a id="arc3_runner.Arc3Runner.available_games"></a>

#### available\_games

```python
def available_games() -> list[Any]
```

<a id="arc3_runner.Arc3Runner.game_info"></a>

#### game\_info

```python
@staticmethod
def game_info(game: Any) -> dict[str, Any]
```

<a id="arc3_runner.Arc3Runner.switch_game"></a>

#### switch\_game

```python
def switch_game(game_id: str) -> Any
```

<a id="arc3_runner.Arc3Runner.action_space"></a>

#### action\_space

```python
@property
def action_space() -> list[Any]
```

<a id="arc3_runner.Arc3Runner.action_table"></a>

#### action\_table

```python
def action_table() -> list[dict[str, Any]]
```

<a id="arc3_runner.Arc3Runner.resolve_action"></a>

#### resolve\_action

```python
def resolve_action(action: Any) -> Any
```

<a id="arc3_runner.Arc3Runner.step"></a>

#### step

```python
def step(action: Any,
         *,
         x: int | None = None,
         y: int | None = None,
         data: Mapping[str, Any] | None = None,
         reasoning: Mapping[str, Any] | None = None) -> Any
```

<a id="arc3_runner.Arc3Runner.reset"></a>

#### reset

```python
def reset(*, clear_history: bool = True) -> Any
```

<a id="arc3_runner.Arc3Runner.restart_game"></a>

#### restart\_game

```python
def restart_game() -> Any
```

<a id="arc3_runner.Arc3Runner.state_name"></a>

#### state\_name

```python
def state_name() -> str | None
```

<a id="arc3_runner.Arc3Runner.is_win"></a>

#### is\_win

```python
def is_win() -> bool
```

<a id="arc3_runner.Arc3Runner.is_game_over"></a>

#### is\_game\_over

```python
def is_game_over() -> bool
```

<a id="arc3_runner.Arc3Runner.history"></a>

#### history

```python
def history() -> list[dict[str, Any]]
```

<a id="arc3_runner.Arc3Runner.save_history"></a>

#### save\_history

```python
def save_history(path: str | Path) -> Path
```

<a id="arc3_runner.Arc3Runner.replay"></a>

#### replay

```python
def replay(
        records: Sequence[StepRecord | Mapping[str, Any]] | None = None
) -> Any
```

<a id="arc3_runner.Arc3Runner.scorecard"></a>

#### scorecard

```python
def scorecard() -> Any
```

<a id="arc3_runner.Arc3Runner.current_level_label"></a>

#### current\_level\_label

```python
def current_level_label() -> str
```

<a id="arc3_runner.Arc3Runner.current_selection_summary"></a>

#### current\_selection\_summary

```python
def current_selection_summary() -> str
```

<a id="arc3_runner.Arc3Runner.change_level"></a>

#### change\_level

```python
def change_level(delta: int) -> Any
```

<a id="arc3_runner.Arc3Runner.show_record"></a>

#### show\_record

```python
def show_record(index: int) -> None
```

<a id="arc3_runner.Arc3Runner.redraw"></a>

#### redraw

```python
def redraw() -> Any
```

<a id="arc3_runner.Arc3Runner.execute_queued_step"></a>

#### execute\_queued\_step

```python
def execute_queued_step() -> Any
```

<a id="arc3_runner.Arc3Runner.export_state"></a>

#### export\_state

```python
def export_state(path: str | Path) -> Path
```

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

<a id="arc3_runner.Arc3Runner.authorize_semantic_candidate"></a>

#### authorize\_semantic\_candidate

```python
def authorize_semantic_candidate(
        *,
        candidate_id: str,
        selected_identity_id: str,
        decision_id: str,
        decision_source: str = "explicit_registry_selection") -> Any
```

<a id="arc3_runner.Arc3Runner.reject_semantic_candidate"></a>

#### reject\_semantic\_candidate

```python
def reject_semantic_candidate(
        *,
        candidate_id: str,
        selected_identity_id: str,
        decision_id: str,
        decision_source: str = "explicit_registry_rejection") -> Any
```

<a id="arc3_runner.Arc3Runner.gpt_command_1"></a>

#### gpt\_command\_1

```python
def gpt_command_1() -> None
```

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

<a id="arc3_runner.Arc3Runner.gpt_command_5"></a>

#### gpt\_command\_5

```python
def gpt_command_5() -> None
```

<a id="arc3_runner.Arc3Runner.gpt_command_6"></a>

#### gpt\_command\_6

```python
def gpt_command_6() -> None
```

<a id="arc3_runner.Arc3Runner.prolog_command_1"></a>

#### prolog\_command\_1

```python
def prolog_command_1() -> None
```

<a id="arc3_runner.Arc3Runner.prolog_command_2"></a>

#### prolog\_command\_2

```python
def prolog_command_2() -> None
```

<a id="arc3_runner.Arc3Runner.prolog_command_3"></a>

#### prolog\_command\_3

```python
def prolog_command_3() -> None
```

<a id="arc3_runner.Arc3Runner.prolog_command_4"></a>

#### prolog\_command\_4

```python
def prolog_command_4() -> None
```

<a id="arc3_runner.Arc3Runner.prolog_command_5"></a>

#### prolog\_command\_5

```python
def prolog_command_5() -> None
```

<a id="arc3_runner.Arc3Runner.prolog_command_6"></a>

#### prolog\_command\_6

```python
def prolog_command_6() -> None
```

<a id="arc3_runner.Arc3Runner.summary_for_prolog"></a>

#### summary\_for\_prolog

```python
def summary_for_prolog() -> dict[str, Any]
```

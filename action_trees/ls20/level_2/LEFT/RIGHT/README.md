# `ls20` level `2` — LEFT / RIGHT

## Navigation

[Level start](../../README.md) · [Parent](../README.md)

### Actions

[`LEFT`](LEFT/README.md)

---

- **Full game ID:** `ls20`
- **State:** `NOT_FINISHED`
- **Image hash:** `0e078204c19c3c04`
- **Incoming action:** `ACTION4`

## Image

![ARC3 state](image.png)

## Files

- [image.png](image.png)
- [state.json](state.json)
- [object_registry.pl](../../object_registry.pl) — shared level registry (0 canonical identities)

## Embedded files

*Canonical identities are shared through [`object_registry.pl`](../../object_registry.pl) and are not repeated in every node.*

<details>
<summary><code>state.json</code></summary>

````json
{
  "state": "NOT_FINISHED",
  "level": "2",
  "level_source": "scorecard.completed_levels+1",
  "next_level_expected": null,
  "observation": {
    "game_id": "ls20-9607627b",
    "state": "NOT_FINISHED",
    "levels_completed": 1,
    "win_levels": 7,
    "action_input": {
      "id": "ACTION4",
      "data": {},
      "reasoning": null
    },
    "guid": "36f2d7f2-25ea-4100-8983-30d4c064bef5",
    "full_reset": false,
    "available_actions": [
      1,
      2,
      3,
      4
    ]
  },
  "step_count": 1,
  "game_id": "ls20",
  "game_directory": "ls20",
  "image_hash": "0e078204c19c3c04",
  "incoming_action": "ACTION4",
  "action_directory": "RIGHT",
  "action_data": {},
  "parent_node": "..",
  "action_path": [
    "LEFT",
    "RIGHT"
  ]
}
````

[Open `state.json`](state.json)

</details>

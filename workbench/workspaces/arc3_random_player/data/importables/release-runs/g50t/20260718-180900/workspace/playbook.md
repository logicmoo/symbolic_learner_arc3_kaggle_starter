# Working model

- **Checked (levels 1–6):** Logical movement centers are 6 pixels apart. ACTION1=up, ACTION2=down, ACTION3=left, ACTION4=right. Legal moves usually animate; color 5 is track. Active is a color-9 5x5 ring, and entering the color-9 framed/dot goal completes a level. Thin one-cell wires are not traversable.
- **Checked (levels 1–6):** ACTION5 stores the active timeline as a color-2 clone and rewinds active and dynamic devices to level start. On later directional inputs each clone replays its own stored inputs, then holds its endpoint. HUD slots bound the number of rewinds; keep the final slot for the live active.
- **Checked (levels 1–6):** Color-8 is a 3x3 pressure pad wired to a notched 5x5 blocker. Occupying the pad moves the blocker off its track node; leaving/restoring timelines closes it. A finished clone can hold a pad.
- **Checked (levels 3–6):** Color-11 is a 3x3 control wired to a solid 5x5 blocker. Touching the control latches its blocker open until ACTION5/reset; clone replay can retrigger it.
- **Checked (levels 4–6):** Color-15 is a 3x3 one-shot trigger wired to paired 7x7 portal frames. Trigger entry teleports any avatar currently centered in either paired frame to the other; simultaneous trigger/portal entry works. The pulse is transient.
- **Checked (levels 6–7, corrected at level 7):** Color-14 follows its own fixed corridor, advancing one 6-pixel step whenever the live active makes a successful move, independent of direction. It does not advance on a blocked active move, **reverses direction at each corridor endpoint (ping-pong patrol rather than holding)**, and rewinds with ACTION5. This retrodicts all level-6 positions after its first endpoint.
- **Checked (levels 1–6):** Changing color-9 bottom border is an action-budget bar, not terrain.
- **Safety:** RESET restarts this level; never RESET twice consecutively. Prefer expectations and ACTION5 only when intentionally recording a timeline.

# Working memory

- **Level 7, step 281; 6/7 complete.** Both timelines are stored successfully: T1 ends on pad `(16,4)`, and T2 ends on right trigger `(52,4)`. Active and color-14 are reset to `(28,28)` and `(22,58)`; no rewind slots remain. Goal `(34,52)`.
- **Checked geometry (Python):** Color-14's unique corridor is `(22,58)->(16,58)->(10,58)->(4,58)->(4,52)->(4,46)->(4,40)->(4,34)->(4,28)`. Control `(22,40)` latches blocker `(4,40)`. Left trigger `(4,28)` pairs portals `(16,28)` and `(16,16)`. Pad `(16,4)` opens blocker `(34,4)`. Right trigger `(52,4)` pairs portals `(52,40)` and `(52,52)`.
- **Computed two-clone solution:** T1 `D2,L,R,U2,L2,U2` (10 moves): latch at t3, active reaches `(16,28)` exactly as bot reaches trigger at t8, teleport to `(16,16)`, then reach/hold pad `(16,4)` at t10. Rewind/store. T2 `D2,R2,U4,L,U2,R3` (14): T1 relatches/teleports/reaches pad at t10, active crosses opened blocker t11 and ends on right trigger `(52,4)` t14. Rewind/store. Final `D2,R2,U4,R2,D4,L3`: reach portal `(52,40)` at t14 exactly as T2 triggers it, teleport to `(52,52)`, then left three into goal.
- **Next:** Final live route `D2,R2,U4,R2,D4,L3`. At t14 active enters portal `(52,40)` exactly as T2 enters trigger `(52,4)`, so it should teleport to `(52,52)`; three left moves then reach goal `(34,52)` and win 7/7.
- **Ruled out on level 7:** color-14 holding at an endpoint; step 264 proved it reverses immediately on the next successful move.

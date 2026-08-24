# Working model

- **[Checked through level 7]** Only `ACTION6(x,y)` has been needed. Buttons apply fixed cyclic permutations; one action can couple separated cycles, and different actions can overlap at transfer slots. Infer membership/direction from exact diffs, never button proximity or reused shape alone.
- **[Checked through level 7]** Completion requires every special tile in a same-color corner-marked target. Same-color tokens are interchangeable; ordinary colors are only permutation evidence and can create misleading equal-color coincidences.
- **[Checked level 7]** Opposing arrows can be exact inverses. Routing may require parking/rephasing tokens on local subcycles before a shared global move. Once generators are known, BFS over token positions gives the shortest word.
- **[Checked]** `x=0` is the move budget and top bars are progress (7/8), not pieces.
- **[Method]** Read exact diffs first; distinguish a true fixed/mapped cell from equal-color masking. Probe unknown generators with token expectations, then batch the computed solution.

# Working memory

- Level 8/final began at step 80. Three 11 tokens began `(18,9),(18,18),(18,27)`; marked targets are `(36,51),(30,51),(24,51)` for systems P1/P2/P3 respectively.
- Four inverse pairs: top local P1 `(49/53,25)`, middle local P2 `(49/53,30)`, lower local P3 `(49/53,35)`, and global G `(31/36,58)`; left is inverse/minus, right is plus.
- **Checked:** global-right `G+` advances each of three 23-position winding cycles by +1; global-left at step 85 exactly reversed it. Crucial correction: each marked target is global index 22, immediately preceding local/natural index 0 (`G+ target→index0`, `G- index0→target`). Earlier apparent propagation down vertical branches into targets was equal-color masking, not valid mapping.
- **Checked locals:** middle-right is +1 on P2 indices `0..5`, coordinates `(6,6),(9,9),…,(21,21)`, wrapping 5→0. Lower-right is +1 on P3 indices `0..6`, `(3,12),(6,15),…,(21,30)`, wrapping 6→0. Pattern predicts top local is P1 indices `0..4`; only inverse map 1→0 is needed and will be expectation-checked.
- Actions so far on this level: `G+`, `P2+`, `P3+`, `P2+`, `G-`. Current token state is P1/P2/P3 `(0,0,22)`: P1 `(18,9)`, P2 `(6,6)`, P3 already in target `(24,51)`.
- Corrected BFS goal is `(22,22,22)`, not differing branch indices. Shortest remaining word is four actions: `G+, P1-, P2-, G-`. Predicted states/coordinates: after G+, `(1,1,0)` = `(21,12),(9,9),(3,12)`; top-left P1- gives `(0,1,0)` with P1 `(18,9)`; middle-left P2- gives `(0,0,0)` with P2 `(6,6)`; final G- sends all three index0 tokens directly into `(36,51),(30,51),(24,51)` and should win 8/8.

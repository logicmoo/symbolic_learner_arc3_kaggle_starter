# Working model
- **Confirmed:** A clue’s micro-code 0 requires a neighboring tile’s underlying palette color to equal the clue core; code2 requires any unequal palette color; code3 means no constraint (outside shape or another clue). Merge all clue constraints by absolute lattice position.
- **Confirmed:** Top-right swatches give the forward click cycle. Clicking an editable tile advances its underlying/base color one step while decorative color6 pixels remain.
- **Confirmed special-effect encoding:** Color6 marks directions affected by a click. A level-5 checker button had color6 at all four cardinal micro-positions; clicking it toggled its own base plus the four orthogonal ordinary neighbors. Clue tiles are immune. Level 5 completed after all three such buttons were set and their unwanted neighbor effects compensated.
- **Confirmed HUD:** y=63 is only a click-budget bar.

# Working memory
- Final level 6, 5/6 completed; only ACTION6. Palette is binary [11,14]. There are 22 editable textured buttons and four fixed clues on lattice origins x=[4,12,20,28,36,44,52], y=[6,14,22,30,38,46].
- Every button pattern has one color6 marker at its north micro-position. By the confirmed level-5 encoding, clicking a button toggles its own base and the immediately north ordinary button; it skips absent cells and immutable clues.
- Clue centers are lattice (1,0),(4,2),(2,3),(5,5), all core14. Python decoded all 22 buttons: 12 require final14 and 10 require final11, with no conflicts and no unconstrained buttons.
- Solved the binary click equations independently by column: final bit at `(c,r)` is `click(c,r) XOR click(c,r+1)` when a south button exists. The unique minimum has 13 clicks at lattice (0,0),(0,1),(2,1),(4,1),(1,2),(2,2),(1,3),(3,3),(4,3),(5,3),(2,4),(5,4),(6,4), grid coordinates (6,8),(6,16),(22,16),(38,16),(14,24),(22,24),(14,32),(30,32),(38,32),(46,32),(22,40),(46,40),(54,40).
- A row-major forward simulation reproduces every required final color exactly. Key cancellations: (0,0), (2,1), (1,2), and (5,3) are clicked/toggled back by their south button. Execute all 13 with side-effect expectations; final click should produce 6/6 and WIN.

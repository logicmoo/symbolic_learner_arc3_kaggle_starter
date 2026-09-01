# Working model

- **Checked through level 6:** The avatar is a fixed 5x5 sprite (color 12 in its top two rows, color 9 in its bottom three) moving on lattice centers `x=11+5c, y=7+5r`. Controls: ACTION1=up, ACTION2=down, ACTION3=left, ACTION4=right. Color-3 centers are floor and color-4 centers are walls.
- **Critical checked timing rule:** The lower timer drains on every input, including blocked inputs, but moving glyphs advance one trajectory phase **only when the avatar successfully changes settled lattice position** (a conveyor jump counts as one). A blocked input freezes all glyphs and does not retrigger an overlap effect.
- **Checked:** Transformation effects occur when the avatar and a glyph share the resulting position after a successful move; a glyph hidden under the avatar appears absent.
- **Checked:** The lower-left HUD is a 3x3 binary pattern at 2x scale. A 7x7 patterned chamber is a lock; entering with matching pattern and foreground color dissolves it. A level with multiple locks requires opening all locks.
- **Checked:** R (black/white plus) rotates the pattern 90° clockwise, preserving color. C (multicolor ring) preserves pattern and cycles color `14→8→12→9→14`. B preserves color and advances the six-shape cycle `A→T→H→P→Q→R→A` while preserving orientation. Level-6 glyph trajectories advanced only on successful moves and had period 8.
- **Checked:** Count the two-row color-11 timer columns, not changed cells. Level 6 drains one column/input; **level 7 drains two columns/input** (only 21 inputs from full). Hollow color-11 rings refill to 42 columns on entry and are one-use.
- **Checked:** A 5-cell edge bar marks a conveyor source. Entering its adjacent floor tile launches away from the bar through contiguous floor in that same successful move.
- **Checked:** Level 6 was completed by the predicted 25-action movement-phase route; its two-lock timing model was correct.
- **Checked on level 7 step 321:** Level 7 uses a circular visibility/fog mask of radius about 20 centered on the avatar. On a move from `(21,17)` to `(21,12)`, fixed terrain stayed anchored while the visible disk shifted upward by 5. Do not treat off-screen objects or color-5 cells outside the disk as absent terrain.

# Working memory

- Level 7 current step 380, successful-move count 60. Avatar `(c0,r6)=(11,37)`, timer 30. Probe expectation passed: C remained at c0r7 and B at c2r7, confirming both are stationary for the planned repeated entries. HUD color 12 pattern `111/010/010`; need exactly 3 C and 5 B hits, no R.
- Execute exact finish: `DRRLLRRLLRD` gives C1/B1/C2/B2/C3, then consumes ring c1r8 (timer refills from 8 to42); `URLRLR` gives B3-B5; `ULLUURRRRDDDDD` reaches the matching c4r9 lock. Post-ring segment is exactly 20 inputs and leaves two timer columns on lock entry.
- Expected HUD progression: C1 color9 S1; B1 color9 S2=`111/101/101`; C2 color14 S2; B2 color14 S3=`010/101/110`; C3 color8 S3; B3 S4=`110/011/010`; B4 S5=`101/100/111`; B5 target S0=`101/110/011`. Enter lock with color8 S0 to complete level 7 / win.
- R period10 on c9; avoid it. Conveyors: top c6r3→c6r7, right c6r5→c4r5, bottom c5r5 launches up.

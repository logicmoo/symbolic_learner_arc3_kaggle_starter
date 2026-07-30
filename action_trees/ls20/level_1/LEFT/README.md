# `ls20` level `1` — LEFT

## Navigation

[Level start](../README.md) · [Parent](../README.md)

### Actions

[`LEFT`](LEFT/README.md) · [`UP`](UP/README.md)

---

- **Full game ID:** `ls20`
- **State:** `NOT_FINISHED`
- **Image hash:** `c8aac72598f024fd`
- **Incoming action:** `ACTION3`

## Image

![ARC3 state](image.png)

## Files

- [image.png](image.png)
- [state.json](state.json)
- [object_registry.pl](../object_registry.pl) — shared level registry (25 canonical identities)
- [differences.pl](differences.pl)
- [objects.pl](objects.pl)
- [redraw.pl](redraw.pl)
- [redraw_diff.pl](redraw_diff.pl)
- [rules.pl](rules.pl)
- [similarities.pl](similarities.pl)
- [turtle_from_diff.pl](turtle_from_diff.pl)
- [turtle_from_image.pl](turtle_from_image.pl)

## Embedded files

*Canonical identities are shared through [`object_registry.pl`](../object_registry.pl) and are not repeated in every node.*

<details>
<summary><code>state.json</code></summary>

````json
{
  "state": "NOT_FINISHED",
  "level": "1",
  "level_source": "default",
  "next_level_expected": null,
  "observation": {
    "game_id": "ls20-9607627b",
    "state": "NOT_FINISHED",
    "levels_completed": 0,
    "win_levels": 7,
    "action_input": {
      "id": "ACTION3",
      "data": {},
      "reasoning": null
    },
    "guid": "8cc5692c-f46e-4662-a43c-97c0f8376183",
    "full_reset": false,
    "available_actions": [
      1,
      2,
      3,
      4
    ]
  },
  "step_count": 0,
  "game_id": "ls20",
  "game_directory": "ls20",
  "image_hash": "c8aac72598f024fd",
  "incoming_action": "ACTION3",
  "action_directory": "LEFT",
  "action_data": {},
  "parent_node": "..",
  "action_path": [
    "LEFT"
  ]
}
````

[Open `state.json`](state.json)

</details>

<details>
<summary><code>differences.pl</code></summary>

````prolog
transition(action3,parent,current).

moved(bottom_center_gate,delta(-5,0)).
transition_evidence(bottom_center_gate,parent_bbox,bbox(34,45,5,5)).
transition_evidence(bottom_center_gate,current_bbox,bbox(29,45,5,5)).
transition_evidence(bottom_center_gate,preserved_geometry,[size(5,5),colors([gray,dark_red]),gray_rows(0,1),dark_red_rows(2,4)]).

moved(gray_gate_cap,delta(-5,0)).
transition_evidence(gray_gate_cap,parent_cells,[rows(45,46,34,38)]).
transition_evidence(gray_gate_cap,current_cells,[rows(45,46,29,33)]).

moved(red_gate_base,delta(-5,0)).
transition_evidence(red_gate_base,parent_cells,[rows(47,49,34,38)]).
transition_evidence(red_gate_base,current_cells,[rows(47,49,29,33)]).

reshaped(green_main_platform).
reshaped(green_maze_structure).
overwritten_cells(green_main_platform,bottom_center_gate,[rows(45,49,29,33)]).
restored_cells(green_main_platform,green,[rows(45,49,34,38)]).
transition_evidence(green_main_platform,parent_lower_runs,[rows(45,49,19,33),rows(45,49,39,53)]).
transition_evidence(green_main_platform,current_lower_runs,[rows(45,49,19,28),rows(45,49,34,53)]).
transition_evidence(green_main_platform,preserved_area,820).
transition_evidence(green_maze_structure,preserved_area,892).

appeared(bottom_green_status_bar).
created(bottom_green_status_bar,[rows(61,62,13,13)],green).
recolored(bottom_status_panel,dark_gray,green,[rows(61,62,13,13)]).
resized(bottom_dark_status_bar,size(42,2),size(41,2)).
transition_evidence(bottom_dark_status_bar,parent_bbox,bbox(13,61,42,2)).
transition_evidence(bottom_dark_status_bar,current_bbox,bbox(14,61,41,2)).
transition_evidence(bottom_status_panel,changed_cells,[rows(61,62,13,13)]).

unchanged(blue_black_player,[bbox(20,31,3,3),occupied_cells([cell(21,31),cell(20,32),cell(21,32),cell(22,32),cell(21,33)])]).
unchanged(yellow_inner_cavity,[bbox(24,30,10,15),area(100)]).
unchanged(green_upper_chamber_frame,[bbox(32,8,9,9),area(32)]).
unchanged(lower_left_control_panel,[bbox(1,53,10,10),area(100)]).
unchanged(bottom_status_panel,[bbox(12,60,52,4),area(208)]).
unchanged(left_cyan_status_cell,[bbox(56,61,2,2),color(cyan)]).
unchanged(middle_cyan_status_cell,[bbox(59,61,2,2),color(cyan)]).
unchanged(right_cyan_status_cell,[bbox(62,61,2,2),color(cyan)]).
````

[Open `differences.pl`](differences.pl)

</details>

<details>
<summary><code>objects.pl</code></summary>

````prolog
% Canonical identities are loaded from the level registry.
:- ensure_loaded('../object_registry.pl').

% State-specific facts for this action-tree node.
object(yellow_playfield,background,current).
color(yellow_playfield,yellow).
bbox(yellow_playfield,0,0,64,64).
area(yellow_playfield,2509).
cell_runs(yellow_playfield,[rows(0,7,4,63),rows(8,16,4,31),rows(8,16,41,63),rows(17,24,4,33),rows(17,24,39,63),rows(25,29,4,13),rows(25,29,54,63),rows(30,39,4,13),rows(30,39,54,63),rows(40,44,4,18),rows(40,44,54,63),rows(45,49,4,18),rows(45,49,54,63),rows(50,51,4,63),rows(52,52,0,63),rows(53,59,0,0),rows(53,59,11,63),rows(60,62,0,0),rows(60,62,11,11),rows(63,63,0,11)]).
shape(yellow_playfield,irregular_background).
role(yellow_playfield,playfield_background).
confidence(yellow_playfield,1.0).

object(left_gray_border,border,current).
color(left_gray_border,gray).
bbox(left_gray_border,0,0,4,52).
size(left_gray_border,4,52).
area(left_gray_border,208).
cell_runs(left_gray_border,[rows(0,51,0,3)]).
shape(left_gray_border,solid_rectangle).
orientation(left_gray_border,vertical).
role(left_gray_border,boundary).
touches(left_gray_border,yellow_playfield).
confidence(left_gray_border,1.0).

object(green_maze_structure,compound_structure,current).
color(green_maze_structure,green).
bbox(green_maze_structure,14,8,40,42).
area(green_maze_structure,892).
cell_runs(green_maze_structure,[rows(8,8,32,40),rows(9,15,32,32),rows(9,15,40,40),rows(16,16,32,40),rows(17,24,34,38),rows(25,29,14,53),rows(30,30,14,28),rows(30,30,34,53),rows(31,31,14,20),rows(31,31,22,28),rows(31,31,34,53),rows(32,32,14,19),rows(32,32,23,28),rows(32,32,34,53),rows(33,33,14,20),rows(33,33,22,28),rows(33,33,34,53),rows(34,39,14,28),rows(34,39,34,53),rows(40,44,19,23),rows(40,44,34,53),rows(45,49,19,28),rows(45,49,34,53)]).
shape(green_maze_structure,connected_maze_structure).
contains(green_maze_structure,gray_upper_chamber_interior).
contains(green_maze_structure,yellow_inner_cavity).
contains(green_maze_structure,bottom_center_gate).
role(green_maze_structure,main_play_structure).
confidence(green_maze_structure,1.0).

object(green_upper_chamber_frame,enclosure,current).
color(green_upper_chamber_frame,green).
bbox(green_upper_chamber_frame,32,8,9,9).
size(green_upper_chamber_frame,9,9).
area(green_upper_chamber_frame,32).
cell_runs(green_upper_chamber_frame,[rows(8,8,32,40),rows(9,15,32,32),rows(9,15,40,40),rows(16,16,32,40)]).
shape(green_upper_chamber_frame,rectangular_frame).
symmetry(green_upper_chamber_frame,vertical).
component_of(green_upper_chamber_frame,green_maze_structure).
contains(green_upper_chamber_frame,gray_upper_chamber_interior).
contains(green_upper_chamber_frame,upper_red_hook_glyph).
contains(green_upper_chamber_frame,upper_red_square).
confidence(green_upper_chamber_frame,1.0).

object(gray_upper_chamber_interior,chamber,current).
color(gray_upper_chamber_interior,gray).
bbox(gray_upper_chamber_interior,33,9,7,7).
size(gray_upper_chamber_interior,7,7).
area(gray_upper_chamber_interior,43).
cell_runs(gray_upper_chamber_interior,[rows(9,10,33,39),rows(11,11,33,34),rows(11,11,38,39),rows(12,12,33,36),rows(12,12,38,39),rows(13,13,33,34),rows(13,13,36,36),rows(13,13,38,39),rows(14,15,33,39)]).
shape(gray_upper_chamber_interior,rectangular_interior_with_glyph_occlusions).
inside(gray_upper_chamber_interior,green_upper_chamber_frame).
confidence(gray_upper_chamber_interior,1.0).

object(upper_red_hook_glyph,glyph,current).
color(upper_red_hook_glyph,dark_red).
bbox(upper_red_hook_glyph,35,11,3,3).
size(upper_red_hook_glyph,3,3).
area(upper_red_hook_glyph,5).
cell_runs(upper_red_hook_glyph,[rows(11,11,35,37),rows(12,13,37,37)]).
shape(upper_red_hook_glyph,hook).
inside(upper_red_hook_glyph,green_upper_chamber_frame).
component_of(upper_red_hook_glyph,gray_upper_chamber_interior).
confidence(upper_red_hook_glyph,1.0).

object(upper_red_square,glyph_component,current).
color(upper_red_square,dark_red).
bbox(upper_red_square,35,13,1,1).
size(upper_red_square,1,1).
area(upper_red_square,1).
occupied_cells(upper_red_square,[cell(35,13)]).
shape(upper_red_square,single_cell_square).
inside(upper_red_square,green_upper_chamber_frame).
aligned_with(upper_red_square,upper_red_hook_glyph,left_edge).
confidence(upper_red_square,1.0).

object(green_chamber_stem,vertical_bar,current).
color(green_chamber_stem,green).
bbox(green_chamber_stem,34,17,5,8).
size(green_chamber_stem,5,8).
area(green_chamber_stem,40).
cell_runs(green_chamber_stem,[rows(17,24,34,38)]).
shape(green_chamber_stem,solid_rectangle).
orientation(green_chamber_stem,vertical).
component_of(green_chamber_stem,green_maze_structure).
touches(green_chamber_stem,green_upper_chamber_frame).
touches(green_chamber_stem,green_main_platform).
confidence(green_chamber_stem,1.0).

object(green_main_platform,platform,current).
color(green_main_platform,green).
bbox(green_main_platform,14,25,40,25).
size(green_main_platform,40,25).
area(green_main_platform,820).
cell_runs(green_main_platform,[rows(25,29,14,53),rows(30,30,14,28),rows(30,30,34,53),rows(31,31,14,20),rows(31,31,22,28),rows(31,31,34,53),rows(32,32,14,19),rows(32,32,23,28),rows(32,32,34,53),rows(33,33,14,20),rows(33,33,22,28),rows(33,33,34,53),rows(34,39,14,28),rows(34,39,34,53),rows(40,44,19,23),rows(40,44,34,53),rows(45,49,19,28),rows(45,49,34,53)]).
shape(green_main_platform,stepped_platform_with_enclosed_cavity).
component_of(green_main_platform,green_maze_structure).
contains(green_main_platform,yellow_inner_cavity).
contains(green_main_platform,bottom_center_gate).
confidence(green_main_platform,1.0).

object(yellow_inner_cavity,hole,current).
color(yellow_inner_cavity,yellow).
bbox(yellow_inner_cavity,24,30,10,15).
size(yellow_inner_cavity,10,15).
area(yellow_inner_cavity,100).
cell_runs(yellow_inner_cavity,[rows(30,39,29,33),rows(40,44,24,33)]).
shape(yellow_inner_cavity,stepped_cavity).
inside(yellow_inner_cavity,green_main_platform).
inside(yellow_inner_cavity,green_maze_structure).
adjacent(yellow_inner_cavity,green_main_platform).
adjacent(yellow_inner_cavity,bottom_center_gate).
role(yellow_inner_cavity,enclosed_hole).
confidence(yellow_inner_cavity,1.0).

object(blue_black_player,player,current).
colors(blue_black_player,[black,blue]).
bbox(blue_black_player,20,31,3,3).
size(blue_black_player,3,3).
area(blue_black_player,5).
occupied_cells(blue_black_player,[cell(21,31),cell(20,32),cell(21,32),cell(22,32),cell(21,33)]).
shape(blue_black_player,asymmetric_cross_marker).
inside(blue_black_player,green_main_platform).
role(blue_black_player,player_marker).
confidence(blue_black_player,1.0).

object(black_player_head,player_component,current).
color(black_player_head,black).
bbox(black_player_head,21,31,2,2).
size(black_player_head,2,2).
area(black_player_head,3).
occupied_cells(black_player_head,[cell(21,31),cell(21,32),cell(22,32)]).
shape(black_player_head,right_facing_corner).
component_of(black_player_head,blue_black_player).
confidence(black_player_head,1.0).

object(blue_player_tail,player_component,current).
color(blue_player_tail,blue).
bbox(blue_player_tail,20,32,2,2).
size(blue_player_tail,2,2).
area(blue_player_tail,2).
occupied_cells(blue_player_tail,[cell(20,32),cell(21,33)]).
shape(blue_player_tail,diagonal_pair).
component_of(blue_player_tail,blue_black_player).
confidence(blue_player_tail,1.0).

object(bottom_center_gate,compound_block,current).
colors(bottom_center_gate,[gray,dark_red]).
bbox(bottom_center_gate,29,45,5,5).
size(bottom_center_gate,5,5).
area(bottom_center_gate,25).
cell_runs(bottom_center_gate,[rows(45,49,29,33)]).
shape(bottom_center_gate,two_color_rectangle).
inside(bottom_center_gate,green_main_platform).
component_of(bottom_center_gate,green_maze_structure).
contains(bottom_center_gate,gray_gate_cap).
contains(bottom_center_gate,red_gate_base).
adjacent(bottom_center_gate,yellow_inner_cavity).
role(bottom_center_gate,embedded_gate).
confidence(bottom_center_gate,1.0).

object(gray_gate_cap,rectangle,current).
color(gray_gate_cap,gray).
bbox(gray_gate_cap,29,45,5,2).
size(gray_gate_cap,5,2).
area(gray_gate_cap,10).
cell_runs(gray_gate_cap,[rows(45,46,29,33)]).
shape(gray_gate_cap,solid_rectangle).
orientation(gray_gate_cap,horizontal).
component_of(gray_gate_cap,bottom_center_gate).
touches(gray_gate_cap,red_gate_base).
confidence(gray_gate_cap,1.0).

object(red_gate_base,rectangle,current).
color(red_gate_base,dark_red).
bbox(red_gate_base,29,47,5,3).
size(red_gate_base,5,3).
area(red_gate_base,15).
cell_runs(red_gate_base,[rows(47,49,29,33)]).
shape(red_gate_base,solid_rectangle).
orientation(red_gate_base,horizontal).
component_of(red_gate_base,bottom_center_gate).
touches(red_gate_base,gray_gate_cap).
confidence(red_gate_base,1.0).

object(lower_left_control_panel,panel,current).
colors(lower_left_control_panel,[gray,dark_red]).
bbox(lower_left_control_panel,1,53,10,10).
size(lower_left_control_panel,10,10).
area(lower_left_control_panel,100).
cell_runs(lower_left_control_panel,[rows(53,62,1,10)]).
shape(lower_left_control_panel,square_panel).
contains(lower_left_control_panel,lower_left_red_hook_glyph).
contains(lower_left_control_panel,lower_left_red_square).
role(lower_left_control_panel,control_panel).
confidence(lower_left_control_panel,1.0).

object(lower_left_red_hook_glyph,glyph,current).
color(lower_left_red_hook_glyph,dark_red).
bbox(lower_left_red_hook_glyph,3,55,6,6).
size(lower_left_red_hook_glyph,6,6).
area(lower_left_red_hook_glyph,20).
cell_runs(lower_left_red_hook_glyph,[rows(55,56,3,8),rows(57,60,3,4)]).
shape(lower_left_red_hook_glyph,thick_hook).
inside(lower_left_red_hook_glyph,lower_left_control_panel).
confidence(lower_left_red_hook_glyph,1.0).

object(lower_left_red_square,glyph_component,current).
color(lower_left_red_square,dark_red).
bbox(lower_left_red_square,7,59,2,2).
size(lower_left_red_square,2,2).
area(lower_left_red_square,4).
cell_runs(lower_left_red_square,[rows(59,60,7,8)]).
shape(lower_left_red_square,solid_square).
inside(lower_left_red_square,lower_left_control_panel).
aligned_with(lower_left_red_square,lower_left_red_hook_glyph,right_edge).
confidence(lower_left_red_square,1.0).

object(bottom_status_panel,interface_bar,current).
colors(bottom_status_panel,[gray,dark_gray,green,cyan]).
bbox(bottom_status_panel,12,60,52,4).
size(bottom_status_panel,52,4).
area(bottom_status_panel,208).
cell_runs(bottom_status_panel,[rows(60,63,12,63)]).
shape(bottom_status_panel,horizontal_status_panel).
orientation(bottom_status_panel,horizontal).
contains(bottom_status_panel,bottom_dark_status_bar).
contains(bottom_status_panel,bottom_green_status_bar).
contains(bottom_status_panel,left_cyan_status_cell).
contains(bottom_status_panel,middle_cyan_status_cell).
contains(bottom_status_panel,right_cyan_status_cell).
role(bottom_status_panel,status_display).
confidence(bottom_status_panel,1.0).

object(bottom_dark_status_bar,bar,current).
color(bottom_dark_status_bar,dark_gray).
bbox(bottom_dark_status_bar,14,61,41,2).
size(bottom_dark_status_bar,41,2).
area(bottom_dark_status_bar,82).
cell_runs(bottom_dark_status_bar,[rows(61,62,14,54)]).
shape(bottom_dark_status_bar,solid_rectangle).
orientation(bottom_dark_status_bar,horizontal).
component_of(bottom_dark_status_bar,bottom_status_panel).
adjacent(bottom_dark_status_bar,bottom_green_status_bar).
confidence(bottom_dark_status_bar,1.0).

object(bottom_green_status_bar,bar,current).
color(bottom_green_status_bar,green).
bbox(bottom_green_status_bar,13,61,1,2).
size(bottom_green_status_bar,1,2).
area(bottom_green_status_bar,2).
cell_runs(bottom_green_status_bar,[rows(61,62,13,13)]).
shape(bottom_green_status_bar,vertical_two_cell_segment).
orientation(bottom_green_status_bar,vertical).
component_of(bottom_green_status_bar,bottom_status_panel).
adjacent(bottom_green_status_bar,bottom_dark_status_bar).
role(bottom_green_status_bar,progress_indicator).
confidence(bottom_green_status_bar,1.0).

object(left_cyan_status_cell,indicator,current).
color(left_cyan_status_cell,cyan).
bbox(left_cyan_status_cell,56,61,2,2).
size(left_cyan_status_cell,2,2).
area(left_cyan_status_cell,4).
cell_runs(left_cyan_status_cell,[rows(61,62,56,57)]).
shape(left_cyan_status_cell,solid_square).
component_of(left_cyan_status_cell,bottom_status_panel).
confidence(left_cyan_status_cell,1.0).

object(middle_cyan_status_cell,indicator,current).
color(middle_cyan_status_cell,cyan).
bbox(middle_cyan_status_cell,59,61,2,2).
size(middle_cyan_status_cell,2,2).
area(middle_cyan_status_cell,4).
cell_runs(middle_cyan_status_cell,[rows(61,62,59,60)]).
shape(middle_cyan_status_cell,solid_square).
component_of(middle_cyan_status_cell,bottom_status_panel).
aligned_with(middle_cyan_status_cell,left_cyan_status_cell,horizontal_centerline).
confidence(middle_cyan_status_cell,1.0).

object(right_cyan_status_cell,indicator,current).
color(right_cyan_status_cell,cyan).
bbox(right_cyan_status_cell,62,61,2,2).
size(right_cyan_status_cell,2,2).
area(right_cyan_status_cell,4).
cell_runs(right_cyan_status_cell,[rows(61,62,62,63)]).
shape(right_cyan_status_cell,solid_square).
component_of(right_cyan_status_cell,bottom_status_panel).
aligned_with(right_cyan_status_cell,middle_cyan_status_cell,horizontal_centerline).
confidence(right_cyan_status_cell,1.0).

turtle_program(bottom_center_gate,[penup,setcolor(gray),pen_width(2),set_pos(29,45),pendown,fwd(4),penup,setcolor(dark_red),pen_width(3),set_pos(29,47),pendown,fwd(4),penup]).
turtle_program(bottom_green_status_bar,[penup,setcolor(green),pen_width(1),set_pos(13,61),rot(90),pendown,fwd(1),penup,rot(-90)]).
turtle_program(blue_black_player,[penup,setcolor(black),pen_width(1),set_pos(21,31),set_cell,set_pos(21,32),pendown,fwd(1),penup,setcolor(blue),set_pos(20,32),set_cell,set_pos(21,33),set_cell]).
````

[Open `objects.pl`](objects.pl)

</details>

<details>
<summary><code>redraw.pl</code></summary>

````prolog
canvas(640, 640).
origin(top_left).
units(pixel).

color(yellow,    '#FFDC00').
color(green,     '#2ECC40').
color(gray,      '#AAAAAA').
color(lightgray, '#B3B3B3').
color(darkgray,  '#666666').
color(burgundy,  '#880C29').
color(blue,      '#0074D9').
color(cyan,      '#7FDBFF').
color(black,     '#000000').

turtle(1,  fill_rect(0,   0,   640, 640, yellow)).
turtle(2,  fill_rect(0,   0,    40, 520, gray)).

turtle(3,  fill_rect(320, 80,    90,  90, green)).
turtle(4,  fill_rect(330, 90,    70,  70, gray)).
turtle(5,  fill_rect(350, 110,   30,  10, burgundy)).
turtle(6,  fill_rect(370, 110,   10,  30, burgundy)).
turtle(7,  fill_rect(350, 130,   10,  10, burgundy)).

turtle(8,  fill_rect(340, 160,   50,  90, green)).
turtle(9,  fill_rect(140, 250,  400,  50, green)).
turtle(10, fill_rect(140, 300,  150, 100, green)).
turtle(11, fill_rect(340, 300,  200, 200, green)).
turtle(12, fill_rect(190, 400,   50, 100, green)).

turtle(13, fill_rect(200, 320,   20,  10, blue)).
turtle(14, fill_rect(210, 330,   10,  10, blue)).
turtle(15, fill_rect(210, 310,   10,  20, black)).
turtle(16, fill_rect(220, 320,   10,  10, black)).

turtle(17, fill_rect(290, 450,   50,  20, lightgray)).
turtle(18, fill_rect(290, 470,   50,  30, burgundy)).

turtle(19, fill_rect(10,  530,  100, 100, gray)).
turtle(20, fill_rect(30,  550,   60,  20, burgundy)).
turtle(21, fill_rect(30,  570,   20,  40, burgundy)).
turtle(22, fill_rect(70,  590,   20,  20, burgundy)).

turtle(23, fill_rect(120, 600,  520,  40, lightgray)).
turtle(24, fill_rect(130, 610,   10,  20, green)).
turtle(25, fill_rect(140, 610,  410,  20, darkgray)).
turtle(26, fill_rect(560, 610,   20,  20, cyan)).
turtle(27, fill_rect(590, 610,   20,  20, cyan)).
turtle(28, fill_rect(620, 610,   20,  20, cyan)).
````

[Open `redraw.pl`](redraw.pl)

</details>

<details>
<summary><code>redraw_diff.pl</code></summary>

````prolog
patch([
    fill_rect(340, 450, 50, 50, green),
    fill_rect(290, 450, 50, 20, gray),
    fill_rect(290, 470, 50, 30, maroon),
    fill_rect(130, 610, 10, 20, green)
]).
````

[Open `redraw_diff.pl`](redraw_diff.pl)

</details>

<details>
<summary><code>rules.pl</code></summary>

````prolog
observed_rule(action3_gate_translation,translates(bottom_center_gate,delta(-5,0))).
observed_rule(action3_status_change,recolors([rows(61,62,13,13)],dark_gray,green)).
observed_rule(action3_gate_preservation,preserves(bottom_center_gate,[size(5,5),colors([gray,dark_red]),internal_partition])).

evidence(action3_gate_translation,parent_gate_bbox,bbox(34,45,5,5)).
evidence(action3_gate_translation,current_gate_bbox,bbox(29,45,5,5)).
evidence(action3_status_change,parent_status_cells,color(dark_gray,[cell(13,61),cell(13,62)])).
evidence(action3_status_change,current_status_cells,color(green,[cell(13,61),cell(13,62)])).
evidence(action3_gate_preservation,current_gate_geometry,[gray(rows(45,46,29,33)),dark_red(rows(47,49,29,33))]).

supported_by(action3_gate_translation,parent_gate_bbox).
supported_by(action3_gate_translation,current_gate_bbox).
supported_by(action3_status_change,parent_status_cells).
supported_by(action3_status_change,current_status_cells).
supported_by(action3_gate_preservation,current_gate_geometry).

hypothetical_rule(gate_targets_cavity_exit,assumes(action3_selects_leftward_gate_position),places(bottom_center_gate,directly_below(yellow_inner_cavity))).
hypothetical_rule(status_records_action3_progress,assumes(bottom_green_status_bar_is_progress),increments_green_status_by(one_column_two_cells)).
hypothetical_rule(gate_motion_uses_gate_width,assumes(discrete_gate_positions),moves_horizontally_by(one_gate_width)).

evidence(gate_targets_cavity_exit,cavity_bottom_run,rows(40,44,24,33)).
evidence(gate_targets_cavity_exit,current_gate_top_run,rows(45,46,29,33)).
evidence(status_records_action3_progress,new_green_segment,[rows(61,62,13,13)]).
evidence(gate_motion_uses_gate_width,translation_and_width,[delta_x(-5),gate_width(5)]).

supported_by(gate_targets_cavity_exit,cavity_bottom_run).
supported_by(gate_targets_cavity_exit,current_gate_top_run).
supported_by(status_records_action3_progress,new_green_segment).
supported_by(gate_motion_uses_gate_width,translation_and_width).

confidence(action3_gate_translation,1.0).
confidence(action3_status_change,1.0).
confidence(action3_gate_preservation,1.0).
confidence(gate_targets_cavity_exit,0.82).
confidence(status_records_action3_progress,0.72).
confidence(gate_motion_uses_gate_width,0.68).
````

[Open `rules.pl`](rules.pl)

</details>

<details>
<summary><code>similarities.pl</code></summary>

````prolog
object_correspondence(yellow_playfield,yellow_playfield,1.0,[color,bbox,cell_runs,area,role],[]).
object_correspondence(left_gray_border,left_gray_border,1.0,[color,bbox,size,area,shape],[]).
object_correspondence(green_maze_structure,green_maze_structure,0.945,[color,bbox,area,connectivity,contained_objects],[cell_runs]).
object_correspondence(green_upper_chamber_frame,green_upper_chamber_frame,1.0,[color,bbox,size,area,shape,symmetry],[]).
object_correspondence(gray_upper_chamber_interior,gray_upper_chamber_interior,1.0,[color,bbox,cell_runs,area,shape],[]).
object_correspondence(upper_red_hook_glyph,upper_red_hook_glyph,1.0,[color,bbox,occupied_geometry,shape],[]).
object_correspondence(upper_red_square,upper_red_square,1.0,[color,bbox,occupied_cells,shape],[]).
object_correspondence(green_chamber_stem,green_chamber_stem,1.0,[color,bbox,size,area,orientation],[]).
object_correspondence(green_main_platform,green_main_platform,0.941,[color,bbox,area,contained_objects],[cell_runs]).
object_correspondence(yellow_inner_cavity,yellow_inner_cavity,1.0,[color,bbox,size,area,cell_runs,shape],[]).
object_correspondence(blue_black_player,blue_black_player,1.0,[colors,bbox,size,occupied_cells,shape],[]).
object_correspondence(black_player_head,black_player_head,1.0,[color,bbox,occupied_cells,shape],[]).
object_correspondence(blue_player_tail,blue_player_tail,1.0,[color,bbox,occupied_cells,shape],[]).
object_correspondence(bottom_center_gate,bottom_center_gate,0.98,[colors,size,area,shape,subcomponents],[bbox,position]).
object_correspondence(gray_gate_cap,gray_gate_cap,0.98,[color,size,area,shape,orientation],[bbox,position]).
object_correspondence(red_gate_base,red_gate_base,0.98,[color,size,area,shape,orientation],[bbox,position]).
object_correspondence(lower_left_control_panel,lower_left_control_panel,1.0,[colors,bbox,size,area,shape,contained_objects],[]).
object_correspondence(lower_left_red_hook_glyph,lower_left_red_hook_glyph,1.0,[color,bbox,size,area,cell_runs,shape],[]).
object_correspondence(lower_left_red_square,lower_left_red_square,1.0,[color,bbox,size,area,cell_runs,shape],[]).
object_correspondence(bottom_status_panel,bottom_status_panel,0.99,[bbox,size,area,shape,orientation,cyan_indicators],[colors,internal_bar_partition]).
object_correspondence(bottom_dark_status_bar,bottom_dark_status_bar,0.976,[color,height,orientation,right_edge],[bbox,width,area,left_edge]).
object_correspondence(left_cyan_status_cell,left_cyan_status_cell,1.0,[color,bbox,size,area,shape],[]).
object_correspondence(middle_cyan_status_cell,middle_cyan_status_cell,1.0,[color,bbox,size,area,shape],[]).
object_correspondence(right_cyan_status_cell,right_cyan_status_cell,1.0,[color,bbox,size,area,shape],[]).

correspondence_evidence(bottom_center_gate,translation,delta(-5,0)).
correspondence_evidence(bottom_center_gate,parent_cells,[rows(45,49,34,38)]).
correspondence_evidence(bottom_center_gate,current_cells,[rows(45,49,29,33)]).
correspondence_evidence(green_main_platform,changed_green_cells,[removed(rows(45,49,29,33)),added(rows(45,49,34,38))]).
correspondence_evidence(bottom_dark_status_bar,current_is_parent_subset,[rows(61,62,14,54)]).
````

[Open `similarities.pl`](similarities.pl)

</details>

<details>
<summary><code>turtle_from_diff.pl</code></summary>

````prolog
turtle_program(parent_to_current_patch,[
penup,setcolor(green),pen_width(4),set_pos(34,45),pendown,fwd(4),penup,pen_width(1),set_pos(34,49),pendown,fwd(4),
penup,setcolor(gray),pen_width(2),set_pos(29,45),pendown,fwd(4),
penup,setcolor(dark_red),pen_width(3),set_pos(29,47),pendown,fwd(4),
penup,setcolor(green),pen_width(1),set_pos(13,61),rot(90),pendown,fwd(1),penup,rot(-90)
]).
````

[Open `turtle_from_diff.pl`](turtle_from_diff.pl)

</details>

<details>
<summary><code>turtle_from_image.pl</code></summary>

````prolog
turtle_program(current_grid,[
penup,setcolor(yellow),pen_width(4),set_pos(0,0),pendown,fwd(63),penup,set_pos(0,4),pendown,fwd(63),penup,set_pos(0,8),pendown,fwd(63),penup,set_pos(0,12),pendown,fwd(63),penup,set_pos(0,16),pendown,fwd(63),penup,set_pos(0,20),pendown,fwd(63),penup,set_pos(0,24),pendown,fwd(63),penup,set_pos(0,28),pendown,fwd(63),penup,set_pos(0,32),pendown,fwd(63),penup,set_pos(0,36),pendown,fwd(63),penup,set_pos(0,40),pendown,fwd(63),penup,set_pos(0,44),pendown,fwd(63),penup,set_pos(0,48),pendown,fwd(63),penup,set_pos(0,52),pendown,fwd(63),penup,set_pos(0,56),pendown,fwd(63),penup,set_pos(0,60),pendown,fwd(63),
penup,setcolor(gray),pen_width(4),set_pos(0,0),pendown,fwd(3),penup,set_pos(0,4),pendown,fwd(3),penup,set_pos(0,8),pendown,fwd(3),penup,set_pos(0,12),pendown,fwd(3),penup,set_pos(0,16),pendown,fwd(3),penup,set_pos(0,20),pendown,fwd(3),penup,set_pos(0,24),pendown,fwd(3),penup,set_pos(0,28),pendown,fwd(3),penup,set_pos(0,32),pendown,fwd(3),penup,set_pos(0,36),pendown,fwd(3),penup,set_pos(0,40),pendown,fwd(3),penup,set_pos(0,44),pendown,fwd(3),penup,set_pos(0,48),pendown,fwd(3),
penup,setcolor(green),pen_width(1),set_pos(32,8),pendown,fwd(8),penup,set_pos(32,9),rot(90),pendown,fwd(6),penup,rot(-90),set_pos(40,9),rot(90),pendown,fwd(6),penup,rot(-90),set_pos(32,16),pendown,fwd(8),
penup,pen_width(4),set_pos(34,17),pendown,fwd(4),penup,set_pos(34,21),pendown,fwd(4),
penup,pen_width(4),set_pos(14,25),pendown,fwd(39),penup,pen_width(1),set_pos(14,29),pendown,fwd(39),
penup,set_pos(14,30),pendown,fwd(14),penup,set_pos(34,30),pendown,fwd(19),
penup,set_pos(14,31),pendown,fwd(6),penup,set_pos(22,31),pendown,fwd(6),penup,set_pos(34,31),pendown,fwd(19),
penup,set_pos(14,32),pendown,fwd(5),penup,set_pos(23,32),pendown,fwd(5),penup,set_pos(34,32),pendown,fwd(19),
penup,set_pos(14,33),pendown,fwd(6),penup,set_pos(22,33),pendown,fwd(6),penup,set_pos(34,33),pendown,fwd(19),
penup,pen_width(4),set_pos(14,34),pendown,fwd(14),penup,set_pos(34,34),pendown,fwd(19),penup,pen_width(2),set_pos(14,38),pendown,fwd(14),penup,set_pos(34,38),pendown,fwd(19),
penup,pen_width(4),set_pos(19,40),pendown,fwd(4),penup,set_pos(34,40),pendown,fwd(19),penup,pen_width(1),set_pos(19,44),pendown,fwd(4),penup,set_pos(34,44),pendown,fwd(19),
penup,pen_width(4),set_pos(19,45),pendown,fwd(9),penup,set_pos(34,45),pendown,fwd(19),penup,pen_width(1),set_pos(19,49),pendown,fwd(9),penup,set_pos(34,49),pendown,fwd(19),
penup,setcolor(gray),pen_width(4),set_pos(33,9),pendown,fwd(6),penup,pen_width(3),set_pos(33,13),pendown,fwd(6),
penup,setcolor(dark_red),pen_width(1),set_pos(35,11),pendown,fwd(2),penup,set_pos(37,12),rot(90),pendown,fwd(1),penup,rot(-90),set_pos(35,13),set_cell,
penup,setcolor(black),pen_width(1),set_pos(21,31),set_cell,set_pos(21,32),pendown,fwd(1),penup,setcolor(blue),set_pos(20,32),set_cell,set_pos(21,33),set_cell,
penup,setcolor(gray),pen_width(2),set_pos(29,45),pendown,fwd(4),penup,setcolor(dark_red),pen_width(3),set_pos(29,47),pendown,fwd(4),
penup,setcolor(gray),pen_width(4),set_pos(1,53),pendown,fwd(9),penup,set_pos(1,57),pendown,fwd(9),penup,pen_width(2),set_pos(1,61),pendown,fwd(9),
penup,setcolor(dark_red),pen_width(2),set_pos(3,55),pendown,fwd(5),penup,set_pos(3,57),rot(90),pendown,fwd(3),penup,rot(-90),set_pos(7,59),pendown,fwd(1),
penup,setcolor(gray),pen_width(4),set_pos(12,60),pendown,fwd(51),
penup,setcolor(dark_gray),pen_width(2),set_pos(14,61),pendown,fwd(40),
penup,setcolor(green),pen_width(1),set_pos(13,61),rot(90),pendown,fwd(1),penup,rot(-90),
penup,setcolor(cyan),pen_width(2),set_pos(56,61),pendown,fwd(1),penup,set_pos(59,61),pendown,fwd(1),penup,set_pos(62,61),pendown,fwd(1),penup
]).
````

[Open `turtle_from_image.pl`](turtle_from_image.pl)

</details>

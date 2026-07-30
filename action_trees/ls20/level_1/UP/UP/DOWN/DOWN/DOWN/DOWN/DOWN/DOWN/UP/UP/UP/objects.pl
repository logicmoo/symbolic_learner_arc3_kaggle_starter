% Canonical identities are loaded from the level registry.
:- ensure_loaded('../../../../../../../../../../../object_registry.pl').

% State-specific facts for this action-tree node.
object(yellow_playfield,background,current).
color(yellow_playfield,yellow).
bbox(yellow_playfield,0,0,63,63).
area(yellow_playfield,2509).
shape(yellow_playfield,irregular_background_region).
role(yellow_playfield,background).
confidence(yellow_playfield,1.0).

object(left_gray_border,border,current).
color(left_gray_border,light_gray).
bbox(left_gray_border,0,0,3,51).
size(left_gray_border,4,52).
area(left_gray_border,208).
cell_runs(left_gray_border,[run(0,0,3),run(1,0,3),run(2,0,3),run(3,0,3),run(4,0,3),run(5,0,3),run(6,0,3),run(7,0,3),run(8,0,3),run(9,0,3),run(10,0,3),run(11,0,3),run(12,0,3),run(13,0,3),run(14,0,3),run(15,0,3),run(16,0,3),run(17,0,3),run(18,0,3),run(19,0,3),run(20,0,3),run(21,0,3),run(22,0,3),run(23,0,3),run(24,0,3),run(25,0,3),run(26,0,3),run(27,0,3),run(28,0,3),run(29,0,3),run(30,0,3),run(31,0,3),run(32,0,3),run(33,0,3),run(34,0,3),run(35,0,3),run(36,0,3),run(37,0,3),run(38,0,3),run(39,0,3),run(40,0,3),run(41,0,3),run(42,0,3),run(43,0,3),run(44,0,3),run(45,0,3),run(46,0,3),run(47,0,3),run(48,0,3),run(49,0,3),run(50,0,3),run(51,0,3)]).
shape(left_gray_border,vertical_rectangle).
orientation(left_gray_border,vertical).
role(left_gray_border,boundary).
confidence(left_gray_border,1.0).

object(green_maze_structure,compound_structure,current).
color(green_maze_structure,green).
bbox(green_maze_structure,14,8,53,49).
area(green_maze_structure,892).
shape(green_maze_structure,connected_stepped_structure).
contains(green_maze_structure,green_upper_chamber_frame).
contains(green_maze_structure,green_chamber_stem).
contains(green_maze_structure,green_main_platform).
contains(green_maze_structure,yellow_inner_cavity).
contains(green_maze_structure,bottom_center_gate).
confidence(green_maze_structure,1.0).

object(green_upper_chamber_frame,enclosure,current).
color(green_upper_chamber_frame,green).
bbox(green_upper_chamber_frame,32,8,40,16).
size(green_upper_chamber_frame,9,9).
area(green_upper_chamber_frame,32).
cell_runs(green_upper_chamber_frame,[run(8,32,40),run(9,32,32),run(9,40,40),run(10,32,32),run(10,40,40),run(11,32,32),run(11,40,40),run(12,32,32),run(12,40,40),run(13,32,32),run(13,40,40),run(14,32,32),run(14,40,40),run(15,32,32),run(15,40,40),run(16,32,40)]).
shape(green_upper_chamber_frame,rectangular_frame).
component_of(green_upper_chamber_frame,green_maze_structure).
contains(green_upper_chamber_frame,gray_upper_chamber_interior).
confidence(green_upper_chamber_frame,1.0).

object(gray_upper_chamber_interior,chamber,current).
color(gray_upper_chamber_interior,light_gray).
bbox(gray_upper_chamber_interior,33,9,39,15).
size(gray_upper_chamber_interior,7,7).
area(gray_upper_chamber_interior,43).
cell_runs(gray_upper_chamber_interior,[run(9,33,39),run(10,33,39),run(11,33,34),run(11,38,39),run(12,33,36),run(12,38,39),run(13,33,34),run(13,36,36),run(13,38,39),run(14,33,39),run(15,33,39)]).
shape(gray_upper_chamber_interior,rectangular_chamber_with_glyph).
inside(gray_upper_chamber_interior,green_upper_chamber_frame).
contains(gray_upper_chamber_interior,upper_red_hook_glyph).
contains(gray_upper_chamber_interior,upper_red_square).
confidence(gray_upper_chamber_interior,1.0).

object(upper_red_hook_glyph,glyph,current).
color(upper_red_hook_glyph,dark_red).
bbox(upper_red_hook_glyph,35,11,37,13).
area(upper_red_hook_glyph,5).
occupied_cells(upper_red_hook_glyph,[cell(35,11),cell(36,11),cell(37,11),cell(37,12),cell(37,13)]).
shape(upper_red_hook_glyph,hook).
inside(upper_red_hook_glyph,gray_upper_chamber_interior).
confidence(upper_red_hook_glyph,1.0).

object(upper_red_square,glyph_component,current).
color(upper_red_square,dark_red).
bbox(upper_red_square,35,13,35,13).
size(upper_red_square,1,1).
area(upper_red_square,1).
occupied_cells(upper_red_square,[cell(35,13)]).
shape(upper_red_square,square).
inside(upper_red_square,gray_upper_chamber_interior).
confidence(upper_red_square,1.0).

object(green_chamber_stem,vertical_bar,current).
color(green_chamber_stem,green).
bbox(green_chamber_stem,34,17,38,24).
size(green_chamber_stem,5,8).
area(green_chamber_stem,40).
cell_runs(green_chamber_stem,[run(17,34,38),run(18,34,38),run(19,34,38),run(20,34,38),run(21,34,38),run(22,34,38),run(23,34,38),run(24,34,38)]).
shape(green_chamber_stem,vertical_rectangle).
orientation(green_chamber_stem,vertical).
component_of(green_chamber_stem,green_maze_structure).
touches(green_chamber_stem,green_upper_chamber_frame).
touches(green_chamber_stem,green_main_platform).
confidence(green_chamber_stem,1.0).

object(green_main_platform,platform,current).
color(green_main_platform,green).
bbox(green_main_platform,14,25,53,49).
area(green_main_platform,820).
cell_runs(green_main_platform,[run(25,14,53),run(26,14,53),run(27,14,53),run(28,14,53),run(29,14,53),run(30,14,28),run(30,39,53),run(31,14,20),run(31,22,28),run(31,39,53),run(32,14,19),run(32,23,28),run(32,39,53),run(33,14,20),run(33,22,28),run(33,39,53),run(34,14,28),run(34,39,53),run(35,14,28),run(35,34,53),run(36,14,28),run(36,34,53),run(37,14,28),run(37,34,53),run(38,14,28),run(38,34,53),run(39,14,28),run(39,34,53),run(40,19,23),run(40,34,53),run(41,19,23),run(41,34,53),run(42,19,23),run(42,34,53),run(43,19,23),run(43,34,53),run(44,19,23),run(44,34,53),run(45,19,53),run(46,19,53),run(47,19,53),run(48,19,53),run(49,19,53)]).
shape(green_main_platform,stepped_platform_with_cavity).
component_of(green_main_platform,green_maze_structure).
contains(green_main_platform,yellow_inner_cavity).
contains(green_main_platform,bottom_center_gate).
confidence(green_main_platform,1.0).

object(yellow_inner_cavity,hole,current).
color(yellow_inner_cavity,yellow).
bbox(yellow_inner_cavity,24,30,33,44).
area(yellow_inner_cavity,100).
cell_runs(yellow_inner_cavity,[run(30,29,33),run(31,29,33),run(32,29,33),run(33,29,33),run(34,29,33),run(35,29,33),run(36,29,33),run(37,29,33),run(38,29,33),run(39,29,33),run(40,24,33),run(41,24,33),run(42,24,33),run(43,24,33),run(44,24,33)]).
shape(yellow_inner_cavity,stepped_enclosed_cavity).
inside(yellow_inner_cavity,green_maze_structure).
adjacent(yellow_inner_cavity,bottom_center_gate).
confidence(yellow_inner_cavity,1.0).

object(blue_black_player,player,current).
colors(blue_black_player,[blue,black]).
bbox(blue_black_player,20,31,22,33).
area(blue_black_player,5).
occupied_cells(blue_black_player,[cell(21,31),cell(20,32),cell(21,32),cell(22,32),cell(21,33)]).
shape(blue_black_player,small_asymmetric_marker).
contains(blue_black_player,black_player_head).
contains(blue_black_player,blue_player_tail).
inside(blue_black_player,green_main_platform).
role(blue_black_player,player_marker).
confidence(blue_black_player,1.0).

object(black_player_head,player_component,current).
color(black_player_head,black).
bbox(black_player_head,21,31,22,32).
area(black_player_head,3).
occupied_cells(black_player_head,[cell(21,31),cell(21,32),cell(22,32)]).
shape(black_player_head,corner_triomino).
component_of(black_player_head,blue_black_player).
confidence(black_player_head,1.0).

object(blue_player_tail,player_component,current).
color(blue_player_tail,blue).
bbox(blue_player_tail,20,32,21,33).
area(blue_player_tail,2).
occupied_cells(blue_player_tail,[cell(20,32),cell(21,33)]).
shape(blue_player_tail,diagonal_pair).
component_of(blue_player_tail,blue_black_player).
confidence(blue_player_tail,1.0).

object(bottom_center_gate,compound_block,current).
colors(bottom_center_gate,[light_gray,dark_red]).
bbox(bottom_center_gate,34,30,38,34).
size(bottom_center_gate,5,5).
area(bottom_center_gate,25).
shape(bottom_center_gate,two_color_rectangle).
component_of(bottom_center_gate,green_maze_structure).
contains(bottom_center_gate,gray_gate_cap).
contains(bottom_center_gate,red_gate_base).
adjacent(bottom_center_gate,yellow_inner_cavity).
confidence(bottom_center_gate,1.0).

object(gray_gate_cap,rectangle,current).
color(gray_gate_cap,light_gray).
bbox(gray_gate_cap,34,30,38,31).
size(gray_gate_cap,5,2).
area(gray_gate_cap,10).
cell_runs(gray_gate_cap,[run(30,34,38),run(31,34,38)]).
shape(gray_gate_cap,solid_rectangle).
orientation(gray_gate_cap,horizontal).
component_of(gray_gate_cap,bottom_center_gate).
confidence(gray_gate_cap,1.0).

object(red_gate_base,rectangle,current).
color(red_gate_base,dark_red).
bbox(red_gate_base,34,32,38,34).
size(red_gate_base,5,3).
area(red_gate_base,15).
cell_runs(red_gate_base,[run(32,34,38),run(33,34,38),run(34,34,38)]).
shape(red_gate_base,solid_rectangle).
orientation(red_gate_base,horizontal).
component_of(red_gate_base,bottom_center_gate).
confidence(red_gate_base,1.0).

object(lower_left_control_panel,panel,current).
colors(lower_left_control_panel,[light_gray,dark_red]).
bbox(lower_left_control_panel,1,53,10,62).
size(lower_left_control_panel,10,10).
area(lower_left_control_panel,100).
shape(lower_left_control_panel,square_control_panel).
contains(lower_left_control_panel,lower_left_red_hook_glyph).
contains(lower_left_control_panel,lower_left_red_square).
confidence(lower_left_control_panel,1.0).

object(lower_left_red_hook_glyph,glyph,current).
color(lower_left_red_hook_glyph,dark_red).
bbox(lower_left_red_hook_glyph,3,55,8,60).
area(lower_left_red_hook_glyph,20).
cell_runs(lower_left_red_hook_glyph,[run(55,3,8),run(56,3,8),run(57,3,4),run(58,3,4),run(59,3,4),run(60,3,4)]).
shape(lower_left_red_hook_glyph,thick_hook).
inside(lower_left_red_hook_glyph,lower_left_control_panel).
confidence(lower_left_red_hook_glyph,1.0).

object(lower_left_red_square,glyph_component,current).
color(lower_left_red_square,dark_red).
bbox(lower_left_red_square,7,59,8,60).
size(lower_left_red_square,2,2).
area(lower_left_red_square,4).
cell_runs(lower_left_red_square,[run(59,7,8),run(60,7,8)]).
shape(lower_left_red_square,square).
inside(lower_left_red_square,lower_left_control_panel).
confidence(lower_left_red_square,1.0).

object(bottom_status_panel,interface_bar,current).
colors(bottom_status_panel,[light_gray,green,dark_gray,cyan]).
bbox(bottom_status_panel,12,60,63,63).
size(bottom_status_panel,52,4).
area(bottom_status_panel,208).
shape(bottom_status_panel,compound_horizontal_status_panel).
orientation(bottom_status_panel,horizontal).
contains(bottom_status_panel,bottom_green_status_bar).
contains(bottom_status_panel,bottom_dark_status_bar).
contains(bottom_status_panel,left_cyan_status_cell).
contains(bottom_status_panel,middle_cyan_status_cell).
contains(bottom_status_panel,right_cyan_status_cell).
role(bottom_status_panel,status_display).
confidence(bottom_status_panel,1.0).

object(bottom_green_status_bar,bar,current).
color(bottom_green_status_bar,green).
bbox(bottom_green_status_bar,13,61,23,62).
size(bottom_green_status_bar,11,2).
area(bottom_green_status_bar,22).
cell_runs(bottom_green_status_bar,[run(61,13,23),run(62,13,23)]).
shape(bottom_green_status_bar,solid_horizontal_bar).
orientation(bottom_green_status_bar,horizontal).
component_of(bottom_green_status_bar,bottom_status_panel).
role(bottom_green_status_bar,filled_status_segment).
confidence(bottom_green_status_bar,1.0).

object(bottom_dark_status_bar,bar,current).
color(bottom_dark_status_bar,dark_gray).
bbox(bottom_dark_status_bar,24,61,54,62).
size(bottom_dark_status_bar,31,2).
area(bottom_dark_status_bar,62).
cell_runs(bottom_dark_status_bar,[run(61,24,54),run(62,24,54)]).
shape(bottom_dark_status_bar,solid_horizontal_bar).
orientation(bottom_dark_status_bar,horizontal).
component_of(bottom_dark_status_bar,bottom_status_panel).
role(bottom_dark_status_bar,unfilled_status_segment).
adjacent(bottom_dark_status_bar,bottom_green_status_bar).
confidence(bottom_dark_status_bar,1.0).

object(left_cyan_status_cell,indicator,current).
color(left_cyan_status_cell,cyan).
bbox(left_cyan_status_cell,56,61,57,62).
size(left_cyan_status_cell,2,2).
area(left_cyan_status_cell,4).
cell_runs(left_cyan_status_cell,[run(61,56,57),run(62,56,57)]).
shape(left_cyan_status_cell,square).
component_of(left_cyan_status_cell,bottom_status_panel).
role(left_cyan_status_cell,status_indicator).
confidence(left_cyan_status_cell,1.0).

object(middle_cyan_status_cell,indicator,current).
color(middle_cyan_status_cell,cyan).
bbox(middle_cyan_status_cell,59,61,60,62).
size(middle_cyan_status_cell,2,2).
area(middle_cyan_status_cell,4).
cell_runs(middle_cyan_status_cell,[run(61,59,60),run(62,59,60)]).
shape(middle_cyan_status_cell,square).
component_of(middle_cyan_status_cell,bottom_status_panel).
role(middle_cyan_status_cell,status_indicator).
confidence(middle_cyan_status_cell,1.0).

object(right_cyan_status_cell,indicator,current).
color(right_cyan_status_cell,cyan).
bbox(right_cyan_status_cell,62,61,63,62).
size(right_cyan_status_cell,2,2).
area(right_cyan_status_cell,4).
cell_runs(right_cyan_status_cell,[run(61,62,63),run(62,62,63)]).
shape(right_cyan_status_cell,square).
component_of(right_cyan_status_cell,bottom_status_panel).
role(right_cyan_status_cell,status_indicator).
confidence(right_cyan_status_cell,1.0).

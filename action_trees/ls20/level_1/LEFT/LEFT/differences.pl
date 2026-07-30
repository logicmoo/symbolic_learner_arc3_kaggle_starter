transition(action3,parent,current).
changed_cell_count(52).

moved(bottom_center_gate,from_bbox(29,45,5,5),to_bbox(24,45,5,5),delta(-5,0)).
moved(gray_gate_cap,from_bbox(29,45,5,2),to_bbox(24,45,5,2),delta(-5,0)).
moved(red_gate_base,from_bbox(29,47,5,3),to_bbox(24,47,5,3),delta(-5,0)).

recolored_cells(green,gray,[rows(45,46,24,28)]).
recolored_cells(green,dark_red,[rows(47,49,24,28)]).
recolored_cells(gray,green,[rows(45,46,29,33)]).
recolored_cells(dark_red,green,[rows(47,49,29,33)]).
recolored_cells(dark_gray,green,[rows(61,62,14,14)]).

overwritten(bottom_center_gate,green_main_platform,[rows(45,49,24,28)]).
restored(green_main_platform,[rows(45,49,29,33)],green).
reshaped(green_main_platform,removed_cells([rows(45,49,24,28)]),added_cells([rows(45,49,29,33)]),area_unchanged(820)).
reshaped(green_maze_structure,removed_cells([rows(45,49,24,28)]),added_cells([rows(45,49,29,33)]),area_unchanged(892)).

resized(bottom_green_status_bar,from_bbox(13,61,1,2),to_bbox(13,61,2,2),area_change(2,4)).
resized(bottom_dark_status_bar,from_bbox(14,61,41,2),to_bbox(15,61,40,2),area_change(82,80)).
status_change(bottom_status_panel,green_progress_added([rows(61,62,14,14)]),dark_gray_removed([rows(61,62,14,14)])).

unchanged(blue_black_player,bbox(20,31,3,3),occupied_cells([cell(21,31),cell(20,32),cell(21,32),cell(22,32),cell(21,33)])).
unchanged(yellow_inner_cavity,bbox(24,30,10,15),cell_runs([rows(30,39,29,33),rows(40,44,24,33)])).
unchanged(green_upper_chamber_frame,bbox(32,8,9,9),area(32)).
unchanged(lower_left_control_panel,bbox(1,53,10,10),area(100)).
unchanged(left_cyan_status_cell,bbox(56,61,2,2),area(4)).
unchanged(middle_cyan_status_cell,bbox(59,61,2,2),area(4)).
unchanged(right_cyan_status_cell,bbox(62,61,2,2),area(4)).

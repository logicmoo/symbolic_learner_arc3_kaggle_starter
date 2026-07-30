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

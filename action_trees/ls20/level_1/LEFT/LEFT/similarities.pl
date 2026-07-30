correspondence(yellow_playfield,parent,current,1.0).
matched_properties(yellow_playfield,[color(yellow),bbox(0,0,64,64),area(2509),cell_runs_unchanged]).
correspondence_evidence(yellow_playfield,[same_background_extent,same_exact_visible_cells]).

correspondence(left_gray_border,parent,current,1.0).
matched_properties(left_gray_border,[color(gray),bbox(0,0,4,52),area(208),shape(solid_rectangle)]).
correspondence_evidence(left_gray_border,[same_exact_cell_run(rows(0,51,0,3))]).

correspondence(green_maze_structure,parent,current,0.97).
matched_properties(green_maze_structure,[color(green),bbox(14,8,40,42),area(892),connectivity(single_component)]).
changed_properties(green_maze_structure,[cells_removed(rows(45,49,24,28)),cells_added(rows(45,49,29,33))]).
correspondence_evidence(green_maze_structure,[same_upper_frame,same_stem,same_platform_extent,localized_gate_position_change]).

correspondence(green_upper_chamber_frame,parent,current,1.0).
matched_properties(green_upper_chamber_frame,[color(green),bbox(32,8,9,9),area(32),shape(rectangular_frame)]).
correspondence_evidence(green_upper_chamber_frame,[same_exact_cell_runs]).

correspondence(gray_upper_chamber_interior,parent,current,1.0).
matched_properties(gray_upper_chamber_interior,[color(gray),bbox(33,9,7,7),area(43),same_glyph_occlusions]).
correspondence_evidence(gray_upper_chamber_interior,[same_exact_cell_runs]).

correspondence(upper_red_hook_glyph,parent,current,1.0).
matched_properties(upper_red_hook_glyph,[color(dark_red),bbox(35,11,3,3),area(5),shape(hook)]).
correspondence_evidence(upper_red_hook_glyph,[same_exact_cell_runs]).

correspondence(upper_red_square,parent,current,1.0).
matched_properties(upper_red_square,[color(dark_red),bbox(35,13,1,1),area(1)]).
correspondence_evidence(upper_red_square,[same_cell(cell(35,13))]).

correspondence(green_chamber_stem,parent,current,1.0).
matched_properties(green_chamber_stem,[color(green),bbox(34,17,5,8),area(40),shape(solid_rectangle)]).
correspondence_evidence(green_chamber_stem,[same_exact_cell_run(rows(17,24,34,38))]).

correspondence(green_main_platform,parent,current,0.96).
matched_properties(green_main_platform,[color(green),bbox(14,25,40,25),area(820),same_connectivity]).
changed_properties(green_main_platform,[cells_removed(rows(45,49,24,28)),cells_added(rows(45,49,29,33))]).
correspondence_evidence(green_main_platform,[all_rows_25_through_44_match,only_gate_band_changed]).

correspondence(yellow_inner_cavity,parent,current,1.0).
matched_properties(yellow_inner_cavity,[color(yellow),bbox(24,30,10,15),area(100),shape(stepped_cavity)]).
correspondence_evidence(yellow_inner_cavity,[same_exact_cell_runs]).

correspondence(blue_black_player,parent,current,1.0).
matched_properties(blue_black_player,[colors([black,blue]),bbox(20,31,3,3),area(5),shape(asymmetric_cross_marker)]).
correspondence_evidence(blue_black_player,[same_five_occupied_cells]).

correspondence(black_player_head,parent,current,1.0).
matched_properties(black_player_head,[color(black),bbox(21,31,2,2),area(3),shape(right_facing_corner)]).
correspondence_evidence(black_player_head,[same_cells([cell(21,31),cell(21,32),cell(22,32)])]).

correspondence(blue_player_tail,parent,current,1.0).
matched_properties(blue_player_tail,[color(blue),bbox(20,32,2,2),area(2),shape(diagonal_pair)]).
correspondence_evidence(blue_player_tail,[same_cells([cell(20,32),cell(21,33)])]).

correspondence(bottom_center_gate,parent,current,1.0).
matched_properties(bottom_center_gate,[colors([gray,dark_red]),size(5,5),area(25),shape(two_color_rectangle),same_internal_partition]).
changed_properties(bottom_center_gate,[bbox(from(29,45,5,5),to(24,45,5,5)),position(delta(-5,0))]).
correspondence_evidence(bottom_center_gate,[exact_translation_of_all_25_cells(-5,0)]).

correspondence(gray_gate_cap,parent,current,1.0).
matched_properties(gray_gate_cap,[color(gray),size(5,2),area(10),shape(solid_rectangle)]).
changed_properties(gray_gate_cap,[bbox(from(29,45,5,2),to(24,45,5,2)),position(delta(-5,0))]).
correspondence_evidence(gray_gate_cap,[exact_translation_of_all_10_cells(-5,0)]).

correspondence(red_gate_base,parent,current,1.0).
matched_properties(red_gate_base,[color(dark_red),size(5,3),area(15),shape(solid_rectangle)]).
changed_properties(red_gate_base,[bbox(from(29,47,5,3),to(24,47,5,3)),position(delta(-5,0))]).
correspondence_evidence(red_gate_base,[exact_translation_of_all_15_cells(-5,0)]).

correspondence(lower_left_control_panel,parent,current,1.0).
matched_properties(lower_left_control_panel,[colors([gray,dark_red]),bbox(1,53,10,10),area(100),shape(square_panel)]).
correspondence_evidence(lower_left_control_panel,[same_exact_visible_cells]).

correspondence(lower_left_red_hook_glyph,parent,current,1.0).
matched_properties(lower_left_red_hook_glyph,[color(dark_red),bbox(3,55,6,6),area(20),shape(thick_hook)]).
correspondence_evidence(lower_left_red_hook_glyph,[same_exact_cell_runs]).

correspondence(lower_left_red_square,parent,current,1.0).
matched_properties(lower_left_red_square,[color(dark_red),bbox(7,59,2,2),area(4),shape(solid_square)]).
correspondence_evidence(lower_left_red_square,[same_exact_cell_run(rows(59,60,7,8))]).

correspondence(bottom_status_panel,parent,current,0.99).
matched_properties(bottom_status_panel,[bbox(12,60,52,4),area(208),shape(horizontal_status_panel),same_cyan_indicators]).
changed_properties(bottom_status_panel,[cell_recolored(rows(61,62,14,14),dark_gray,green)]).
correspondence_evidence(bottom_status_panel,[same_outer_extent,localized_internal_progress_change]).

correspondence(bottom_dark_status_bar,parent,current,0.98).
matched_properties(bottom_dark_status_bar,[color(dark_gray),right_edge(54),height(2),shape(solid_rectangle)]).
changed_properties(bottom_dark_status_bar,[bbox(from(14,61,41,2),to(15,61,40,2)),area(from(82),to(80))]).
correspondence_evidence(bottom_dark_status_bar,[remaining_cells_exactly_rows(61,62,15,54)]).

correspondence(bottom_green_status_bar,parent,current,0.95).
matched_properties(bottom_green_status_bar,[color(green),left_edge(13),height(2),role(progress_indicator)]).
changed_properties(bottom_green_status_bar,[bbox(from(13,61,1,2),to(13,61,2,2)),area(from(2),to(4))]).
correspondence_evidence(bottom_green_status_bar,[old_cells_preserved,new_cells(rows(61,62,14,14))]).

correspondence(left_cyan_status_cell,parent,current,1.0).
matched_properties(left_cyan_status_cell,[color(cyan),bbox(56,61,2,2),area(4)]).
correspondence_evidence(left_cyan_status_cell,[same_exact_cell_run(rows(61,62,56,57))]).

correspondence(middle_cyan_status_cell,parent,current,1.0).
matched_properties(middle_cyan_status_cell,[color(cyan),bbox(59,61,2,2),area(4)]).
correspondence_evidence(middle_cyan_status_cell,[same_exact_cell_run(rows(61,62,59,60))]).

correspondence(right_cyan_status_cell,parent,current,1.0).
matched_properties(right_cyan_status_cell,[color(cyan),bbox(62,61,2,2),area(4)]).
correspondence_evidence(right_cyan_status_cell,[same_exact_cell_run(rows(61,62,62,63))]).

correspondence(yellow_playfield,yellow_playfield,1.0).
matched_properties(yellow_playfield,yellow_playfield,[color,background_role,outer_connectivity]).
changed_properties(yellow_playfield,yellow_playfield,[]).

correspondence(left_gray_border,left_gray_border,1.0).
matched_properties(left_gray_border,left_gray_border,[color,bbox,size,area,shape]).
changed_properties(left_gray_border,left_gray_border,[]).

correspondence(green_maze_structure,green_maze_structure,0.99).
matched_properties(green_maze_structure,green_maze_structure,[color,bbox,connectivity,components]).
changed_properties(green_maze_structure,green_maze_structure,[gate_occupied_cells]).

correspondence(green_upper_chamber_frame,green_upper_chamber_frame,1.0).
matched_properties(green_upper_chamber_frame,green_upper_chamber_frame,[color,bbox,area,cell_runs]).
changed_properties(green_upper_chamber_frame,green_upper_chamber_frame,[]).

correspondence(gray_upper_chamber_interior,gray_upper_chamber_interior,1.0).
matched_properties(gray_upper_chamber_interior,gray_upper_chamber_interior,[color,bbox,area,cell_runs]).
changed_properties(gray_upper_chamber_interior,gray_upper_chamber_interior,[]).

correspondence(upper_red_hook_glyph,upper_red_hook_glyph,1.0).
matched_properties(upper_red_hook_glyph,upper_red_hook_glyph,[color,bbox,occupied_cells,shape]).
changed_properties(upper_red_hook_glyph,upper_red_hook_glyph,[]).

correspondence(upper_red_square,upper_red_square,1.0).
matched_properties(upper_red_square,upper_red_square,[color,bbox,occupied_cells]).
changed_properties(upper_red_square,upper_red_square,[]).

correspondence(green_chamber_stem,green_chamber_stem,1.0).
matched_properties(green_chamber_stem,green_chamber_stem,[color,bbox,size,area]).
changed_properties(green_chamber_stem,green_chamber_stem,[]).

correspondence(green_main_platform,green_main_platform,0.97).
matched_properties(green_main_platform,green_main_platform,[color,bbox,area,stepped_outline,cavity]).
changed_properties(green_main_platform,green_main_platform,[occupied_cells_at_gate_source_and_destination]).
correspondence_evidence(green_main_platform,green_main_platform,[same_area(820),restored_rows(35,39,34,38),overwritten_rows(30,34,34,38)]).

correspondence(yellow_inner_cavity,yellow_inner_cavity,1.0).
matched_properties(yellow_inner_cavity,yellow_inner_cavity,[color,bbox,area,cell_runs,enclosure]).
changed_properties(yellow_inner_cavity,yellow_inner_cavity,[]).

correspondence(blue_black_player,blue_black_player,1.0).
matched_properties(blue_black_player,blue_black_player,[colors,bbox,occupied_cells,shape]).
changed_properties(blue_black_player,blue_black_player,[]).

correspondence(black_player_head,black_player_head,1.0).
matched_properties(black_player_head,black_player_head,[color,bbox,occupied_cells]).
changed_properties(black_player_head,black_player_head,[]).

correspondence(blue_player_tail,blue_player_tail,1.0).
matched_properties(blue_player_tail,blue_player_tail,[color,bbox,occupied_cells]).
changed_properties(blue_player_tail,blue_player_tail,[]).

correspondence(bottom_center_gate,bottom_center_gate,1.0).
matched_properties(bottom_center_gate,bottom_center_gate,[colors,size,area,shape,internal_layout]).
changed_properties(bottom_center_gate,bottom_center_gate,[bbox,position]).
correspondence_evidence(bottom_center_gate,bottom_center_gate,[translation(0,-5),same_size(5,5),same_cap_size(5,2),same_base_size(5,3)]).

correspondence(gray_gate_cap,gray_gate_cap,1.0).
matched_properties(gray_gate_cap,gray_gate_cap,[color,size,area,shape]).
changed_properties(gray_gate_cap,gray_gate_cap,[bbox,position]).

correspondence(red_gate_base,red_gate_base,1.0).
matched_properties(red_gate_base,red_gate_base,[color,size,area,shape]).
changed_properties(red_gate_base,red_gate_base,[bbox,position]).

correspondence(lower_left_control_panel,lower_left_control_panel,1.0).
matched_properties(lower_left_control_panel,lower_left_control_panel,[colors,bbox,size,glyph_layout]).
changed_properties(lower_left_control_panel,lower_left_control_panel,[]).

correspondence(lower_left_red_hook_glyph,lower_left_red_hook_glyph,1.0).
matched_properties(lower_left_red_hook_glyph,lower_left_red_hook_glyph,[color,bbox,cell_runs,shape]).
changed_properties(lower_left_red_hook_glyph,lower_left_red_hook_glyph,[]).

correspondence(lower_left_red_square,lower_left_red_square,1.0).
matched_properties(lower_left_red_square,lower_left_red_square,[color,bbox,size,cell_runs]).
changed_properties(lower_left_red_square,lower_left_red_square,[]).

correspondence(bottom_status_panel,bottom_status_panel,0.99).
matched_properties(bottom_status_panel,bottom_status_panel,[bbox,size,outer_frame,cyan_indicators]).
changed_properties(bottom_status_panel,bottom_status_panel,[green_dark_partition]).

correspondence(bottom_green_status_bar,bottom_green_status_bar,0.98).
matched_properties(bottom_green_status_bar,bottom_green_status_bar,[color,height,orientation,left_edge]).
changed_properties(bottom_green_status_bar,bottom_green_status_bar,[width,right_edge,area]).
correspondence_evidence(bottom_green_status_bar,bottom_green_status_bar,[width_change(10,11),added_cells([cell(23,61),cell(23,62)])]).

correspondence(bottom_dark_status_bar,bottom_dark_status_bar,0.98).
matched_properties(bottom_dark_status_bar,bottom_dark_status_bar,[color,height,orientation,right_edge]).
changed_properties(bottom_dark_status_bar,bottom_dark_status_bar,[width,left_edge,area]).
correspondence_evidence(bottom_dark_status_bar,bottom_dark_status_bar,[width_change(32,31),removed_cells([cell(23,61),cell(23,62)])]).

correspondence(left_cyan_status_cell,left_cyan_status_cell,1.0).
matched_properties(left_cyan_status_cell,left_cyan_status_cell,[color,bbox,size,area]).
changed_properties(left_cyan_status_cell,left_cyan_status_cell,[]).

correspondence(middle_cyan_status_cell,middle_cyan_status_cell,1.0).
matched_properties(middle_cyan_status_cell,middle_cyan_status_cell,[color,bbox,size,area]).
changed_properties(middle_cyan_status_cell,middle_cyan_status_cell,[]).

correspondence(right_cyan_status_cell,right_cyan_status_cell,1.0).
matched_properties(right_cyan_status_cell,right_cyan_status_cell,[color,bbox,size,area]).
changed_properties(right_cyan_status_cell,right_cyan_status_cell,[]).

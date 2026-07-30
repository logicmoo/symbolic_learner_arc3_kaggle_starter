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

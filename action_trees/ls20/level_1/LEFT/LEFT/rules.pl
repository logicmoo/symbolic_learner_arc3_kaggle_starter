hypothetical_rule(action3_gate_step_left,action(action3),effect(translate(bottom_center_gate,-5,0))).
evidence(action3_gate_step_left_evidence,parent_to_current,[gate_bbox_from(29,45,5,5),gate_bbox_to(24,45,5,5),exact_component_translation(delta(-5,0))]).
supported_by(action3_gate_step_left,action3_gate_step_left_evidence).
confidence(action3_gate_step_left,0.9).

hypothetical_rule(action3_progress_increment,action(action3),effect(expand_right(bottom_green_status_bar,1))).
evidence(action3_progress_increment_evidence,parent_to_current,[green_status_bbox_from(13,61,1,2),green_status_bbox_to(13,61,2,2),recolored_cells(dark_gray,green,[rows(61,62,14,14)])]).
supported_by(action3_progress_increment,action3_progress_increment_evidence).
confidence(action3_progress_increment,0.85).

hypothetical_rule(gate_step_updates_progress,assumption(bottom_green_status_bar_tracks_successful_gate_steps),effect(one_green_status_column_per_gate_step)).
evidence(gate_step_updates_progress_evidence,parent_to_current,[gate_translation(delta(-5,0)),gate_width(5),green_status_width_change(1,2),simultaneous_under_action(action3)]).
supported_by(gate_step_updates_progress,gate_step_updates_progress_evidence).
confidence(gate_step_updates_progress,0.6).

observed_rule(action2_no_change_in_observed_transition,holds_for_transition(parent,current,action2,no_changed_cells)).
evidence(action2_no_change_in_observed_transition,evidence_full_grid_identity,cellwise_comparison(bbox(0,0,64,64),matched_cells(4096),changed_cells(0))).
evidence(action2_no_change_in_observed_transition,evidence_player_identity,player_cells([cell(21,31,black),cell(20,32,blue),cell(21,32,black),cell(22,32,black),cell(21,33,blue)])).
supported_by(action2_no_change_in_observed_transition,evidence_full_grid_identity).
supported_by(action2_no_change_in_observed_transition,evidence_player_identity).
confidence(action2_no_change_in_observed_transition,1.0).

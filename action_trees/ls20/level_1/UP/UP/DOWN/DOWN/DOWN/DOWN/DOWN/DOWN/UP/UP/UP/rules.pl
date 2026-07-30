hypothetical_rule(action1_gate_step,action(action1),effect(translate(bottom_center_gate,0,-5))).
hypothetical_rule(action1_status_advance,action(action1),effect(advance_status_partition,1)).
hypothetical_rule(action1_combined_progress,action(action1),effect([translate(bottom_center_gate,0,-5),recolor(column(23,61,62),dark_gray,green)])).

evidence(action1_gate_step,parent_gate_geometry,[bbox(34,35,38,39),cap_bbox(34,35,38,36),base_bbox(34,37,38,39)]).
evidence(action1_gate_step,current_gate_geometry,[bbox(34,30,38,34),cap_bbox(34,30,38,31),base_bbox(34,32,38,34)]).
evidence(action1_gate_step,exact_translation,[delta(0,-5),preserved_size(5,5),preserved_color_layout]).
evidence(action1_status_advance,status_cell_change,[cell(23,61,dark_gray,green),cell(23,62,dark_gray,green)]).
evidence(action1_status_advance,status_bar_dimensions,[green_width(10,11),dark_width(32,31)]).
evidence(action1_combined_progress,synchronized_observation,[gate_translation(0,-5),status_advance_columns(1)]).

supported_by(action1_gate_step,parent_gate_geometry).
supported_by(action1_gate_step,current_gate_geometry).
supported_by(action1_gate_step,exact_translation).
supported_by(action1_status_advance,status_cell_change).
supported_by(action1_status_advance,status_bar_dimensions).
supported_by(action1_combined_progress,synchronized_observation).

confidence(action1_gate_step,0.72).
confidence(action1_status_advance,0.72).
confidence(action1_combined_progress,0.62).

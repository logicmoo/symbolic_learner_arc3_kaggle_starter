hypothetical_rule(goal_progress, move_reduces_distance_to_exit, step_13).
hypothetical_rule(level1_first_image_baseline, identities_anchor_to_first_image, step_scope(level_1)).
confidence(goal_progress, 0.66).
confidence(level1_first_image_baseline, 0.89).
observed_rule(contact_triggers_rotation, caused_by(rotation_event_rotor_wheel, contact(player_entity, plus_sign))).
confidence(contact_triggers_rotation, 0.84).
observed_rule(glyph_alignment_opens_top_exit, alignment_changed_to_open(alignment_event_top_exit, top_exit)).
supported_by(glyph_alignment_opens_top_exit, aligned(glyph_a, glyph_b)).
supported_by(glyph_alignment_opens_top_exit, escape_possible(player_entity, top_exit)).
confidence(glyph_alignment_opens_top_exit, 0.87).

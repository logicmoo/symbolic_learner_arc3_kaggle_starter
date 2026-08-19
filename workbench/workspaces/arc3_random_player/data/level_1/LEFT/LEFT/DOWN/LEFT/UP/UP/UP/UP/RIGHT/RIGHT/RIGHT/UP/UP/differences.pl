transition_step(13).
command_executed('UP').
touched(player_entity, plus_sign).
rotated(rotor_wheel, degrees(90), direction(cw)).
caused_by(rotation_event_rotor_wheel, contact(player_entity, plus_sign)).
aligned(glyph_a, glyph_b).
alignment_changed_to_open(alignment_event_top_exit, top_exit).
escape_possible(player_entity, top_exit).
diff_turtle_patch(step_13_patch, [set_pos(22,8), set_color(rgb(255,255,0)), set_width(1), pendown, fwd(2), penup, rot(180), fwd(1), rot(90), pendown, fwd(1)]).

transition_step(6).
command_executed('UP').
touched(player_entity, plus_sign).
rotated(rotor_wheel, degrees(90), direction(cw)).
caused_by(rotation_event_rotor_wheel, contact(player_entity, plus_sign)).
diff_turtle_patch(step_6_patch, [set_pos(22,8), set_color(rgb(255,255,0)), set_width(1), pendown, fwd(2), penup, rot(180), fwd(1), rot(90), pendown, fwd(1)]).

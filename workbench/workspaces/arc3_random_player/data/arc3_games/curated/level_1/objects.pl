object(player_entity, agent, current).
object(plus_sign, trigger, current).
object(rotor_wheel, mechanism, current).
object(glyph_a, glyph, current).
object(glyph_b, glyph, current).

object(top_exit, exit, current).
object(path_corridor, corridor, current).
object(obstacle_cluster_a, obstacle, current).
object(hud_score_panel, hud, current).
object(g_player_plus_rotor, object_group, current).

object(g_glyph_pair, object_group, current).
object(g_exit_corridor, object_group, current).
component_of(player_entity, g_player_plus_rotor).
component_of(plus_sign, g_player_plus_rotor).
component_of(rotor_wheel, g_player_plus_rotor).
component_of(glyph_a, g_glyph_pair).
component_of(glyph_b, g_glyph_pair).
component_of(path_corridor, g_exit_corridor).
component_of(top_exit, g_exit_corridor).
role(plus_sign, trigger).
role(top_exit, goal_exit).
aligned_with(glyph_a, glyph_b, vertical).
confidence(rotor_wheel, 0.90).
confidence(g_glyph_pair, 0.85).

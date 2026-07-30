moved(bottom_center_gate,bbox(34,35,38,39),bbox(34,30,38,34)).
moved(gray_gate_cap,bbox(34,35,38,36),bbox(34,30,38,31)).
moved(red_gate_base,bbox(34,37,38,39),bbox(34,32,38,34)).

restored(cell_runs([run(35,34,38),run(36,34,38),run(37,34,38),run(38,34,38),run(39,34,38)]),[light_gray,dark_red],green).
overwritten(cell_runs([run(30,34,38),run(31,34,38)]),green,light_gray).
overwritten(cell_runs([run(32,34,38),run(33,34,38),run(34,34,38)]),green,dark_red).
reshaped(green_main_platform,area(820),area(820),restored_and_overwritten_gate_footprints).

recolored(cell_runs([run(61,23,23),run(62,23,23)]),dark_gray,green).
resized(bottom_green_status_bar,size(10,2),size(11,2)).
resized(bottom_dark_status_bar,size(32,2),size(31,2)).
changed_bbox(bottom_green_status_bar,bbox(13,61,22,62),bbox(13,61,23,62)).
changed_bbox(bottom_dark_status_bar,bbox(23,61,54,62),bbox(24,61,54,62)).

unchanged(blue_black_player,bbox(20,31,22,33),[cell(21,31),cell(20,32),cell(21,32),cell(22,32),cell(21,33)]).
unchanged(green_upper_chamber_frame,bbox(32,8,40,16),area(32)).
unchanged(gray_upper_chamber_interior,bbox(33,9,39,15),area(43)).
unchanged(yellow_inner_cavity,bbox(24,30,33,44),area(100)).
unchanged(lower_left_control_panel,bbox(1,53,10,62),size(10,10)).
unchanged(bottom_status_panel,bbox(12,60,63,63),size(52,4)).
unchanged(left_cyan_status_cell,bbox(56,61,57,62),area(4)).
unchanged(middle_cyan_status_cell,bbox(59,61,60,62),area(4)).
unchanged(right_cyan_status_cell,bbox(62,61,63,62),area(4)).

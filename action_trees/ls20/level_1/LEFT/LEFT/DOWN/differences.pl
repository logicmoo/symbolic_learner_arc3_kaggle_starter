transition_action(parent,current,action2).
changed_cells(parent,current,[]).
unchanged(parent,current,logical_grid(bbox(0,0,64,64),area(4096))).
unchanged(parent,current,visible_color_partition,evidence(exact_cellwise_match,4096)).
unchanged(parent,current,blue_black_player,evidence(bbox(20,31,3,3),occupied_cells([cell(21,31),cell(20,32),cell(21,32),cell(22,32),cell(21,33)]))).
unchanged(parent,current,bottom_green_status_bar,evidence(bbox(13,61,2,2),cell_runs([rows(61,62,13,14)]))).

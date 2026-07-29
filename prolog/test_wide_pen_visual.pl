:- use_module(turtle_dsl).
:- use_module(world_state).

%% Visual test runner for wide pen (pen_width) functionality
%% Similar to arc2_runner.pl - displays visual output of various pen widths

run_test(Name, Program) :-
    format('~n=== ~w ===~n', [Name]),
    initial_state(State0),
    execute_program(Program, State0, State),
    render_state(State).

% Test 1: Single width pen (default)
test_width_1 :-
    run_test('Width 1 - Horizontal Line', [
        penup, set_pos(2, 5),
        pen_width(1), pendown,
        fwd(6)
    ]).

% Test 2: Width 2 pen - horizontal
test_width_2_horizontal :-
    run_test('Width 2 - Horizontal Line', [
        penup, set_pos(2, 4),
        pen_width(2), pendown,
        fwd(6)
    ]).

% Test 3: Width 3 pen - horizontal
test_width_3_horizontal :-
    run_test('Width 3 - Horizontal Line', [
        penup, set_pos(2, 4),
        pen_width(3), pendown,
        fwd(6)
    ]).

% Test 4: Width 4 pen - horizontal
test_width_4_horizontal :-
    run_test('Width 4 - Horizontal Line', [
        penup, set_pos(2, 3),
        pen_width(4), pendown,
        fwd(6)
    ]).

% Test 5: Width 1 vertical
test_width_1_vertical :-
    run_test('Width 1 - Vertical Line', [
        penup, set_pos(5, 2),
        pen_width(1), rot(90), pendown,
        fwd(6)
    ]).

% Test 6: Width 2 vertical
test_width_2_vertical :-
    run_test('Width 2 - Vertical Line', [
        penup, set_pos(4, 2),
        pen_width(2), rot(90), pendown,
        fwd(6)
    ]).

% Test 7: Width 3 vertical
test_width_3_vertical :-
    run_test('Width 3 - Vertical Line', [
        penup, set_pos(4, 2),
        pen_width(3), rot(90), pendown,
        fwd(6)
    ]).

% Test 8: Width 4 vertical
test_width_4_vertical :-
    run_test('Width 4 - Vertical Line', [
        penup, set_pos(3, 2),
        pen_width(4), rot(90), pendown,
        fwd(6)
    ]).

% Test 9: Square with width 1
test_square_width_1 :-
    run_test('Width 1 - Square', [
        penup, set_pos(2, 2),
        pen_width(1), pendown,
        fwd(5), rot(90),
        fwd(5), rot(90),
        fwd(5), rot(90),
        fwd(5)
    ]).

% Test 10: Square with width 2
test_square_width_2 :-
    run_test('Width 2 - Square', [
        penup, set_pos(2, 2),
        pen_width(2), pendown,
        fwd(5), rot(90),
        fwd(5), rot(90),
        fwd(5), rot(90),
        fwd(5)
    ]).

% Test 11: Cross pattern with width 2
test_cross_width_2 :-
    run_test('Width 2 - Cross Pattern', [
        penup, set_pos(5, 3),
        pen_width(2), pendown,
        rot(90), fwd(4),
        penup, set_pos(3, 5), pendown,
        rot(-90), fwd(4)
    ]).

% Test 12: Diagonal with width 3
test_diagonal_width_3 :-
    run_test('Width 3 - Diagonal Steps', [
        penup, set_pos(1, 4),
        pen_width(3), pendown,
        fwd(2), rot(90), fwd(2),
        rot(-90), fwd(2), rot(90), fwd(2)
    ]).

% Test 13: All widths comparison (horizontal)
test_all_widths_horizontal :-
    run_test('All Widths - Horizontal Comparison', [
        penup, set_pos(1, 1),
        pen_width(1), pendown, fwd(3), penup,
        set_pos(1, 3), pen_width(2), pendown, fwd(3), penup,
        set_pos(1, 5), pen_width(3), pendown, fwd(3), penup,
        set_pos(1, 7), pen_width(4), pendown, fwd(3)
    ]).

% Test 14: All widths comparison (vertical)
test_all_widths_vertical :-
    run_test('All Widths - Vertical Comparison', [
        rot(90),
        penup, set_pos(1, 1),
        pen_width(1), pendown, fwd(3), penup,
        set_pos(3, 1), pen_width(2), pendown, fwd(3), penup,
        set_pos(5, 1), pen_width(3), pendown, fwd(3), penup,
        set_pos(7, 1), pen_width(4), pendown, fwd(3)
    ]).

% Test 15: Width changing mid-stroke
test_width_change :-
    run_test('Dynamic Width Change', [
        penup, set_pos(2, 2),
        pen_width(1), pendown, fwd(2),
        pen_width(2), fwd(2),
        pen_width(3), fwd(2)
    ]).

% Run all visual tests
run_all :-
    format('~n~n╔════════════════════════════════════════╗~n', []),
    format('║  WIDE PEN VISUAL TEST SUITE           ║~n', []),
    format('╚════════════════════════════════════════╝~n~n', []),

    test_width_1,
    test_width_2_horizontal,
    test_width_3_horizontal,
    test_width_4_horizontal,
    test_width_1_vertical,
    test_width_2_vertical,
    test_width_3_vertical,
    test_width_4_vertical,
    test_square_width_1,
    test_square_width_2,
    test_cross_width_2,
    test_diagonal_width_3,
    test_all_widths_horizontal,
    test_all_widths_vertical,
    test_width_change,

    format('~n~n╔════════════════════════════════════════╗~n', []),
    format('║  ALL VISUAL TESTS COMPLETED            ║~n', []),
    format('╚════════════════════════════════════════╝~n~n', []).

% Quick test - just a few key examples
run_quick :-
    format('~n~n╔════════════════════════════════════════╗~n', []),
    format('║  WIDE PEN QUICK VISUAL TEST            ║~n', []),
    format('╚════════════════════════════════════════╝~n~n', []),

    test_all_widths_horizontal,
    test_all_widths_vertical,
    test_square_width_2,

    format('~n~nQuick test completed!~n', []).

:- module(generative_form, [
    canonicalize_form/3,
    render_form/4,
    fit_form_instance/4,
    form_distance/4
]).

:- use_module(turtle_dsl).

% Grid forms reuse the existing turtle_dsl implementation rather than creating
% a second drawing engine. Raster forms can add clauses behind this interface.
canonicalize_form(grid, Program, Program).

render_form(grid, Program, InitialState, FinalState) :-
    turtle_dsl:execute_program(Program, InitialState, FinalState).

fit_form_instance(grid, Program, CandidateProgram, Fit) :-
    ( Program == CandidateProgram -> Residual = 0.0 ; Residual = 1.0 ),
    Fit = _{parameters:_{}, residual:Residual}.

form_distance(grid, Left, Right, Distance) :-
    ( Left == Right -> Distance = 0.0 ; Distance = 1.0 ).

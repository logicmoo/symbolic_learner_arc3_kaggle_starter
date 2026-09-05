% object_memory.pl — persistent GLOBAL object memory for the vision line.
%
% A cross-encounter, disk-backed store of recognized objects keyed by their
% (shape signature, color). It survives across runs and sessions via
% library(persistency): every assert is journaled to the attached DB file, so an
% object first seen in one grid-game encounter is recognized (not re-minted) when
% it recurs in a later encounter. This is the Phase 2 "persistent symbolic
% memory / later recognition as the same object" substrate.
%
% Batch interface (consulted together with a generated facts file that provides
% db/1, when_stamp/1 and sig/2, then `run_memory` is called):
%
%   db('/path/to/object_memory.db.pl').
%   when_stamp('ls20-saved_001').
%   sig('<shape-key>', '<color>').
%   ...
%
% For each sig/2 it prints one line:  mem <GlobalId> <Key> <Color> <Seen> <t|f>
% where Seen is the accumulated encounter count and the last field is t when the
% object is brand new to memory, f when it was recognized from a prior encounter.
%
% Placement: the batch may also provide place/5 facts recording, per game and per
% tracked instance, its move-to-move (x,y,shape) trajectory. This is stored
% separately from the (position-invariant) shape identity so a moving object is
% not seen as new; the recorded shape-per-move lets a later similar shape be
% recognized as a meaningful recurrence.

:- use_module(library(persistency)).

:- dynamic sig/2.
:- dynamic db/1.
:- dynamic when_stamp/1.
:- dynamic shape/3.
:- dynamic place/5.
:- dynamic variant/4.

:- persistent
     known_object(key:atom, color:atom, first:atom, last:atom, seen:integer).
:- persistent
     known_placement(game:atom, iid:atom, gid:atom, points:atom, moves:integer).

% recognize-or-add: reuse an existing identity and bump its encounter count, or
% mint a new persistent identity the first time this (shape,color) is seen.
remember(Key, Color, When, Id, Seen, New) :-
    ( known_object(Key, Color, First, _Last0, Seen0)
    -> retract_known_object(Key, Color, First, _, Seen0),
       Seen is Seen0 + 1,
       assert_known_object(Key, Color, First, When, Seen),
       New = f
    ;  Seen = 1,
       assert_known_object(Key, Color, When, When, Seen),
       New = t
    ),
    format(atom(Id), 'gobj_~w_~w', [Color, Key]).

% name of an observed shape key: the full shape, else any variant (a shrunk /
% rotated / diagonal form) it matches, else '-'. shape/3 + variant/4 are the
% colorless vocabulary consulted from shape_dir/shapes.pl (no identity).
shape_name(Key, Name) :- shape(Key, Name, _), !.
shape_name(Key, Name) :- variant(Key, Name, _, _), !.
shape_name(_, '-').

% record (or refresh) a tracked instance's move-to-move (x,y,shape) trajectory for
% a game. Keyed by (game, instance-id); replaces the prior trajectory for that pair.
remember_placement(Game, Iid, Gid, Points, Moves) :-
    forall(known_placement(Game, Iid, G0, P0, M0),
           retract_known_placement(Game, Iid, G0, P0, M0)),
    assert_known_placement(Game, Iid, Gid, Points, Moves).

% report the size of the consulted shape vocabulary (no identity is touched).
run_seed :-
    aggregate_all(count, shape(_, _, _), NS),
    aggregate_all(count, variant(_, _, _, _), NV),
    format("shapes ~w variants ~w~n", [NS, NV]),
    halt.
run_seed :- halt(1).

run_memory :-
    ( db(DB) -> db_attach(DB, []) ; true ),
    ( when_stamp(When) -> true ; When = unknown ),
    forall(sig(Key, Color),
           ( remember(Key, Color, When, Id, Seen, New),
             shape_name(Key, SName),
             format("mem ~w ~w ~w ~w ~w ~w~n", [Id, Key, Color, Seen, New, SName]) )),
    forall(place(Game, Iid, Gid, Points, Moves),
           ( remember_placement(Game, Iid, Gid, Points, Moves),
             format("place ~w ~w ~w~n", [Iid, Moves, Gid]) )),
    halt.
run_memory :- halt(1).

% dump the attached identity store (known_object + known_placement) as
% tab-delimited lines for the registry viewer. db(DB) selects which scope.
run_dump :-
    ( db(DB) -> db_attach(DB, []) ; true ),
    forall(known_object(K, C, F, L, S),
           format("obj\t~w\t~w\t~w\t~w\t~w~n", [K, C, F, L, S])),
    forall(known_placement(G, I, Gd, P, M),
           format("plc\t~w\t~w\t~w\t~w\t~w~n", [G, I, Gd, P, M])),
    halt.
run_dump :- halt(1).

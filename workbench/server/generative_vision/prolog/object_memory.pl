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

:- use_module(library(persistency)).

:- dynamic sig/2.
:- dynamic db/1.
:- dynamic when_stamp/1.
:- dynamic shape/3.

:- persistent
     known_object(key:atom, color:atom, first:atom, last:atom, seen:integer).
:- persistent
     known_shape(key:atom, name:atom, turtle:atom).

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

% idempotent seeding of the shape library (e.g. the tetrominoes) as named
% turtle programs. Asserts a shape the first time its key is seen, and reconciles
% the (derived) name/turtle if the seeding code changed how the shape is named.
seed_shape(Key, Name, Turtle) :-
    ( known_shape(Key, Name0, Turtle0)
    -> ( ( Name0 == Name, Turtle0 == Turtle ) -> true
       ;  retract_known_shape(Key, Name0, Turtle0),
          assert_known_shape(Key, Name, Turtle) )
    ;  assert_known_shape(Key, Name, Turtle) ).

run_seed :-
    ( db(DB) -> db_attach(DB, []) ; true ),
    forall(shape(K, N, T), seed_shape(K, N, T)),
    forall(known_shape(K, N, _), format("shape ~w ~w~n", [K, N])),
    halt.
run_seed :- halt(1).

run_memory :-
    ( db(DB) -> db_attach(DB, []) ; true ),
    forall(shape(K, N, T), seed_shape(K, N, T)),
    ( when_stamp(When) -> true ; When = unknown ),
    forall(sig(Key, Color),
           ( remember(Key, Color, When, Id, Seen, New),
             ( known_shape(Key, SName, _) -> true ; SName = '-' ),
             format("mem ~w ~w ~w ~w ~w ~w~n", [Id, Key, Color, Seen, New, SName]) )),
    halt.
run_memory :- halt(1).

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

:- dynamic sig/1.
:- dynamic occ/3.
:- dynamic db/1.
:- dynamic when_stamp/1.
:- dynamic shape/3.
:- dynamic place/5.
:- dynamic variant/4.

% Option A object model: an OBJECT is a scale + colour normalized shape identity
% (Key = its shape name). Colour and full size are OCCURRENCE attributes bound to
% the object via known_variation, so recolour / resize / move all keep the same
% object identity. known_object counts how many encounters recognized the object;
% known_variation records each distinct (colour, size) it has appeared as.
:- persistent
     known_object(key:atom, first:atom, last:atom, seen:integer).
:- persistent
     known_variation(key:atom, color:atom, size:integer, seen:integer).
:- persistent
     known_placement(game:atom, iid:atom, gid:atom, points:atom, moves:integer).

% recognize-or-add by SHAPE identity only: reuse an existing object and bump its
% encounter count, or mint a new persistent object the first time this shape is
% seen (regardless of colour or size).
remember(Key, When, Id, Seen, New) :-
    ( known_object(Key, First, _Last0, Seen0)
    -> retract_known_object(Key, First, _, Seen0),
       Seen is Seen0 + 1,
       assert_known_object(Key, First, When, Seen),
       New = f
    ;  Seen = 1,
       assert_known_object(Key, When, When, Seen),
       New = t
    ),
    format(atom(Id), 'gobj_~w', [Key]).

% record (or bump) one (colour, size) occurrence variation bound to an object.
remember_variation(Key, Color, Size) :-
    ( known_variation(Key, Color, Size, VS0)
    -> retract_known_variation(Key, Color, Size, VS0),
       VS is VS0 + 1,
       assert_known_variation(Key, Color, Size, VS)
    ;  assert_known_variation(Key, Color, Size, 1)
    ).

% recognize-only: report the object identity + accumulated count for an observed
% shape identity WITHOUT minting a new object or bumping any count. Seen is the
% stored encounter count (0 when unknown); New = t means the object is not yet in
% memory (it would be minted if committed), f means it was recognized from a prior
% encounter. Non-mutating counterpart of remember/5.
recognize(Key, Id, Seen, New) :-
    ( known_object(Key, _First, _Last, Seen0)
    -> Seen = Seen0, New = f
    ;  Seen = 0, New = t ),
    format(atom(Id), 'gobj_~w', [Key]).

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

% commit batch: for each object identity sig(Key) recognize-or-mint and print
%   mem <GlobalId> <Key> <Seen> <t|f>
% then bind every occurrence variation occ(Key,Color,Size) and record placements.
run_memory :-
    ( db(DB) -> db_attach(DB, []) ; true ),
    ( when_stamp(When) -> true ; When = unknown ),
    forall(sig(Key),
           ( remember(Key, When, Id, Seen, New),
             format("mem ~w ~w ~w ~w~n", [Id, Key, Seen, New]) )),
    forall(occ(Key, Color, Size), remember_variation(Key, Color, Size)),
    forall(place(Game, Iid, Gid, Points, Moves),
           ( remember_placement(Game, Iid, Gid, Points, Moves),
             format("place ~w ~w ~w~n", [Iid, Moves, Gid]) )),
    halt.
run_memory :- halt(1).

% recognize-only batch: like run_memory but read-only. For each sig(Key) it prints
%   mem <GlobalId> <Key> <Seen> <t|f>
% and never asserts, bumps, records variations, or placements, so the attached DB
% is left byte-for-byte unchanged. With no db/1 every object is unknown (Seen 0).
run_recognize :-
    ( db(DB) -> db_attach(DB, []) ; true ),
    forall(sig(Key),
           ( recognize(Key, Id, Seen, New),
             format("mem ~w ~w ~w ~w~n", [Id, Key, Seen, New]) )),
    halt.
run_recognize :- halt(1).

% dump the attached identity store (objects + variations + placements) as
% tab-delimited lines for the registry viewer. db(DB) selects which scope.
run_dump :-
    ( db(DB) -> db_attach(DB, []) ; true ),
    forall(known_object(K, F, L, S),
           format("obj\t~w\t~w\t~w\t~w~n", [K, F, L, S])),
    forall(known_variation(K, C, Z, S),
           format("var\t~w\t~w\t~w\t~w~n", [K, C, Z, S])),
    forall(known_placement(G, I, Gd, P, M),
           format("plc\t~w\t~w\t~w\t~w\t~w~n", [G, I, Gd, P, M])),
    halt.
run_dump :- halt(1).

% arc_group.pl — bbox-FREE symbolic grouping for the ARC "prolog line" of the
% reduce pipeline.  Consumes topological facts emitted by symbolic_arc.py and
% prints machine-readable results for the pipeline to turn into metta/parts.json.
%
% Facts in:  region(Id,Color,Area,centroid(CX,CY)).  adjacent(A,B).
%            encloses(Outer,Inner).  border(Id).  img_size(W,H).
% Emits:     pof <Inner> <Outer>       (containment, from encloses)
%            obj <ClusterN> <RegionId> (object instance, adjacency cluster)

:- dynamic region/4.
:- dynamic adjacent/2.
:- dynamic encloses/2.
:- dynamic border/1.
:- dynamic img_size/2.

background(Id) :-
    border(Id), img_size(W, H), region(Id, _, Area, _),
    Area >= 0.10 * W * H.

foreground(Id) :- region(Id, _, _, _), \+ background(Id).

part_of(Inner, Outer) :- encloses(Outer, Inner).

adj(A, B) :- adjacent(A, B).
adj(A, B) :- adjacent(B, A).
nadj(A, B) :- adj(A, B), \+ background(A), \+ background(B).

cluster([], Acc, S) :- sort(Acc, S).
cluster([X|Q], Acc, Out) :-
    ( memberchk(X, Acc) -> cluster(Q, Acc, Out)
    ; findall(Y, (nadj(X, Y), \+ memberchk(Y, Acc)), Ns),
      append(Q, Ns, Q1), cluster(Q1, [X|Acc], Out) ).

objects(Objects) :-
    findall(Id, foreground(Id), Ids),
    partition_objects(Ids, [], Objects).

partition_objects([], _, []).
partition_objects([Id|T], Seen, Objs) :-
    ( memberchk(Id, Seen) -> partition_objects(T, Seen, Objs)
    ; cluster([Id], [], Members), append(Members, Seen, Seen1),
      Objs = [Members|Rest], partition_objects(T, Seen1, Rest) ).

emit :-
    forall(part_of(I, O), format("pof ~w ~w~n", [I, O])),
    objects(Os),
    forall(nth1(K, Os, M),
           forall(member(R, M), format("obj ~w ~w~n", [K, R]))),
    halt.

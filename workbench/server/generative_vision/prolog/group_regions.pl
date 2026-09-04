% group_regions.pl — bbox-FREE symbolic grouping over topological region facts
% from pixels_to_regions2.py.  Containment comes from `encloses/2` (one region
% fully surrounds another) and object instances from connected components of
% `adjacent/2` (pixels actually touch).  No bounding boxes are ever used.
%
% Facts consumed:
%   region(Id, Color, Area, centroid(CX,CY)).
%   adjacent(A, B).  encloses(Outer, Inner).  border(Id).  img_size(W, H).
%
% Run: swipl -q -g "consult('group_regions.pl'), consult('REGIONS.pl'), report" -t halt

:- dynamic region/4.
:- dynamic adjacent/2.
:- dynamic encloses/2.
:- dynamic border/1.
:- dynamic img_size/2.

part(Id, Color, Area, Centroid) :- region(Id, Color, Area, Centroid).

% ---- background: hugs the edge and is large (bridges unrelated objects) -----
background(Id) :-
    border(Id),
    img_size(W, H),
    region(Id, _, Area, _),
    Area >= 0.10 * W * H.

foreground(Id) :- region(Id, _, _, _), \+ background(Id).

% ---- containment: straight from topology, no boxes -------------------------
part_of(Inner, Outer) :- encloses(Outer, Inner).

group(Outer, Inners) :-
    findall(I, encloses(Outer, I), Inners),
    Inners \== [].

% ---- object instances: connected components of touch adjacency -------------
adj(A, B) :- adjacent(A, B).
adj(A, B) :- adjacent(B, A).
nadj(A, B) :- adj(A, B), \+ background(A), \+ background(B).

cluster([], Acc, Sorted) :- sort(Acc, Sorted).
cluster([X|Q], Acc, Out) :-
    ( memberchk(X, Acc)
    -> cluster(Q, Acc, Out)
    ;  findall(Y, (nadj(X, Y), \+ memberchk(Y, Acc)), Ns),
       append(Q, Ns, Q1),
       cluster(Q1, [X|Acc], Out)
    ).

objects(Objects) :-
    findall(Id, foreground(Id), Ids),
    partition_objects(Ids, [], Objects).

partition_objects([], _, []).
partition_objects([Id|T], Seen, Objs) :-
    ( memberchk(Id, Seen)
    -> partition_objects(T, Seen, Objs)
    ;  cluster([Id], [], Members),
       append(Members, Seen, Seen1),
       Objs = [Members|Rest],
       partition_objects(T, Seen1, Rest)
    ).

% ---- report ----------------------------------------------------------------
report :-
    aggregate_all(count, region(_,_,_,_), NR),
    aggregate_all(count, encloses(_,_), NE),
    findall(Id, background(Id), Bg), length(Bg, NB),
    objects(Objs), length(Objs, NO),
    format("~n== ~w regions, ~w enclosures, ~w background, ~w objects ==~n", [NR, NE, NB, NO]),
    format("~n== containment groups (encloses) ==~n"),
    forall((group(P, Cs), length(Cs, L), L >= 1),
           ( region(P, Col, _, _), format("  ~w (~w) encloses ~w~n", [P, Col, Cs]) )),
    format("~n== object instances (adjacency clusters, foreground) ==~n"),
    forall((member(M, Objs), length(M, L), L >= 3),
           format("  object of ~w regions: ~w~n", [L, M])).

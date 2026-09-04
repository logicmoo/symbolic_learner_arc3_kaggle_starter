% arc_parts.pl — a purely symbolic recognizer that finds the SAME parts and
% groups the vision model returned for an ARC frame, but deterministically
% from the underlying colored grid instead of from the rendered image.
%
%   part  = a maximal 4-connected region of one color   (flood fill)
%   group = containment: a part is `part_of` the SMALLEST other part whose
%           bounding box strictly encloses it (background < walls < maze < item)
%
% The vision model invents human labels ("maze_body", "player"); Prolog can't,
% but it recovers exactly the same regions (by color) and the same nesting.
%
% Run:  swipl -q -g demo -t halt arc_parts.pl

:- dynamic cell/3.
:- table regions/1.

% ---- load a grid (list of rows of color atoms) into cell(X,Y,Color) --------
load_grid(Rows) :-
    retractall(cell(_,_,_)),
    forall(nth0(Y, Rows, Row),
           forall(nth0(X, Row, C), assertz(cell(X, Y, C)))).

% ---- 4-neighbour adjacency -------------------------------------------------
adj(X,Y,X1,Y) :- X1 is X+1.
adj(X,Y,X1,Y) :- X1 is X-1.
adj(X,Y,X,Y1) :- Y1 is Y+1.
adj(X,Y,X,Y1) :- Y1 is Y-1.

% ---- all maximal same-color regions, each with a stable id p1,p2,... -------
regions(Regions) :-
    findall(X-Y-C, cell(X,Y,C), Cs),
    grow(Cs, [], 1, Regions).

grow([], _, _, []).
grow([X-Y-C|T], Seen, N, Out) :-
    ( memberchk(X-Y, Seen)
    -> grow(T, Seen, N, Out)
    ;  flood([X-Y], C, [], Cells),
       append(Cells, Seen, Seen1),
       atom_concat(p, N, Id),
       N1 is N + 1,
       Out = [region(Id,C,Cells)|Rest],
       grow(T, Seen1, N1, Rest)
    ).

% breadth-first flood fill of one color region
flood([], _, Acc, Out) :- sort(Acc, Out).
flood([X-Y|Q], C, Acc, Out) :-
    ( memberchk(X-Y, Acc)
    -> flood(Q, C, Acc, Out)
    ;  cell(X,Y,C)
    -> findall(NX-NY,
               ( adj(X,Y,NX,NY), cell(NX,NY,C),
                 \+ memberchk(NX-NY,Acc), \+ memberchk(NX-NY,Q) ),
               Ns),
       append(Q, Ns, Q1),
       flood(Q1, C, [X-Y|Acc], Out)
    ;  flood(Q, C, Acc, Out)
    ).

% ---- a part: id, color, area, bounding box, centroid -----------------------
part(Id, Color, Area, bbox(X0,Y0,X1,Y1), centroid(CX,CY)) :-
    regions(Rs),
    member(region(Id,Color,Cells), Rs),
    length(Cells, Area),
    findall(X, member(X-_, Cells), Xs),
    findall(Y, member(_-Y, Cells), Ys),
    min_list(Xs,X0), max_list(Xs,X1),
    min_list(Ys,Y0), max_list(Ys,Y1),
    sum_list(Xs,SX), sum_list(Ys,SY),
    CX is SX // Area, CY is SY // Area.

% ---- grouping: nearest strictly-enclosing part -----------------------------
part_of(Child, Parent) :-
    part(Child,  _, _, CB, _),
    part(Parent, _, _, PB, _),
    Child \== Parent,
    encloses(PB, CB),
    box_area(PB, PBA), box_area(CB, CBA), PBA > CBA,
    \+ ( part(Mid, _, _, MB, _), Mid \== Parent, Mid \== Child,
         encloses(PB, MB), encloses(MB, CB),
         box_area(MB, MBA), MBA < PBA, MBA > CBA ).

box_area(bbox(X0,Y0,X1,Y1), A) :- A is (X1 - X0 + 1) * (Y1 - Y0 + 1).

encloses(bbox(PX0,PY0,PX1,PY1), bbox(CX0,CY0,CX1,CY1)) :-
    PX0 =< CX0, PY0 =< CY0, PX1 >= CX1, PY1 >= CY1.

group(Parent, Children) :-
    part(Parent, _, _, _, _),
    findall(C, part_of(C, Parent), Children),
    Children \== [].

% ---- pretty report ---------------------------------------------------------
report :-
    format("~n== parts ==~n"),
    forall(part(Id,Col,Area,bbox(X0,Y0,X1,Y1),centroid(CX,CY)),
           format("  ~w  ~w  area=~w  bbox=[~w,~w,~w,~w]  center=(~w,~w)~n",
                  [Id,Col,Area,X0,Y0,X1,Y1,CX,CY])),
    format("~n== groups (partOf nearest enclosing) ==~n"),
    ( group(_, _)
      -> forall(group(P2, Cs2), format("  ~w  contains  ~w~n", [P2, Cs2]))
      ;  format("  (none)~n") ),
    format("~n== flat partOf facts ==~n"),
    forall(part_of(C, P), format("  (partOf ~w ~w)~n", [C, P])).

% ---- demo grid: yellow playfield, tan wall ring, green maze, 2 items -------
demo_grid([
  [t,t,t,t,t,t,t,t,t,t,t,t],
  [t,y,y,y,y,y,y,y,y,y,y,t],
  [t,y,y,y,y,y,y,y,y,y,y,t],
  [t,y,y,g,g,g,g,g,g,y,y,t],
  [t,y,y,g,r,g,g,b,g,y,y,t],
  [t,y,y,g,g,g,g,g,g,y,y,t],
  [t,y,y,g,g,g,g,g,g,y,y,t],
  [t,y,y,y,y,y,y,y,y,y,y,t],
  [t,y,y,y,y,y,y,y,y,y,y,t],
  [t,t,t,t,t,t,t,t,t,t,t,t]
]).

demo :- demo_grid(G), load_grid(G), report.

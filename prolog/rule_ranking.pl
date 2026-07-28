:- module(rule_ranking, [
    rank_rules/3,
    preferred_rule/2
]).

:- use_module(library(pairs)).

:- meta_predicate rank_rules(+, 2, -).

rank_rules(Rules, Scorer, Ranked) :-
    must_be(callable, Scorer),
    maplist(score_rule(Scorer), Rules, Scored),
    keysort(Scored, Ascending),
    reverse(Ascending, Descending),
    maplist(to_ranked, Descending, Ranked).

score_rule(Scorer, Rule, Score-Rule) :-
    call(Scorer, Rule, Score),
    must_be(number, Score).

to_ranked(Score-Rule, ranked(Score, Rule)).

preferred_rule([ranked(_, Rule)|_], Rule).

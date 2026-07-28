:- module(rule_induction, [
    propose_transition_rules/4,
    specialize_rule/4,
    generalize_rule/4
]).

:- meta_predicate propose_transition_rules(+, +, 3, -).
:- meta_predicate specialize_rule(+, +, 3, -).
:- meta_predicate generalize_rule(+, +, 3, -).

propose_transition_rules(Candidates, Context, Inducer, Rules) :-
    must_be(callable, Inducer),
    call(Inducer, Candidates, Context, Rules).

specialize_rule(Rule, Evidence, Specializer, Specialized) :-
    must_be(callable, Specializer),
    call(Specializer, Rule, Evidence, Specialized).

generalize_rule(Rule, Evidence, Generalizer, Generalized) :-
    must_be(callable, Generalizer),
    call(Generalizer, Rule, Evidence, Generalized).

:- module(transition_rules, [
    store_transition_rule/2,
    transition_rule/2,
    applicable_transition_rule/3,
    apply_transition_rule/4,
    clear_transition_rules/0
]).

:- dynamic transition_rule/2.

% Store one canonical rule record. Existing rule IDs are exact identities and
% may not silently change their definition.
store_transition_rule(RuleId, Rule) :-
    must_be(atom, RuleId),
    must_be(dict, Rule),
    (   transition_rule(RuleId, Existing)
    ->  Existing == Rule
    ;   assertz(transition_rule(RuleId, Rule))
    ).

% Applicability and execution are supplied as callables so this module stores
% and governs rules without duplicating the domain-specific rule engine.
applicable_transition_rule(RuleId, State, Checker) :-
    transition_rule(RuleId, Rule),
    call(Checker, Rule, State).

apply_transition_rule(RuleId, State0, Executor, State) :-
    transition_rule(RuleId, Rule),
    call(Executor, Rule, State0, State).

clear_transition_rules :-
    retractall(transition_rule(_, _)).

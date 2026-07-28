:- module(transition_rules, [
    store_transition_rule/2,
    transition_rule/2,
    applicable_transition_rule/3,
    apply_transition_rule/4,
    clear_transition_rules/0
]).

:- use_module(object_memory_contract, []).

:- meta_predicate applicable_transition_rule(+, +, 2).
:- meta_predicate apply_transition_rule(+, +, 3, -).

transition_rule(RuleId, Rule) :-
    object_memory_contract:transition_rule(RuleId, Rule).

% Store one canonical rule record. Existing rule IDs are exact identities and
% may not silently change their definition. The canonical facts remain in
% object_memory_contract rather than being copied into this module.
store_transition_rule(RuleId, Rule) :-
    must_be(atom, RuleId),
    is_dict(Rule),
    (   transition_rule(RuleId, Existing)
    ->  Existing == Rule
    ;   assertz(object_memory_contract:transition_rule(RuleId, Rule))
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
    retractall(object_memory_contract:transition_rule(_, _)).

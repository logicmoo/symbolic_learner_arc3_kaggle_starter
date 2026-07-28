:- module(transition_analysis, [
    analyze_transition/5
]).

:- meta_predicate analyze_transition(+, +, +, 4, -).

% Analyzer is a callable provider. It may be native Prolog or a bridge over
% normalized GPT/Python artifacts, but the returned transition contract is one.
analyze_transition(Before, ActionOrEvent, After, Analyzer, Transition) :-
    must_be(callable, Analyzer),
    call(Analyzer, Before, ActionOrEvent, After, Transition).

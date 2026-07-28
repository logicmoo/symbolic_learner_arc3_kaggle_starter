:- module(transformation_learning, [
    infer_transformations/4,
    apply_transformation/4,
    validate_transformation/4
]).

:- meta_predicate infer_transformations(+, +, 3, -).
:- meta_predicate apply_transformation(+, +, 3, -).
:- meta_predicate validate_transformation(+, +, +, 3).

infer_transformations(Transition, Context, Learner, Candidates) :-
    must_be(callable, Learner),
    call(Learner, Transition, Context, Candidates).

apply_transformation(Candidate, State0, Executor, State) :-
    must_be(callable, Executor),
    call(Executor, Candidate, State0, State).

validate_transformation(Candidate, Before, After, Validator) :-
    must_be(callable, Validator),
    call(Validator, Candidate, Before, After).

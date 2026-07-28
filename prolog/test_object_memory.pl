:- begin_tests(object_memory).

:- use_module(object_memory_contract, []).
:- use_module(residual_gate).
:- use_module(single_writer).
:- use_module(prediction_ledger).
:- use_module(transition_rules).

reset_state :-
    retractall(object_memory_contract:candidate_object(_, _)),
    retractall(object_memory_contract:residual_candidate(_, _)),
    retractall(object_memory_contract:committed_atom(_, _)),
    prediction_ledger:clear_prediction_records,
    transition_rules:clear_transition_rules.

test(residual_promotes_on_recurrence, [setup(reset_state)]) :-
    Residual = _{
        disposition: provisional,
        structured: true,
        recurrence_count: 2,
        prediction_gain: 0.0
    },
    residual_gate:evaluate_residual(Residual, commit_request).

test(single_writer_forces_zero_confidence, [setup(reset_state)]) :-
    Candidate = _{atom_type: object, confidence: 0.9, provenance: []},
    single_writer:commit_candidate(ball, Candidate, Atom),
    assertion(Atom.confidence =:= 0.0),
    assertion(object_memory_contract:committed_atom(ball, Atom)).

test(invalid_grade_preserves_open_prediction, [setup(reset_state)]) :-
    Record = _{
        rule_id: rule_1,
        source_state_id: state_1,
        predicted_effects: [move],
        created_sequence: 10,
        outcome_sequence: none
    },
    prediction_ledger:record_prediction(prediction_1, Record),
    \+ prediction_ledger:grade_prediction(prediction_1, 10, move, 1.0, _),
    assertion(prediction_ledger:prediction_record(prediction_1, Record)).

test(valid_prediction_grade, [setup(reset_state)]) :-
    Record = _{
        rule_id: rule_1,
        source_state_id: state_1,
        predicted_effects: [move],
        created_sequence: 10,
        outcome_sequence: none
    },
    prediction_ledger:record_prediction(prediction_1, Record),
    prediction_ledger:grade_prediction(prediction_1, 11, move, 1.0, Closed),
    assertion(Closed.outcome_sequence =:= 11),
    assertion(Closed.grade =:= 1.0).

always_applicable(_Rule, _State).
copy_effect(Rule, State0, State) :-
    State = State0.put(effect, Rule.effect).

test(transition_rule_storage_and_application, [setup(reset_state)]) :-
    Rule = _{effect: moved_right},
    transition_rules:store_transition_rule(rule_1, Rule),
    transition_rules:applicable_transition_rule(rule_1, _{}, always_applicable),
    transition_rules:apply_transition_rule(rule_1, _{}, copy_effect, State),
    assertion(State.effect == moved_right),
    assertion(object_memory_contract:transition_rule(rule_1, Rule)).

:- end_tests(object_memory).

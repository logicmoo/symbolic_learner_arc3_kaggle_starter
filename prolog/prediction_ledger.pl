:- module(prediction_ledger, [
    prediction_record/2,
    record_prediction/2,
    grade_prediction/5,
    prediction_precedes_outcome/2,
    clear_prediction_records/0
]).

:- dynamic prediction_record/2.

record_prediction(Id, Record) :-
    must_be(atom, Id),
    \+ prediction_record(Id, _),
    Record.get(outcome_sequence, none) == none,
    assertz(prediction_record(Id, Record)).

prediction_precedes_outcome(Prediction, OutcomeSequence) :-
    Created = Prediction.created_sequence,
    OutcomeSequence > Created.

grade_prediction(Id, OutcomeSequence, Outcome, Grade, Closed) :-
    prediction_record(Id, Prediction),
    prediction_precedes_outcome(Prediction, OutcomeSequence),
    Prediction.get(outcome_sequence, none) == none,
    Closed = Prediction.put(_{
        outcome_sequence: OutcomeSequence,
        outcome: Outcome,
        grade: Grade
    }),
    retract(prediction_record(Id, Prediction)),
    assertz(prediction_record(Id, Closed)).

clear_prediction_records :-
    retractall(prediction_record(_, _)).

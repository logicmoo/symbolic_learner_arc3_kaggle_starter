:- module(prediction_ledger, [
    prediction_record/2,
    record_prediction/2,
    grade_prediction/5,
    prediction_precedes_outcome/2
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
    retract(prediction_record(Id, Prediction)),
    prediction_precedes_outcome(Prediction, OutcomeSequence),
    Prediction.get(outcome_sequence, none) == none,
    Closed = Prediction.put(_{
        outcome_sequence: OutcomeSequence,
        outcome: Outcome,
        grade: Grade
    }),
    assertz(prediction_record(Id, Closed)).

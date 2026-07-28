:- module(prediction_evaluation, [
    evaluate_prediction/4,
    grade_recorded_prediction/6
]).

:- use_module(prediction_ledger).

:- meta_predicate evaluate_prediction(+, +, 3, -).
:- meta_predicate grade_recorded_prediction(+, +, +, 3, -, -).

evaluate_prediction(Predicted, Observed, Comparator, Grade) :-
    must_be(callable, Comparator),
    call(Comparator, Predicted, Observed, Grade),
    must_be(number, Grade).

grade_recorded_prediction(
    PredictionId,
    OutcomeSequence,
    Observed,
    Comparator,
    Grade,
    Closed
) :-
    prediction_ledger:prediction_record(PredictionId, Prediction),
    Predicted = Prediction.predicted_effects,
    evaluate_prediction(Predicted, Observed, Comparator, Grade),
    prediction_ledger:grade_prediction(
        PredictionId,
        OutcomeSequence,
        Observed,
        Grade,
        Closed
    ).

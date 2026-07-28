:- module(residual_gate, [
    residual_disposition/2,
    evaluate_residual/2
]).

residual_disposition(absorbed, absorbed).
residual_disposition(provisional, provisional).
residual_disposition(commit_request, commit_request).

evaluate_residual(Residual, commit_request) :-
    Residual.get(structured, false) == true,
    ( Residual.get(recurrence_count, 0) > 1
    ; Residual.get(prediction_gain, 0.0) > 0.0
    ),
    !.
evaluate_residual(Residual, absorbed) :-
    Residual.get(disposition, provisional) == absorbed,
    !.
evaluate_residual(_, provisional).

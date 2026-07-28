:- module(game_object_learner_api, [
    process_transition/5,
    predict_with_rule/8,
    grade_prediction/6
]).

:- use_module(transition_analysis).
:- use_module(transformation_learning).
:- use_module(rule_induction).
:- use_module(rule_ranking).
:- use_module(transition_rules).
:- use_module(prediction_ledger).
:- use_module(prediction_evaluation).

% Providers is one dict of backend-specific callables. The orchestration and
% normalized result stay stable whether those callables use Prolog, GPT-backed
% artifacts, or deterministic Python through a bridge.
process_transition(Before, ActionOrEvent, After, Providers, Result) :-
    get_dict(analyzer, Providers, Analyzer),
    get_dict(learner, Providers, Learner),
    get_dict(inducer, Providers, Inducer),
    get_dict(scorer, Providers, Scorer),
    ( get_dict(context, Providers, Context) -> true ; Context = _{} ),
    transition_analysis:analyze_transition(
        Before, ActionOrEvent, After, Analyzer, Transition
    ),
    transformation_learning:infer_transformations(
        Transition, Context, Learner, Candidates
    ),
    rule_induction:propose_transition_rules(
        Candidates, Context, Inducer, Rules
    ),
    rule_ranking:rank_rules(Rules, Scorer, Ranked),
    store_ranked_rules(Ranked),
    Result = _{
        transition: Transition,
        candidates: Candidates,
        rules: Ranked
    }.

store_ranked_rules([]).
store_ranked_rules([ranked(_, Rule)|Rest]) :-
    RuleId = Rule.rule_id,
    transition_rules:store_transition_rule(RuleId, Rule),
    store_ranked_rules(Rest).

predict_with_rule(
    PredictionId,
    RuleId,
    SourceStateId,
    State,
    Executor,
    CreatedSequence,
    PredictedState,
    Record
) :-
    transition_rules:apply_transition_rule(
        RuleId, State, Executor, PredictedState
    ),
    Record = _{
        prediction_id: PredictionId,
        rule_id: RuleId,
        source_state_id: SourceStateId,
        predicted_effects: [PredictedState],
        created_sequence: CreatedSequence,
        outcome_sequence: none
    },
    prediction_ledger:record_prediction(PredictionId, Record).

grade_prediction(
    PredictionId,
    OutcomeSequence,
    OutcomeChannel,
    Comparator,
    Grade,
    Closed
) :-
    must_be(callable, OutcomeChannel),
    call(OutcomeChannel, Observed),
    prediction_evaluation:grade_recorded_prediction(
        PredictionId,
        OutcomeSequence,
        Observed,
        Comparator,
        Grade,
        Closed
    ).

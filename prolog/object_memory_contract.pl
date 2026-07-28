:- module(object_memory_contract, [
    candidate_object/2,
    residual_candidate/2,
    committed_atom/2,
    transition_rule/2,
    candidate_properties/2,
    candidate_correspondence/2,
    candidate_differences/2,
    candidate_rules/2,
    candidate_generative_form/2
]).

:- dynamic candidate_object/2.
:- dynamic residual_candidate/2.
:- dynamic committed_atom/2.
:- dynamic transition_rule/2.

% These normalized access predicates form the PROLOG backend of the same
% contract used by Python providers and GPT-generated .pl artifacts.
candidate_properties(Id, Properties) :-
    candidate_object(Id, Candidate),
    Properties = Candidate.get(properties, _{}).

candidate_correspondence(Id, Correspondence) :-
    candidate_object(Id, Candidate),
    Correspondence = Candidate.get(correspondence, []).

candidate_differences(Id, Differences) :-
    candidate_object(Id, Candidate),
    Differences = Candidate.get(differences, []).

candidate_rules(Id, Rules) :-
    candidate_object(Id, Candidate),
    Rules = Candidate.get(rules, []).

candidate_generative_form(Id, Form) :-
    candidate_object(Id, Candidate),
    Form = Candidate.get(generative_form, none).

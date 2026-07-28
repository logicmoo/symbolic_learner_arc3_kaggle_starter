:- module(single_writer, [
    commit_candidate/3,
    accrue_atom_evidence/4,
    tombstone_atom/3
]).

:- use_module(object_memory_contract).

commit_candidate(Handle, Candidate, Atom) :-
    must_be(atom, Handle),
    \+ committed_atom(Handle, _),
    Atom = Candidate.put(_{
        handle: Handle,
        confidence: 0.0,
        lifecycle_state: active
    }),
    assertz(object_memory_contract:committed_atom(Handle, Atom)).

accrue_atom_evidence(Handle, Confidence, Evidence, Updated) :-
    must_be(number, Confidence),
    Confidence >= 0.0,
    Confidence < 1.0,
    retract(object_memory_contract:committed_atom(Handle, Atom)),
    Provenance0 = Atom.get(provenance, []),
    append(Provenance0, [Evidence], Provenance),
    Updated = Atom.put(_{confidence:Confidence, provenance:Provenance}),
    assertz(object_memory_contract:committed_atom(Handle, Updated)).

tombstone_atom(Handle, Reason, Updated) :-
    retract(object_memory_contract:committed_atom(Handle, Atom)),
    Provenance0 = Atom.get(provenance, []),
    append(Provenance0, [Reason], Provenance),
    Updated = Atom.put(_{lifecycle_state:tombstoned, provenance:Provenance}),
    assertz(object_memory_contract:committed_atom(Handle, Updated)).

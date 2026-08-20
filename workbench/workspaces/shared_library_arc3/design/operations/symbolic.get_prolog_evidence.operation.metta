(
  (kind operation)
  (id symbolic.get_prolog_evidence)
  (label "Get Prolog Evidence")
  (description "Collect the ARC3 Prolog artifact bundle and expose it for inspection, validation, and downstream rule induction. The workflow selects this semantic Operation; its implementation may use a prompted LLM or deterministic Python without changing the workflow item.")
  (topics ([]
    arc3
    symbolic
  ))
  (inputs (
    (bundle ArtifactBundle)
  ))
  (outputs (
    (bundle ArtifactBundle)
    (validation Evidence)
  ))
  (children ([]
    symbolic.get_prolog_evidence.prompted_llm
    symbolic.get_prolog_evidence.python
  ))
  (preferredChild symbolic.get_prolog_evidence.prompted_llm)
  (example_execute (
    (action symbolic.get_prolog_evidence)
    (arguments (
      (bundle (
        (datatype ArtifactBundle)
        (label "ARC3 artifact bundle")
        (default ((node "") (registry "")))
      ))
    ))
  ))
)
(
  (kind operation)
  (id symbolic.get_prolog_evidence.prompted_llm)
  (label "Get Prolog Evidence / Prompted LLM")
  (description "Use the Visual Image Diff Prolog-evidence Prompt resource to inspect and cherry-pick the existing symbolic artifact bundle.")
  (topics ([]
    arc3
    symbolic
    llm
  ))
  (implementation llm.complete)
  (inputs (
    (bundle ArtifactBundle)
  ))
  (outputs (
    (bundle ArtifactBundle)
    (validation Evidence)
  ))
  (bindings (
    (prompts ([]
      visual_image_diff.pipeline.cherry_pick
    ))
    (separator "\n\n")
  ))
  (modelSelection (
    (models ([]))
    (strategy single)
  ))
  (parameters (
    (requiresVision false)
    (parseJson true)
    (responseFormat json_object)
  ))
  (parents ([]
    symbolic.get_prolog_evidence
  ))
)
(
  (kind operation)
  (id symbolic.get_prolog_evidence.python)
  (label "Get Prolog Evidence / Python + Prolog")
  (description "Read the existing ARC3 Prolog artifacts deterministically and ask SWI-Prolog to load-check them when the executable is available. This implementation makes no Prompt or LLM request.")
  (topics ([]
    arc3
    symbolic
    python
  ))
  (implementation python.callable)
  (inputs (
    (bundle ArtifactBundle)
  ))
  (outputs (
    (bundle ArtifactBundle)
    (validation Evidence)
  ))
  (python (
    (importMode file)
    (file python/visual_image_diff_operations.py)
    (callable collect_prolog_evidence)
  ))
  (parents ([]
    symbolic.get_prolog_evidence
  ))
)

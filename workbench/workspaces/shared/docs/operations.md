[â† Back to top-level README](../../../../README.md)

# Operations

A Operation is the abstract semantic operation in the workbench. A `operation_implementation` is one concrete way to perform that operation.

The workflow should normally point to the abstract Operation ID. The Operation lists allowed implementation variants and a default. The runtime resolves that abstract stage to a concrete implementation when the workflow is validated/executed.

```text
echo_into_titlecased.operation.metta
    ├── echo_into_titlecased_python.operation_implementation.metta
    ├── echo_into_titlecased_prolog.operation_implementation.metta
    └── echo_into_titlecased_llm.operation_implementation.metta
```

## Python implementations

Python callables need enough metadata to locate and invoke the code without hard-coding that knowledge into the workflow engine. A Python implementation can describe:

```metta
(
  (kind operation_implementation)
  (implementation python.callable)
  (python (
    (importMode module)
    (module shared_operation_callables)
    (file workbench/server/shared_operation_callables.py)
    (className null)
    (callable to_titlecase)
    (constructorArgs ([]))
    (constructorKwargs ())
    (callArgs ([]))
    (callKwargs ())
    (reload false)
  ))
)
```

`importMode` may be `module` or `file`. `className` is optional; when supplied, the runtime constructs the class and invokes the named method. Without a class, the callable is resolved directly from the module. Inputs are added to the call keyword arguments after any configured static arguments.

## SWI-Prolog implementations

A Prolog implementation can carry the exact source that SWI-Prolog should run. This is useful because a operation definition becomes a complete, inspectable implementation artifact rather than merely naming an external predicate whose source is hidden elsewhere.

```metta
(
  (kind operation_implementation)
  (implementation prolog.source)
  (prolog (
    (engine swipl)
    (predicate titlecase_text)
    (arity 2)
    (source_code ([]
      "titlecase_text(Input, Output) :-"
      "    ..."
    ))
  ))
)
```

The runtime materializes `source_code`, invokes SWI-Prolog, passes the selected operation input to the configured predicate, and captures the configured output plus execution diagnostics.

## LLM implementations

LLM implementation variants contain model/profile selection and prompt bindings. Prompt text remains a separate Prompt resource. The old ARC3 `llm_profiles[].prompt_text` list belongs to LLM operation implementation behavior, not model/profile configuration.

```text
model/profile selection
  single | parallel | compare | fallback

ordered prompts
  response_contract
  coordinate_contract
  object_extraction
  ...
```

This separation means the same abstract Operation can have Python, Prolog, MeTTa, LLM, HTTP, subprocess, or other implementations while preserving one stable semantic stage identity.

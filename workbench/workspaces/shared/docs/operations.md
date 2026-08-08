[â† Back to top-level README](../../../../README.md)

# Operations

An Operation is a semantic operation in the workbench. A root `operation` is an abstract contract; an `operation` with a same-kind parent is one concrete implementation.

The workflow should normally point to the abstract Operation ID. The Operation lists allowed implementation variants and a default. The runtime resolves that abstract stage to a concrete implementation when the workflow is validated/executed.

```text
echo_into_titlecased.operation.metta
    ├── echo_into_titlecased_python.operation.metta
    ├── echo_into_titlecased_prolog.operation.metta
    └── echo_into_titlecased_llm.operation.metta
```

## Python implementations

Python callables need enough metadata to locate and invoke the code without hard-coding that knowledge into the workflow engine. A Python implementation can describe:

```metta
(
  (kind operation)
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
  (kind operation)
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

LLM implementations bind an abstract Operation to a model and one or more reusable Prompt resources. The model decides *where* inference runs; the Prompt decides *what instructions* accompany the operation input. Prompt text therefore does not belong in a model profile or directly in the abstract Operation.

### Complete titlecase example

The `titlecase_demo` workflow points only to the abstract Operation and maps workflow data into and out of it:

```metta
(
  (kind workflow)
  (id titlecase_demo)
  (inputs ((text Text)))
  (outputs ((text $titlecased_text)))
  (steps ([]
    (
      (kind workflow_step)
      (id step_titlecase)
      (operation echo_into_titlecased)
      (inputs ((text $text)))
      (outputs ((text titlecased_text)))
    )
  ))
)
```

The abstract Operation owns the stable input/output contract, its executable example, the allowed implementations, and the default implementation:

```metta
(
  (kind operation)
  (id echo_into_titlecased)
  (inputs ((text Text)))
  (outputs ((text Text)))
  (example_execute (
    (action operation.invoke)
    (arguments (
      (text (
        (datatype Text)
        (label "Text to title-case")
        (default "the quick brown fox")
      ))
    ))
  ))
  (children ([]
    echo_into_titlecased_llm
    echo_into_titlecased_prolog
    echo_into_titlecased_python
  ))
  (preferredChild echo_into_titlecased_llm)
)
```

The LLM child selects a concrete model, binds the abstract Prompt, and declares which named input becomes the user content and which named output receives the model response:

```metta
(
  (kind operation)
  (id echo_into_titlecased_llm)
  (implementation llm.complete)
  (modelSelection (
    (models ([] openrouter-ai21_jamba-large-1.7))
    (strategy single)
  ))
  (bindings (
    (prompts ([] titlecase_received_text))
    (separator "\n\n")
  ))
  (parameters (
    (inputBinding text)
    (outputBinding text)
  ))
  (parents ([] echo_into_titlecased))
)
```

`titlecase_received_text` is an abstract Prompt. Its `preferredChild` selects the default concrete wording while allowing model-specific alternatives:

```metta
(
  (kind prompt)
  (id titlecase_received_text)
  (inputs ((text text)))
  (outputs ((text text)))
  (children ([]
    titlecase_received_text.default
    titlecase_received_text.gpt5
    titlecase_received_text.multi_modal.claude
    titlecase_received_text.text_only.claude
  ))
  (preferredChild titlecase_received_text.default)
)

(
  (kind prompt)
  (id titlecase_received_text.default)
  (targets ([] generic-chat))
  (text ([]
    "Convert the received text to title case."
    "Preserve punctuation."
    "Return only the transformed text."
  ))
  (parents ([] titlecase_received_text))
)
```

### What happens when Run is pressed

For the example input `the quick brown fox`, the runtime:

1. Resolves `echo_into_titlecased` to the selected implementation. The Operation prefers `echo_into_titlecased_llm`, but the playground may explicitly select Python, Prolog, or LLM without changing that saved preference.
2. Inherits the Operation's `example_execute` form, so the implementation tab gets the same `text` input control even though it does not duplicate that form.
3. Resolves the model resource `openrouter-ai21_jamba-large-1.7` through its model/profile/backend inheritance chain and applies its runtime policy.
4. Resolves `titlecase_received_text` to `titlecase_received_text.default` and joins its three `text` entries using the configured separator.
5. Reads the `text` argument because `inputBinding` is `text`. The effective request is the resolved instructions followed by the user value `the quick brown fox`.
6. Calls the `llm.complete` provider and stores the returned content under `text` because `outputBinding` is `text`.
7. Produces an output such as `The Quick Brown Fox`, which the workflow exposes as `$titlecased_text`.

The prompt playground stops after prompt resolution and rendering; the operation playground continues through model selection and inference. This makes it possible to inspect prompt composition separately from the model call.

Model-selection strategies may be `single`, `parallel`, `compare`, or `fallback`. Prompt bindings are ordered, so larger operations can compose response contracts, domain instructions, examples, and output-format constraints without copying prompt text into every implementation.

This separation means the same abstract Operation can have Python, Prolog, MeTTa, LLM, HTTP, subprocess, or other implementations while preserving one stable semantic stage identity.

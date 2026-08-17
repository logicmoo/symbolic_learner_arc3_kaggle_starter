[Back to repository README](../../../../README.md)

# Source Code

Source Code contains the reusable implementation material bound to Operations. The editor presents four focused views while preserving the same filesystem-backed resources and rich hierarchy controls.

## Languages and bindings

- **Prompts** are reusable LLM instructions and ordered Prompt Profiles stored under `design/prompts/`.
- **Prolog** shows Operations whose concrete children use `prolog.source`.
- **MeTTa** shows Operations backed by executable MeTTa source.
- **Python** shows Operations bound to Python modules and callables.

An Operation defines *what* a capability does through its typed input and output contract. A same-kind child Operation defines *how* it runs and points to its implementation source. Workflows and PDDL-produced plans should reference the abstract Operation; runtime resolution selects an enabled concrete child.

Prompts do not select models. An LLM-backed Operation binds Prompt IDs or Prompt Profiles, while its model selection chooses a backend, model, or preset independently. This keeps instruction source reusable across model providers.

## Editing and testing

Open a resource in a persistent tab, edit its structured fields or raw MeTTa/JSON source, then save it to the workspace. Use the inherited runner to invoke an implementation with typed inputs. Python and Prolog runs expose standard output, standard error, request details, and response bodies in the execution trace when available.

Source Code is an implementation-oriented view of Operations and Prompts, not a duplicate catalog. Changes made here appear in the Operations or Prompts editors because they address the same resources.

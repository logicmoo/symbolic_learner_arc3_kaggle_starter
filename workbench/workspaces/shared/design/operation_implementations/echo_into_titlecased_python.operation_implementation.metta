(
  (kind operation_implementation)
  (id echo_into_titlecased_python)
  (label "Echo Into Titlecased / Python")
  (description "Take received text, call an imported Python function, and return the title-cased text.")
  (implementation python.callable)
  (inputs (
    (text Text)
  ))
  (outputs (
    (text Text)
  ))
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
  (parameters (
    (inputBinding text)
    (outputBinding text)
  ))
  (parents ([]
    echo_into_titlecased
  ))
)

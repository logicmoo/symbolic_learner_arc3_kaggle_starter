(
  (kind operation)
  (topics ([]
    collection-building
    sample-demos
  ))
  (id collection.random_list_element)
  (label "Random List Element")
  (description "Select one actual element from a non-empty list using an optional deterministic seed.")
  (inputs (
    (items Array)
    (seed Number)
  ))
  (outputs (
    (element Any)
  ))
  (implementedBy (
    (collection.random_list_element.python ())
  ))
  (inheritedBy (
    (collection.random_list_element.python (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        implements
        implementedBy
        preferredImplementation
      ))
    ))
  ))
  (preferredImplementation collection.random_list_element.python)
)
(
  (kind operation)
  (topics ([]
    collection-building
    sample-demos
    systems-python
  ))
  (id collection.random_list_element.python)
  (label "Random List Element / Python")
  (implementation python.callable)
  (inputs (
    (items Array)
    (seed Number)
  ))
  (outputs (
    (element Any)
  ))
  (python (
    (importMode file)
    (file python/collection_operations.py)
    (callable random_list_element)
  ))
  (parameters (
    (outputBinding element)
  ))
  (implements (
    (collection.random_list_element ())
  ))
  (inheritsFrom (
    (collection.random_list_element (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)

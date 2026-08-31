(
  (kind operation)
  (topics ([]
    gallery-inspection
    collection-building
  ))
  (id gallery.curate_resource)
  (label "Gallery Curation Operation")
  (description "Optional, specializable circuit-board-style inspection probe that assembles any upstream collection into a Gallery Resource for humans, AI, and downstream operations without filtering, judging utility, or learning. It is non-blocking by default; a child or workflow may require it. Its Python child is the deterministic implementation available when the task executes.")
  (inputs (
    (items Array)
  ))
  (parameters (
    (label "Gallery Resource")
    (title_field title)
    (image_field frame_path)
    (description_field description)
  ))
  (outputs (
    (gallery Object)
  ))
  (probePolicy (
    (defaultRequired false)
    (defaultBlocking false)
    (specializable true)
  ))
  (example_execute (
    (action gallery.curate_resource)
    (arguments (
      (items (
        (datatype Array)
        (label "Items to inspect")
        (default ([]))
      ))
    ))
    (parameters (
      (label (
        (datatype Text)
        (default "Gallery Resource")
      ))
      (title_field (
        (datatype Text)
        (default title)
      ))
      (image_field (
        (datatype Text)
        (default frame_path)
      ))
      (description_field (
        (datatype Text)
        (default description)
      ))
    ))
  ))
  (implementedBy (
    (gallery.curate_resource.python ())
  ))
  (inheritedBy (
    (gallery.curate_resource.python (
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
  (preferredImplementation gallery.curate_resource.python)
)
(
  (kind operation)
  (topics ([]
    gallery-inspection
    sample-demos
    systems-python
  ))
  (id gallery.curate_resource.python)
  (label "Gallery Curation Operation / Python")
  (implementation python.callable)
  (inputs (
    (items Array)
  ))
  (outputs (
    (gallery Object)
  ))
  (python (
    (importMode file)
    (file python/collection_operations.py)
    (callable curate_gallery_resource)
  ))
  (parameters (
    (outputBinding gallery)
    (label "Gallery Resource")
    (title_field title)
    (image_field frame_path)
    (description_field description)
  ))
  (implements (
    (gallery.curate_resource ())
  ))
  (inheritsFrom (
    (gallery.curate_resource (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)

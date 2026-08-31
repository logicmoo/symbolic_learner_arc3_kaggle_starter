(
  (kind operation)
  (id skill.apply_image_filter)
  (label "Apply Image Filter Skill")
  (description "Run one prepass filter skill over an image and return the filtered copy. Skills are capabilities the workbench calls directly -- no model decides anything: built-in transforms (cartoon, pixelate, downscale), .cube color LUTs, and drop-in Python skill files (data/VideoImports/filter_skills/*.py exporting SKILL metadata plus apply(image, params)). The live execution surface is POST /workbench/video-import/filter (single spec or a chain, applyTo frames|video) with previews at POST /workbench/video-import/filter-preview; the loadable registry is GET /workbench/video-import/filters.")
  (topics ([]
    image
    skills
    video-import
  ))
  (role abstract_stage)
  (inputs (
    (imagePath Text)
    (filterId Text)
    (params Json)
  ))
  (outputs (
    (filteredPath Text)
  ))
  (example_execute (
    (action operation.invoke)
    (arguments (
      (imagePath (
        (datatype Text)
        (label "Workspace-relative image to filter")
        (default data/VideoImports/previews/testcard.png)
      ))
      (filterId (
        (datatype Text)
        (label "Filter id from GET /workbench/video-import/filters")
        (default cartoon)
      ))
      (params (
        (datatype Json)
        (label "Filter parameters")
        (default (
          (__metta_json_string_parts__ ([]
            (
              (colors 8)
              (scale 8)
            )
          ))
        ))
      ))
    ))
  ))
  (implementedBy (
    (skill.image_filter.cartoon ())
    (skill.image_filter.pixelate ())
    (skill.image_filter.downscale ())
    (skill.image_filter.lut ())
    (skill.image_filter.python_skill ())
  ))
  (inheritedBy (
    (skill.image_filter.cartoon (
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
    (skill.image_filter.pixelate (
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
    (skill.image_filter.downscale (
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
    (skill.image_filter.lut (
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
    (skill.image_filter.python_skill (
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
  (preferredImplementation skill.image_filter.cartoon)
)
(
  (kind operation)
  (id skill.image_filter.cartoon)
  (label "Cartoon Filter Skill")
  (description "Flat quantized color regions with darkened edges (params: colors). Built-in PIL transform behind POST /workbench/video-import/filter with filter=cartoon.")
  (topics ([]
    image
    skills
  ))
  (implementation python.callable)
  (implements (
    (skill.apply_image_filter ())
  ))
  (inheritsFrom (
    (skill.apply_image_filter (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind operation)
  (id skill.image_filter.pixelate)
  (label "Pixelate Filter Skill")
  (description "Blocky low-res + reduced palette (params: colors, scale) so an image reduces to a small redraw program; POST /workbench/video-import/filter with filter=pixelate.")
  (topics ([]
    image
    skills
  ))
  (implementation python.callable)
  (implements (
    (skill.apply_image_filter ())
  ))
  (inheritsFrom (
    (skill.apply_image_filter (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind operation)
  (id skill.image_filter.downscale)
  (label "Downscale Filter Skill")
  (description "Generic 1/N resolution decrease, nothing else (params: scale); POST /workbench/video-import/filter with filter=downscale.")
  (topics ([]
    image
    skills
  ))
  (implementation python.callable)
  (implements (
    (skill.apply_image_filter ())
  ))
  (inheritsFrom (
    (skill.apply_image_filter (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind operation)
  (id skill.image_filter.lut)
  (label "Color LUT Filter Skill")
  (description "Color-grade through a .cube 3D LUT (trilinear interpolation). LUT files dropped into data/VideoImports/luts/ auto-register; POST /workbench/video-import/filter with filter=lut plus lutPath.")
  (topics ([]
    image
    skills
  ))
  (implementation python.callable)
  (implements (
    (skill.apply_image_filter ())
  ))
  (inheritsFrom (
    (skill.apply_image_filter (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)
(
  (kind operation)
  (id skill.image_filter.python_skill)
  (label "Python Skill File Filter")
  (description "Run a drop-in Python skill file (data/VideoImports/filter_skills/*.py exporting SKILL metadata plus apply(image, params)); examples shipped: grayscale_posterize, edge_sketch, and the downloaded MIT pilgram library wrapper (params.style). POST /workbench/video-import/filter with filter=skill plus skillPath.")
  (topics ([]
    image
    skills
  ))
  (implementation python.callable)
  (implements (
    (skill.apply_image_filter ())
  ))
  (inheritsFrom (
    (skill.apply_image_filter (
      (borrow ([]
        *
      ))
      (exclude ([]))
    ))
  ))
)

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VIDEO_IMPORT_PAGE = (
    ROOT
    / "workbench"
    / "frontend"
    / "src"
    / "components"
    / "VideoImportPage.tsx"
)
MODEL_OPTION_DISPLAY = ROOT / "workbench" / "frontend" / "src" / "components" / "modelOptionDisplay.ts"
COLORED_COMBOBOX = ROOT / "workbench" / "frontend" / "src" / "components" / "ColoredTagCombobox.tsx"
CHAT_CONVERSATION = ROOT / "workbench" / "frontend" / "src" / "components" / "ChatConversation.tsx"


def test_colored_combobox_is_shared_by_chat_and_video_models() -> None:
    combo = COLORED_COMBOBOX.read_text(encoding="utf-8")
    chat = CHAT_CONVERSATION.read_text(encoding="utf-8")
    video = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")
    display = MODEL_OPTION_DISPLAY.read_text(encoding="utf-8")

    assert "export function ColoredTagCombobox" in combo
    assert 'role="listbox"' in combo
    assert 'className="colored-combobox-tag"' in combo
    assert "disabled={description.disabled}" in combo
    assert "ColoredTagCombobox" in chat
    assert "function StreamPicker" not in chat
    assert video.count("<ColoredTagCombobox") >= 8
    assert '"imageOutput"' in display
    assert '"image output"' in display


def test_user_preview_picker_has_no_number_parameter() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")

    assert '{groupKind !== "user" && (' in source
    assert 'id === "select:user" ? {} : { n: "" }' in source
    assert 'step.entryId === "select:user" ? { ...step, params: {} } : step' in source

    user_picker = source.index('if (groupKind === "user")')
    numbered_picker = source.index(
        "const count = Math.max(1, Math.min(frames.length, Number(groupCount) || 6));"
    )
    assert user_picker < numbered_picker


def test_inherited_model_is_available_before_full_model_enumeration() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")

    fast_selection = source.index("model-selection?include_models=false")
    full_registry = source.index("/model-policy")
    assert fast_selection < full_registry
    assert "inheritedModelRef.current = inherited" in source
    assert "inheritedChoices" in source
    assert 'text: "inherited"' in source
    assert "allCallsModelTouchedRef.current = true" in source
    assert "describerModelTouchedRef.current = true" in source
    assert "plannerModelTouchedRef.current = true" in source
    assert "extractorModelTouchedRef.current = true" in source
    assert "turtleModelTouchedRef.current = true" in source
    assert 'from "./ColoredTagCombobox"' in source
    assert "modelCapabilityTags" in source
    assert "videoModelDescription" in source
    assert '"image output": "#ff8bd1"' in source
    assert '"no vision": "#e0a458"' in source
    assert "disabled: !model.enabled || !compatible" in source
    assert "preferred by ${preferenceSourceLabel(preferenceSource)}" in source
    assert "preferred:" in source
    display = MODEL_OPTION_DISPLAY.read_text(encoding="utf-8")
    for capability in ("multimodal", "vision", "audio", "reasoning", "tools", "code", "json", "text"):
        assert f'"{capability}"' in display
    assert "[${tags.join(\", \")}]" in display


def test_each_video_import_image_collection_has_a_distinct_gallery_name() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")

    for name in (
        "USER PICK GALLERY",
        "EXTRACTED FRAME GALLERY",
        "FILTER EFFECT GALLERY",
        "PROCESSED OUTPUT GALLERY",
        "PROCESSING TRAIL GALLERY",
        "SCENE OBJECT VISUALS",
    ):
        assert name in source
    assert 'aria-label="Extracted Frame Gallery"' in source
    assert 'role="listitem"' in source
    assert "Extracted Frame Gallery:" in source


def test_status_controls_have_their_own_top_row() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "video_import.css").read_text(encoding="utf-8")

    controls = source.index('className="video-import-activity-controls"')
    lower = source.index('className="video-import-activity-lower"', controls)
    logs = source.index('className="video-import-activity-lines"', lower)
    assert controls < lower < logs
    assert source[controls:logs].count('type="checkbox"') == 4
    assert "copyStateJson" in source[controls:logs]
    assert "forgetState" in source[controls:logs]
    assert "stopEverything" not in source[controls:lower]
    assert "stopEverything" in source[lower:]
    assert ".video-import-activity-controls" in styles
    assert ".video-import-activity-lower" in styles
    assert "flex-wrap: wrap" in styles
    assert "grid-template-columns: minmax(0, 1fr)" in styles


def test_center_scroller_reserves_its_scrollbar_gutter() -> None:
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "video_import.css").read_text(encoding="utf-8")

    page_rule = styles[styles.index(".video-import-page {"):styles.index("}", styles.index(".video-import-page {"))]
    assert "scrollbar-gutter: stable" in page_rule
    assert "box-sizing: border-box" in page_rule
    assert "grid-template-columns: minmax(0, 1fr)" in page_rule
    assert "padding-left: 10px" in page_rule
    assert ".video-import-page > * { min-width: 0; max-width: 100%; }" in styles


def test_model_responses_are_persistently_cached_by_prompt_and_image() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")

    assert "type CachedModelResponse" in source
    assert "modelResponseCache," in source
    assert "modelResponseCacheRef.current = restoredModelCache" in source
    assert "responseCacheHash(image)" in source
    assert "cached.modelId === modelId" in source
    assert "cached.prompt === prompt" in source
    assert "cached.imageHash === imageHash" in source
    assert "↻ cached model response" in source
    assert source.count("invokeCachedModel(") == 11


def test_member_gallery_has_two_stage_runner_with_inspectable_prompts() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "video_import.css").read_text(encoding="utf-8")

    assert "SCENE OBJECTS TEXTUAL DESCRIPTION." in source
    assert "Describe this image, then list only its direct visually separable child objects." in source
    assert "{{subjectContext}}" in source
    assert "Do not return polygons or coordinates in this stage." in source
    assert "OBJECT EXTRACTION PLANNER." in source
    assert "Planner orders direct children; it does not generate prompts." in source
    assert "OBJECT OUTLINER." in source
    assert "Outline exactly ONE object" in source
    assert "SCENE OBJECT VISUAL EXTRACTION." in source
    assert "Locate ONLY this listed thing:" in source
    assert "const describeMemberScenes = (onlyMissing = false)" in source
    assert "describeRecursiveSubject" in source
    assert "planRecursiveInventory" in source
    assert "runRecursivePlanner" in source
    assert "runRecursiveOutliner" in source
    assert "runRecursiveExtractor" in source
    assert "queue.push(child)" in source
    assert "parentInventoryId: parent.id" in source
    assert "MAX_RECURSIVE_OBJECT_DEPTH = 9" in source
    assert "(inventory.depth || 0) < MAX_RECURSIVE_OBJECT_DEPTH" in source
    assert "descriptionPrompt: inventoryPrompt" in source
    extraction_section = source.index('section("members", "SCENE OBJECT VISUALS · RECURSIVE DESCRIBER / PLANNER / OUTLINER / EXTRACTOR"')
    assert 'section("memberDescription", "SCENE OBJECTS TEXTUAL DESCRIPTION"' not in source
    assert extraction_section > 0
    assert "video-import-member-tabs" not in source
    assert 'role="tablist"' not in source
    assert 'role="tabpanel"' not in source
    assert "PROMPTS + IMAGE OUTPUTS" in source
    assert "Exact Describer prompt" in source
    assert "Exact Describer output" in source
    assert "Call LLM · Describe selected input images" in source
    assert "Call LLM · Planner" in source
    assert "Call LLM · Outliner" in source
    assert "Call LLM · Recursive Extractor" in source
    assert "Call LLM · Turtle Gen" in source
    assert "Call LLM · Turtle PNG" in source
    assert "DEFAULT_MEMBER_DESCRIPTION_PROMPT" in source
    assert "DEFAULT_MEMBER_ORDER_PROMPT" in source
    assert "DEFAULT_MEMBER_OUTLINER_PROMPT" in source
    assert "DEFAULT_RECURSIVE_EXTRACTOR_PROMPT" in source
    assert "DEFAULT_TURTLE_PROMPT" in source
    assert "DEFAULT_TURTLE_PNG_PROMPT" in source
    assert "renderTurtlePrompt" in source
    assert "renderTurtlePngPrompt" in source
    assert "turtle-render" in source
    assert "TURTLE OUTPUT" in source
    assert "PRE-TURTLE LEAVES" in source
    assert "clearPreTurtleLeaves" in source
    assert "activeTurtleArtifact.rawProgram" in source
    assert 'className="video-import-member-prompt-editor"' in source
    assert source.count('className="video-import-member-prompt-disclosure"') == 5
    assert "video-import-member-prompt-disclosure" in styles
    assert "<textarea value={memberOrderPrompt}" in source
    assert "<textarea value={memberOutlinerPrompt}" in source
    assert "<textarea value={memberExtractorPrompt}" in source
    assert "<textarea value={turtlePrompt}" in source
    assert "<textarea value={turtlePngPrompt}" in source
    assert "D · DESCRIBER" in source
    assert "Call LLM · Describe selected input images" in source
    assert '{{goal}}' in source
    assert '{{alreadyExtracted}}' in source
    assert "renderMemberDescriptionPrompt" in source
    assert "renderMemberExtractionPrompt" in source
    assert "renderMemberOrderPrompt" in source
    assert "renderMemberOutlinerPrompt" in source
    assert "Exact Describer prompt" in source
    assert "Exact Planner prompt" in source
    assert "Planner-selected next-object data" in source
    assert "traceTurtle" in source
    assert "normalized 0..1000 move/line commands" in source
    assert "renderSharedExtractorPrompt" in source
    assert "One shared reconstruction template." in source
    planner_prompt = source[source.index("const DEFAULT_MEMBER_ORDER_PROMPT"):source.index("const DEFAULT_MEMBER_OUTLINER_PROMPT")]
    assert "cutoutInstructions" not in planner_prompt
    assert '\\"order\\":[\\"exact object name\\"' in planner_prompt
    assert '\\"touching\\":[{\\"objects\\"' in planner_prompt
    assert '\\"occlusions\\":[{\\"occluder\\"' in planner_prompt
    assert '\\"containments\\":[{\\"container\\"' in planner_prompt
    assert "every contained object before its container" in planner_prompt
    assert "parsePlannerRelationships" in source
    assert "migratePlannerPrompt" in source
    assert "setMemberOrderPrompt(migratePlannerPrompt(s.memberOrderPrompt))" in source
    assert "plannerTouching: relationships.touching" in source
    assert "plannerOcclusions: relationships.occlusions" in source
    assert "plannerContainments: relationships.containments" in source
    assert "parsePlannerLabels" in source
    assert "planner-visualization" in source
    assert "PLANNER NUMBERED ORDER PREVIEW" in source
    assert "outline-verification" in source
    assert "outlineVerificationImage: thing.outlineVerificationImage" in source
    assert "VERIFIED TRACE · agreement" in source
    assert "video-import-verification-gallery" in styles
    assert "Touching: none declared." in source
    assert "Occlusions: none declared." in source
    assert "Containments: none declared." in source
    outliner_prompt = source[source.index("const DEFAULT_MEMBER_OUTLINER_PROMPT"):source.index("const DEFAULT_RECURSIVE_EXTRACTOR_PROMPT")]
    assert "polygons" in outliner_prompt
    assert "holes" in outliner_prompt
    assert "{{plannerRelationships}}" in outliner_prompt
    assert "containedBy:" in source
    assert "one object per call" in source.lower()
    assert "const scenePath = inventory.sourceImage" in source
    assert "outlineRecursiveThing" in source
    assert "hasAlignedOutline" in source
    assert "outlineSourceImage: thing.outlineImage" in source
    assert "outlineSourceDimensions: thing.outlineDimensions" in source
    assert "PIXEL COORDINATE SPACE:" in source
    assert "runConcurrent(orderedCandidates, outlinerConcurrency" in source
    assert "polygons: thing.outlinePolygons || []" in source
    assert "Outliner owns geometry; Extractor owns cutting and background reconstruction." in source
    assert "{{nextObjectName}}" in source
    assert "{{plannerPosition}}" in source
    assert "<pre>{attempt.prompt}</pre>" not in source
    assert "const objectPlans =" not in source
    assert "DESCRIBER INPUT IMAGE" in source
    assert "EXACT ROUTE INPUT IMAGE" in source
    assert 'open={attempt.status === "extracted"}' not in source
    assert "Planned extraction order:" in source
    assert "↓ Planner output" in source
    assert "revealRecursiveOutput" in source
    assert "(described && inventory.things.length === 0)" in source
    assert ".sort((left, right) => left.frameIndex - right.frameIndex" in source
    assert "orderedMemberInventories" in source
    assert "retrying after error" in source
    assert "waiting for Describer" in source
    assert "video-import-planner-jump-status" in source
    assert 'id={`recursive-output-${responseCacheHash(inventory.id)}`}' in source
    assert 'setCollapsedMap((current) => ({ ...current, [sectionId]: false }))' in source
    assert 'scrollIntoView({ behavior: "smooth", block: "start" })' in source
    assert "normalizeMemberPromptLabels" in source
    assert "OUTPUT IMAGE(S)" in source
    assert "video-import-member-call-images" in source
    assert 'type="checkbox" checked={probed}' in source
    assert "check at least one Processing Trail probe first" not in source
    assert "checkedProbes.has(inventory.probeIndex)" not in source
    assert "const scenePath = frame.path" in source
    assert "sourceImage: scenePath" in source
    assert "inputImage: inputPath" in source
    assert "/player/asset?path=" not in source
    assert "/asset?path=${encodeURIComponent(path)}" in source
    assert "Could not load checked probe image:" not in source
    assert "include_disabled_models=true" in source
    assert "no enabled vision models" in source
    assert "isRunnableVisionModel" in source
    assert "model.capabilities?.vision === true" in source
    assert "formatDetectedJson" in source
    assert "```(?:json)?" in source
    assert "Describer output · JSON formatted" in source
    assert "No enabled vision-capable model" in source
    assert "Enable their backend in Models" in source
    assert "automaticVideoModelId" in source
    assert "opus[\\s/_-]*4[._-]?8" in source
    assert "if (opus48) return opus48.id" in source
    assert "turtleLeafCandidates" in source
    assert "nextPassImage" in source
    assert "activeImageMember.nextPassImage || activeImageMember.cutout" in source
    runner = source.index('className="video-import-member-runner"')
    strips = source.index('className="video-import-extracted-object-strips"')
    assert runner < strips
    assert "VERTICAL STRIPS OF EXTRACTED OBJECTS" in source
    assert "memberInputPaths" in source
    assert "frames.filter((frame) => memberInputPaths.has(frame.path))" in source
    assert "multi-select at least one Extracted Frame Gallery image as an LLM input" in source
    assert 'className="video-import-member-input-check"' in source
    assert "Only checked images enter the recursive Describer" in source
    assert 'checked={memberInputPaths.has(frame.path)} disabled={busy}' not in source
    assert "disabled={busy || memberInputPaths.size === frames.length}" not in source
    assert "Select all" in source
    assert "Select none" in source
    assert "clearExtractedFrames" in source
    assert "× Clear extracted frames" in source
    assert "clearRecursiveLevel" in source
    assert "clearSelectedImages" in source
    assert "onClear={clearSelectedImages}" in source
    assert "affectedInventoryIds" in source
    assert "modelResponseCacheRef.current = remainingCache" in source
    assert "compactCachedModelPayload" in source
    assert "compactModelResponseCache" in source
    assert "delete imageProvenanceCacheRef.current[path]" in source
    assert "setPinnedImageContext" in source
    assert "their recursive metadata" in source
    assert "watchConcurrentJob" in source
    assert "sceneJob?.state === \"running\"" in source
    assert "frameExtractionJob?.state === \"running\"" in source
    assert 'watchConcurrentJob(String(payload.jobId), "scenes"' in source
    assert 'watchConcurrentJob(String(payload.jobId), "extract"' in source
    assert '<button disabled={!selectedPath || sceneJob?.state === "running" || job?.state === "running"}' in source
    assert "clearSceneDetection" in source
    assert "scene detection cleared; next scan starts from the beginning" in source
    assert '<button disabled={!markers.length && sceneJob?.state !== "running"} onClick={clearSceneDetection}>× Clear scenes</button>' in source
    assert '<button disabled={frameExtractionJob?.state === "running" || job?.state === "running" || (mode === "scenes" && !markers.length)}' in source
    assert "captionJob?.state === \"running\"" in source
    assert 'watchConcurrentJob(String(payload.jobId), "captions"' in source
    assert "CC Generate captions" in source
    assert "× Clear captions" in source
    assert "video-import-active-caption" in source
    assert "MEDIA JOB QUEUE" in source
    assert "effectiveCaptionModel" in source
    assert "clearTurtleTerminations" in source
    assert "onClear={clearTurtleTerminations}" in source
    assert "onClear={clearPreTurtleLeaves}" in source
    assert 'useState<"interval" | "scenes">("scenes")' in source
    assert 'const [startScene, setStartScene] = useState("2")' in source
    assert 'const [skipScenes, setSkipScenes] = useState("1")' in source
    assert "startScene: Math.max(1, Number(startScene) || 1)" in source
    assert "endScene: endScene.trim() ? Number(endScene) : undefined" in source
    assert "skipScenes: Math.max(0, Number(skipScenes) || 0)" in source
    assert ">start scene <" in source
    assert ">end scene <" in source
    assert "scene(s)</label>" in source
    assert "frame.sceneIndex" in source
    assert "provenance?: string" in source
    assert "setStartScene(s.startScene)" in source
    assert "setSkipScenes(s.skipScenes)" in source
    assert "video-import-workflow-galleries" in source
    assert "WorkflowGalleryPanel" in source
    assert "WorkflowGalleryItem" in source
    assert 'role={onSelectedChange ? "checkbox" : undefined}' in source
    assert "const toggle = () => onSelectedChange?.(!selected)" in source
    assert 'onClick={(event) => event.stopPropagation()}' in source
    assert "showCheckbox = false" in source
    assert "if (event.ctrlKey) toggle()" in source
    assert "if (!target || event.ctrlKey" in source
    assert "Click for popup · Ctrl-click to select or unselect" in source
    assert "pinnedImageContext" in source
    assert "handleImageContextClick" in source
    assert "video-import-image-hover-context${pinnedImageContext ? \" is-pinned\" : \"\"}" in source
    assert "× Close" in source
    assert ".video-import-image-hover-context.is-pinned" in styles
    assert "pointer-events: auto; resize: both" in styles
    assert "max-width: calc(50vw - 16px)" in styles
    assert "max-height: calc(50vh - 16px)" in styles
    assert "collapsedLeftGalleries" in source
    assert "selectedWorkflowGalleryPaths" in source
    assert "previousInventory = memberInventories.find" in source
    assert "previousThings = new Map" in source
    assert "existingChild = memberInventories.find" in source
    assert "queuedInventoryIds" in source
    assert 'title={`EXTRACTED IMAGES · ${frames.length}`}' in source
    assert 'title={`SELECTED IMAGES · ${memberInputPaths.size}`}' in source
    assert "selectedImageStageIndicators" in source
    assert "stageIndicators={selectedImageStageIndicators(frame)}" in source
    assert 'label: "T", value: `${generatedTurtles}/${rootLeaves.length}`' in source
    assert 'label: "I", value: `${renderedImages}/${rootLeaves.length}`' in source
    assert "grid-template-columns: repeat(6, 1fr)" in styles
    assert "video-import-gallery-stage-strip" in source
    assert ".video-import-gallery-stage-strip span.is-active" in styles
    assert ".video-import-gallery-stage-strip span.is-retrying" in styles
    assert ".video-import-gallery-stage-strip span.is-partial" in styles
    assert ".video-import-gallery-stage-strip span.is-complete" in styles
    assert "LEFTOVER BACKGROUNDS" in source
    assert "video-import-workflow-gallery-panel" in source
    assert "outlinePolygons: polygons" in source
    assert "outlineHoles: holes" in source
    assert "outlineBox: box" in source
    assert "pixel-edge precision" in source
    assert "fillInstructions" in source
    assert "remove: content-aware inpaint" in source
    assert "parsed.backgroundFill" in source
    assert "imageGenerationModelId: effectiveImageOutputModel" in source
    assert "automaticImageOutputModelId" in source
    assert "masked image editing via ${effectiveImageOutputModel}" in source
    assert "no enabled model advertises image output" in source
    assert "DEFAULT_RECURSIVE_AUTOMATION" in source
    automation_defaults = source[source.index("const DEFAULT_RECURSIVE_AUTOMATION"):source.index("const DEFAULT_MEMBER_DESCRIPTION_PROMPT")]
    assert "describer: true" in automation_defaults
    assert "planner: true" in automation_defaults
    assert "outliner: true" in automation_defaults
    assert "extractor: true" in automation_defaults
    assert "turtle: true" in automation_defaults
    assert "turtlePng: true" in automation_defaults
    assert "advanceLevels: true" in automation_defaults
    assert "enlargeSubobjects: true" in automation_defaults
    assert "setRecursiveAutomation({" in source
    assert "s.recursiveAutomation.describer === true" in source
    assert "recursiveAutomation.describer" in source
    assert "recursiveAutomation.planner" in source
    assert "recursiveAutomation.outliner" in source
    assert "recursiveAutomation.extractor" in source
    assert "recursiveAutomation.turtle" in source
    assert "recursiveAutomation.turtlePng" in source
    assert "recursiveAutomation.advanceLevels" in source
    assert "recursiveAutomation.enlargeSubobjects" in source
    assert "enlargeForNextPass: recursiveAutomation.enlargeSubobjects" in source
    assert "visibleAltImageZoom.imagePath" in source
    assert "maximumImageWidth" in source
    assert "maximumImageHeight" in source
    assert "const width = maximumImageWidth" in source
    assert "const height = maximumImageHeight" in source
    assert "window.innerWidth - width - contextWidth" in source
    assert "visibleAltImageZoom.scale.toFixed(1)" in source
    assert "pinnedAltImageZoom" in source
    assert "visibleAltImageZoom" in source
    assert "event.altKey && altImageZoom" in source
    assert "video-import-alt-image-zoom${pinnedAltImageZoom ? \" is-pinned\" : \"\"}" in source
    assert ".video-import-alt-image-zoom.is-pinned" in styles
    assert "position: sticky; z-index: 3; top: -10px" in styles
    assert "position: sticky; z-index: 3; top: -8px" in styles
    assert "transform: translate(-50%, -50%)" not in styles
    assert "activeImageParentThing?.description ||" in source
    assert "activeImageInventory?.sceneDescription ||" in source
    assert "activeImageInventory?.descriptionOutput ||" in source
    assert "activeImageInventory?.orderOutput ||" in source
    assert "activeImagePlannerStatus" in source
    assert "PLANNER · {activeImagePlannerStatus}" in source
    assert "formatDetectedJson(activeImagePlannerOutput)" in source
    assert "activeImageOutlinerOutputs" in source
    assert "OUTLINER · {activeImageOutlinerOutputs.length} OBJECT(S)" in source
    assert "imageProvenanceCacheRef" in source
    assert "activeImageProvenance" in source
    assert "image-provenance?workspaceId=" in source
    assert "JSON.stringify(activeImageProvenance, null, 2)" in source
    assert "formatDetectedJson(activeImageDescriberOutput" in source
    assert "formatDetectedJson(activeTurtleArtifact.pngProgram)" in source
    assert "OBJECTS · {activeImageInventory?.things.length || 0}" in source
    assert "No object list has been made for this image yet." in source
    assert "PARENT OBJECT DESCRIPTION" in source
    assert "LAST IMAGE DESCRIBER OUTPUT" in source
    assert "video-import-image-hover-context" in source
    assert "ALL LLM CALLS" in source
    assert "slots stay available for other stages in either direction." in source
    assert "ACTIVE WORKER" in source
    assert "video-import-llm-call-metrics" in source
    assert "PENDING" in source
    assert "COMPLETED" in source
    assert "AVG / JOB" in source
    assert "performance.now() - startedAt" in source
    assert "llmCallMetrics" in source
    assert "llmStageProgress" in source
    assert "ready, but still waiting for a worker" in source
    assert ".video-import-llm-call-metrics" in styles
    assert '" has-workers"' in source
    assert ".video-import-llm-call-row > button.has-workers" in styles
    assert "thing.status === \"outlining\"" in source
    assert "thing.status === \"extracting\"" in source
    assert "manualWorkerHold" in source
    assert "workersHeld = manualWorkerHold || restartPendingSignal" in source
    assert "if (!restoredRef.current || workersHeld) return;" in source
    assert 'aria-pressed={workersHeld}' in source
    assert "■ HOLD / DRAIN WORKERS" in source
    assert "▶ WORKERS HELD / DRAINING" in source
    assert "before restarting an LLM server" in source
    assert ".video-import-worker-hold.is-held" in styles
    assert "noneLabel={`<use global" in source
    assert "reserve cross-stage capacity" in source
    assert "Math.ceil(totalLlmConcurrency / 3)" not in source
    assert "queuedDescriptionTasks" in source
    assert "orderedDescriptionTasks.slice(0, descriptionConcurrency)" not in source
    assert "automaticDescriptionClaimsRef" in source
    assert "allowsOverlappingRefill" in source
    assert "total max processes" in source
    assert "DEFAULT_LLM_CALL_CONCURRENCY" in source
    assert "effectiveCallConcurrency" in source
    assert ".slice(0, 6)" not in source
    assert "descriptionTasks" in source
    assert "LLM_RETRY_DELAY_MS = 1000" in source
    assert "scheduleRetry" in source
    assert "retryReady" in source
    assert "bypassCache = false" in source
    assert "!bypassCache && cached" in source
    assert "failedStage: \"gen\"" in source
    assert "failedStage: \"png\"" in source
    assert "llmSchedulerRef" in source
    assert "acquireLlmSlot" in source
    assert "scheduler.waiters.findIndex" not in source
    assert "bestUtilization" in source
    assert "downstreamWaiting" not in source
    assert "reserve cross-stage capacity" in source
    assert "LLM_STAGE_RESERVE_FRACTION = 0.30" in source
    assert "LLM_STAGE_RESERVE_MIN = 5" in source
    assert "LLM_STAGE_ORDER" in source
    assert "bestRoundRobinDistance" in source
    assert "scheduler.lastGrantedIndex" in source
    assert "cooperativeRetryOrder" in source
    assert "retryReserve = Math.min(2" in source
    assert "automaticStagesRunningRef" in source
    assert "setAutomaticSchedulerTick((tick) => tick + 1)" in source
    scheduler_dependencies = source[source.index("  }, [", source.index("const automaticStagesRunningRef")):source.index("  ]);", source.index("const automaticStagesRunningRef"))]
    assert "models," in scheduler_dependencies
    assert "restartPendingSignal" in source
    assert "Restart pending; new LLM work is paused." in source
    assert "queued LLM work was paused before launch" in source
    assert "RESTART PENDING · DRAINING" in source
    assert 'launch("describer"' in source
    assert 'launch("planner"' in source
    assert 'launch("outliner"' in source
    assert 'launch("extractor"' in source
    assert 'launch("turtle"' in source
    assert 'launch("turtlePng"' in source
    assert "Array.from({ length: 50 }" in source
    assert "selectedDescriptionPrompt" in source
    assert "selectedPlannerPrompt" in source
    assert "selectedOutlinerPrompt" in source
    assert "selectedExtractorPrompt" in source
    assert "selectedTurtlePrompt" in source
    assert "selectedTurtlePngPrompt" in source
    assert "T · TURTLE GEN" in source
    assert "O · OUTLINER" in source
    assert "PNG · TURTLE PNG" in source
    assert "video-import-controller-prompt" in source
    assert "Fully exposed from the controller prompt selector." in source
    assert "↻ Reload prompt" in source
    assert "💾 Save prompt" in source
    assert "reloadExpandedPrompt" in source
    assert "saveExpandedPrompt" in source
    assert "no saved Video Import state is available" in source
    assert "usePageProcessActivity" in source
    assert "onOpen={() => setExpandedCallPrompt(type)}" in source
    assert "min-height: 320px" in styles
    assert "isolation: isolate; overflow: visible" in styles
    assert "flex: 0 1 min(720px, calc(50vw - 16px))" in styles
    automation = source.index('className="video-import-recursive-automation"')
    split = source.index('aria-label="Video Import pipeline forks"')
    assert 'section("memberDescription", "SCENE OBJECTS TEXTUAL DESCRIPTION"' not in source
    assert automation < split
    assert source.index('section("config", "JSON CONFIG"') > source.index('section("finish", "TURTLE / IMPORT GAME"')
    assert "grid-column: 1 / -1; grid-row: 1" in styles


def test_scene_object_flow_is_recursive_describer_planner_outliner_extractor_tree() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "video_import.css").read_text(encoding="utf-8")

    assert 'aria-label="Video Import pipeline forks"' in source
    assert 'aria-label="Recursive object workflow tree"' in source
    assert "RECURSIVE OBJECT FLOW" in source
    assert "Describer → Planner → Outliner → Extractor" in source
    assert "Every extracted object becomes the input to another cycle." in source
    assert "RecursiveInventoryTreeNode" in source
    assert "recursiveRootInventories.map" in source
    assert "candidate.parentInventoryId === inventory.id" in source
    assert "video-import-recursive-tree-node" in source
    assert "video-import-recursive-tree-leaf" in source
    assert "TURTLE" in source
    assert 'className="video-import-pipe-bushy-wires"' not in source
    assert '{selected && (\n        <section className="video-import-pipe-board"' not in source
    assert 'className="video-import-scene-object-workspace"' in source
    assert 'className="video-import-pipe-column"' in source
    assert "frame extraction stopped: no completed scene list yet; scene detection continues to the end" in source
    assert "stopped: frame extraction is starved while scene detection continues to the end" in source
    assert "scene threshold" in source
    assert "samples/s" in source
    assert "min gap" in source
    assert 'placeholder="until end"' in source
    assert "■ Stop scene scan" in source
    assert "scene scan stop requested; detected markers will be preserved" in source
    assert "■ Stop frame extraction" in source
    assert "frame extraction stop requested; completed frames will be preserved" in source
    assert "ARC playbacks…" in source
    assert "move-list provenance" in source
    assert "Publish (WHIP)" in source
    assert "Watch (HLS)" in source
    assert "Consume stream + detect scenes" in source
    assert "Paste HLS, RTSP, RTMP, SRT, or HTTP video/podcast stream URL" in source
    assert "YouTube / HLS / RTSP / RTMP / SRT / video URL or local movie path" in source
    assert "Consume URL + detect scenes" in source
    assert "⇪ Upload movie / image ZIP…" in source
    assert 'accept="video/*,.zip,application/zip"' in source
    assert '"image-archive/upload"' in source
    assert "Extracted Images source" in source
    assert "frameSources.filter" in source
    assert "Current video above" in source
    assert "Curated data ·" in source
    assert "curated-image-sources/import" in source
    assert "ARC3 PLAYER / RECORDING SOURCE" in source
    assert "<EmbeddedArc3PlayPage" in source
    assert "onRecordingChanged={refreshArcRecordings}" in source
    assert source.index('className="video-import-pipe-board"') < source.index('section("members", "SCENE OBJECT VISUALS · RECURSIVE DESCRIBER / PLANNER / OUTLINER / EXTRACTOR"')
    assert ".video-import-scene-object-workspace" in styles
    assert "grid-column: 1; grid-row: 2 / 5" in styles
    assert ".video-import-pipe-column > header::after" in styles
    assert "display: grid; grid-template-rows: auto auto" in styles
    assert "position: sticky; top: 8px" in styles
    assert ".video-import-recursive-tree" in styles
    assert ".video-import-recursive-tree-node::before" in styles
    assert ".video-import-recursive-tree-node > button.is-selected > i" in styles
    assert ".video-import-recursive-tree-leaf" in styles
    assert "border-radius: 50%" in styles
    board_start = styles.index("\n.video-import-pipe-board {")
    board_rule = styles[board_start:styles.index("}", board_start)]
    assert "overflow: visible" in board_rule


def test_alt_hover_gives_image_and_context_separate_half_page_panes() -> None:
    source = VIDEO_IMPORT_PAGE.read_text(encoding="utf-8")
    styles = (ROOT / "workbench" / "frontend" / "src" / "styles" / "video_import.css").read_text(encoding="utf-8")

    assert "type AltImageZoom" in source
    assert "hoveredImageRef" in source
    assert "showAltImageZoom" in source
    assert "event.altKey" in source
    assert 'event.key === "Alt"' in source
    assert "const width = maximumImageWidth" in source
    assert "const height = maximumImageHeight" in source
    assert "maximumImageWidth / rect.width" in source
    assert "maximumImageHeight / rect.height" in source
    assert 'window.addEventListener("keydown", keyDown)' in source
    assert 'window.addEventListener("keyup", hide)' in source
    assert 'window.addEventListener("blur", blur)' in source
    assert "onPointerMove={handleImageZoomPointer}" in source
    assert 'video-import-alt-image-zoom${pinnedAltImageZoom ? " is-pinned" : ""}' in source
    assert "visibleAltImageZoom.scale.toFixed(1)" in source
    assert ".video-import-alt-image-zoom" in styles
    assert "position: fixed" in styles
    assert "pointer-events: none" in styles
    assert ".video-import-pipe-parent-choice" in styles
    assert ".video-import-pipe-cycle" in styles
    assert "enabled: previous?.enabled === true || model.enabled" in source
    assert "vision: previous?.vision === true || model.vision" in source

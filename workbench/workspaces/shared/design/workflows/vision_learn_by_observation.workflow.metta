(
  (kind workflow)
  (id vision_learn_by_observation)
  (label "Learn a Visual World by Observation")
  (description "Bind a visual world, capture before and after states, observe an action, explain the transition, and decide whether to continue.")
  (inputs (
    (world Object)
    (observation Object)
    (result_observation Object)
  ))
  (outputs (
    (transition $transition_record)
    (decision $continue_decision)
  ))
  (steps ([]
    (
      (id select_world)
      (label "Select world")
      (kind operation)
      (implementation core.echo)
      (inputs (
        (value $world)
      ))
      (outputs (
        (value selected_world)
      ))
    )
    (
      (id capture_initial_state)
      (label "Capture initial state")
      (kind operation)
      (implementation core.echo)
      (dependsOn ([]
        select_world
      ))
      (inputs (
        (value $observation)
      ))
      (outputs (
        (value initial_observation)
      ))
    )
    (
      (id objectify_observation)
      (label "Objectify observation")
      (kind operation)
      (implementation core.echo)
      (dependsOn ([]
        capture_initial_state
      ))
      (inputs (
        (value $initial_observation)
      ))
      (outputs (
        (value objectified_before)
      ))
    )
    (
      (id observe_action)
      (label "Observe action")
      (kind human)
      (dependsOn ([]
        objectify_observation
      ))
      (form (
        (action (
          (type Object)
        ))
      ))
      (outputs (
        (action observed_action)
      ))
    )
    (
      (id capture_result)
      (label "Capture result")
      (kind operation)
      (implementation core.echo)
      (dependsOn ([]
        observe_action
      ))
      (inputs (
        (value $result_observation)
      ))
      (outputs (
        (value objectified_after)
      ))
    )
    (
      (id explain_transition)
      (label "Explain transition")
      (kind operation)
      (implementation core.merge)
      (dependsOn ([]
        objectify_observation
        capture_result
      ))
      (inputs (
        (left $objectified_before)
        (right $objectified_after)
      ))
      (outputs (
        (value transition_record)
      ))
    )
    (
      (id repeat_or_conclude)
      (label "Repeat or conclude")
      (kind human)
      (dependsOn ([]
        explain_transition
      ))
      (form (
        (continue (
          (type Boolean)
        ))
      ))
      (outputs (
        (continue continue_decision)
      ))
    )
  ))
)

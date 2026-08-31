(
  (kind managed_service)
  (id clawrouter)
  (label ClawRouter)
  (description "Keyless local model-routing gateway.")
  (port 3456)
  (healthPath /health)
  (launcher workbench/scripts/run_clawrouter.bat)
  (workingDirectory workbench)
  (commandPatterns ([]
    clawrouter
  ))
  (controllable true)
  (allowKill true)
  (allowRelaunch true)
  (singleton true)
  (defaultStartup (
    (start true)
    (hiddenWindow false)
  ))
  (dependedOnBy (
    (clawrouter-free-router ())
  ))
  (implementedBy (
    (clawrouter-free-router ())
  ))
  (inheritedBy (
    (clawrouter-free-router (
      (lend ([]
        *
      ))
      (withhold ([]
        id
        label
        description
        enabled
        implements
        implementedBy
        preferredImplementation
        inheritsFrom
        inheritedBy
        dependsOn
        dependedOnBy
      ))
    ))
  ))
)

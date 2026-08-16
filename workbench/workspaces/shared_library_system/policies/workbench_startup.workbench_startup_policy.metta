(
  (kind workbench_startup_policy)
  (id workbench_startup)
  (label "Managed Process Startup Policy")
  (services (
    (workbench-api ((start true) (hiddenWindow false) (hideFromProcessViewer false)))
    (workbench-web ((start true) (hiddenWindow false) (hideFromProcessViewer false)))
    (channel-relay ((start true) (hiddenWindow false) (hideFromProcessViewer false)))
    (clawrouter ((start true) (hiddenWindow false) (hideFromProcessViewer false)))
    (omniroute ((start true) (hiddenWindow false) (hideFromProcessViewer false)))
    (freerouter ((start true) (hiddenWindow false) (hideFromProcessViewer false)))
  ))
)
